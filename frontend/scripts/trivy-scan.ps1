# Trivy security scan — frontend (npm, Dockerfile, optional image).
# Usage: .\frontend\scripts\trivy-scan.ps1 [-Image]  (from repo root)

param(
    [switch]$Image
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$FrontendRoot = Join-Path $RepoRoot "frontend"
$TrivyConfig = Join-Path $FrontendRoot "config\trivy\trivy.yaml"
$ComposeFile = Join-Path $FrontendRoot "deploy\docker-compose.yml"

Push-Location $FrontendRoot
try {
    if (-not (Get-Command trivy -ErrorAction SilentlyContinue)) {
        Write-Error "Trivy not found. Install: https://trivy.dev/docs/latest/getting-started/installation/"
    }

    Write-Host "==> Filesystem (frontend)" -ForegroundColor Cyan
    & trivy fs --config $TrivyConfig .

    Write-Host "`n==> Docker / compose (misconfig)" -ForegroundColor Cyan
    & trivy config --severity CRITICAL,HIGH,MEDIUM deploy/Dockerfile $ComposeFile

    if ($Image) {
        if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
            Write-Error "Docker required for -Image. Start Docker Desktop and retry."
        }
        docker compose -f $ComposeFile build web
        & trivy image --severity CRITICAL,HIGH nanoka-web:latest
    }
}
finally {
    Pop-Location
}
