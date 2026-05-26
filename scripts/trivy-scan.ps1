# Analyse de sécurité Trivy (dépendances, secrets, Dockerfiles).
# Usage : .\scripts\trivy-scan.ps1 [-Image]

param(
    [switch]$Image
)

$ErrorActionPreference = "Stop"
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSNativeCommandUseErrorActionPreference = $false
}
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

function Find-TrivyExecutable {
    $cmd = Get-Command trivy -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    # Terminal ouvert avant winget : recharger le PATH système
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($machine -or $user) {
        $env:Path = @($machine, $user) -join ";"
    }

    $cmd = Get-Command trivy -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

  $wingetRoot = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
    if (Test-Path $wingetRoot) {
        $found = Get-ChildItem -Path $wingetRoot -Filter "trivy.exe" -Recurse -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($found) { return $found.FullName }
    }

    return $null
}

$Trivy = Find-TrivyExecutable
if (-not $Trivy) {
    Write-Error @"
Trivy introuvable.

1. Installez-le : winget install AquaSecurity.Trivy
2. Fermez puis rouvrez le terminal  (PATH mis à jour par winget)
3. Relancez : .\scripts\trivy-scan.ps1

Ou lancez directement (remplacez le chemin si besoin) :
  & "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\AquaSecurity.Trivy_Microsoft.Winget.Source_8wekyb3d8bbwe\trivy.exe" fs --config .trivy.yaml .
"@
}

Write-Host "Trivy : $Trivy" -ForegroundColor DarkGray

Write-Host "==> Dépendances Python (requirements)" -ForegroundColor Cyan
& $Trivy fs --config .trivy.yaml --scanners vuln --severity CRITICAL,HIGH,MEDIUM .

Write-Host "`n==> Code + secrets + misconfig" -ForegroundColor Cyan
& $Trivy fs --config .trivy.yaml --scanners secret,misconfig --severity CRITICAL,HIGH,MEDIUM .

Write-Host "`n==> Docker / compose (misconfig)" -ForegroundColor Cyan
& $Trivy config --severity CRITICAL,HIGH,MEDIUM deploy/Dockerfile.pipeline deploy/Dockerfile.scraper docker-compose.yml

if ($Image) {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker requis pour -Image. Démarrez Docker Desktop puis relancez."
    }
    Write-Host "`n==> Build + scan image pipeline" -ForegroundColor Cyan
    docker compose build pipeline
    & $Trivy image --severity CRITICAL,HIGH,MEDIUM nanoka-pipeline:latest

    Write-Host "`n==> Build + scan image scraper" -ForegroundColor Cyan
    docker compose build scrape
    & $Trivy image --severity CRITICAL,HIGH,MEDIUM nanoka-scraper:latest
}

Write-Host "Terminé." -ForegroundColor Green
