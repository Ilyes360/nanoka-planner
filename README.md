# Nanoka scraper (Genshin Impact)

Scrape et post-traitement des données personnages / armes / objets depuis [gi.nanoka.cc](https://gi.nanoka.cc/), avec interface web de planification.

## Première installation (clone vierge)

> ⚠️ **Les données ne sont pas versionnées.** Le dépôt ne contient pas les JSON ni les images (`backend/data/` est ignoré par git, seuls les `.gitkeep` sont présents). Après un `git clone`, les dossiers `data/` sont **vides** : l'API répondrait, mais sans aucun personnage ni arme à afficher.
>
> Sur une nouvelle machine, il faut donc **générer les données une première fois** avant de lancer l'interface.

Le plus simple est la voie Docker (Chromium pour le scrape est embarqué dans l'image, rien à installer) :

```powershell
git clone https://github.com/Ilyes360/python-project.git
cd python-project

# 1. Générer l'intégralité des données : scrape -> assign -> rapports
#    (Docker Desktop doit être démarré ; opération longue : tout le catalogue est scrapé)
npm run docker:full

# 2. Lancer la stack API + UI
npm run docker:stack:up        # UI http://localhost:8080
```

`npm run docker:full` enchaîne le scrape complet (personnages, armes, objets **et** images) puis le post-traitement (`assign` + rapports). Les données sont écrites dans `backend/data/` sur l'hôte et réutilisées à chaque lancement suivant — l'étape 1 n'est donc à refaire que pour rafraîchir le catalogue.

Sans Docker (installation locale), voir [Installation (backend)](#installation-backend) puis générer les données avec `npm run scrape` et `npm run assign` (venv activé). Le scrape local nécessite **Chromium + chromedriver** sur la machine.

Une fois les données présentes, utilise le [Démarrage rapide](#démarrage-rapide) pour les lancements suivants.

## Démarrage rapide

Deux façons de lancer le projet (les données doivent déjà avoir été générées — voir [Première installation](#première-installation-clone-vierge) pour un clone vierge).

### Option A — Développement local (recommandé)

Prérequis : dépendances installées une fois (voir [Installation](#installation-backend)).

1. **Active le venv** dans le terminal (étape indispensable, sinon `No module named uvicorn`) :

```powershell
cd backend
.\.venv\Scripts\Activate.ps1   # l'invite doit afficher (.venv)
cd ..
```

2. Lance l'API et l'UI dans **deux terminaux** (venv activé dans celui de l'API) :

```powershell
npm run dev:api    # API http://127.0.0.1:8000
npm run dev:web    # UI  http://localhost:5173
```

> Les scripts npm exécutent `python ...` : ils utilisent le Python du terminal. Sans venv activé, c'est le Python global (sans `uvicorn`) qui est appelé.

### Option B — Docker (comme en production)

Prérequis : **Docker Desktop démarré** (sinon `failed to connect to the docker API`).

```powershell
npm run docker:stack:up     # API :8000 (healthy) puis UI :8080
npm run docker:stack:down   # pour arrêter
```

UI sur http://localhost:8080. Pas besoin de venv ni de Python local dans ce mode.

## Structure

```
python-project/
├── backend/
│   ├── nanoka/               # Package Python (scrape, rapports, API)
│   ├── requirements/         # Dépendances pip
│   ├── config/trivy/         # Scan sécurité
│   ├── data/                 # raw, processed, images
│   ├── tests/
│   ├── scripts/
│   └── deploy/               # Dockerfiles + docker-compose.yml
├── deploy/
│   └── docker-compose.stack.yml   # Stack runtime API → web
└── frontend/                 # Interface web JavaScript (Vite)
    ├── src/
    ├── deploy/               # Dockerfile + docker-compose.yml (nginx)
    ├── config/trivy/         # Scan sécurité frontend
    └── scripts/              # trivy-scan.ps1
```

## Installation (backend)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements/requirements-dev.txt
```

Le venv vit dans `backend/.venv`. **Active-le à chaque nouveau terminal** avant de lancer les scripts npm Python (`dev:api`, `assign`, `scrape`, `pytest`, ...) :

```powershell
cd backend
.\.venv\Scripts\Activate.ps1   # (.venv) apparaît dans l'invite
```

Si PowerShell bloque le script (« execution of scripts is disabled »), autorise-le pour la session :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Ne déplacez pas le dossier `.venv` après création (sinon `pip` pointe vers un Python introuvable). En cas d’erreur « fichier spécifié introuvable », supprimez `.venv` et recréez-le avec les commandes ci-dessus.

Depuis la racine du repo, les scripts npm raccourcissent les commandes (`npm run assign`, `npm run dev:api`, etc.).

## Tests

```powershell
cd backend
pytest
pytest --cov=nanoka --cov-report=term-missing
```

Ou : `npm test` depuis la racine (backend). Frontend : `npm run test:web`.

## Tests frontend

```powershell
cd frontend
npm install
npm test
npm run test:cov
```

Ou depuis la racine : `npm run test:web`.

## Utilisation (CLI)

```powershell
cd backend
python -m nanoka.scrape
python -m nanoka.assign
python -m nanoka.ascension_report --print
python -m nanoka.weapon_report --weapon Aquila
python -m nanoka.talent_report --character Aino
```

## Interface web

Voir [Démarrage rapide › Option A](#option-a--développement-local-recommandé). Prérequis : loadouts dans `backend/data/processed/` (générés par `npm run assign`, venv activé).

Installation initiale des dépendances :

```powershell
cd backend && .\.venv\Scripts\Activate.ps1 && pip install -r requirements/requirements-dev.txt && cd ..
cd frontend && npm install && cd ..
```

## Docker

Prérequis : **Docker Desktop lancé**. Si le démon n'est pas démarré, les commandes échouent avec `failed to connect to the docker API ... dockerDesktopLinuxEngine`.

Ordre recommandé :

1. **Pipeline données** (scrape → assign → rapports)  
2. **Runtime** (API healthy → UI)

### 1. Pipeline données

```powershell
docker compose -f backend/deploy/docker-compose.yml build
docker compose -f backend/deploy/docker-compose.yml run --rm scrape
docker compose -f backend/deploy/docker-compose.yml run --rm pipeline -m nanoka.assign
# ou en une commande :
docker compose -f backend/deploy/docker-compose.yml --profile full up scrape post-process
```

`post-process` attend la **fin réussie** de `scrape`, puis enchaîne :  
`assign` → `ascension_report` → `weapon_report` → `talent_report`.

Données montées depuis `backend/data` sur l'hôte.

### 2. Runtime (API + UI)

Stack orchestrée (API prête avant le front) :

```powershell
npm run docker:stack:up    # API :8000 puis UI :8080
npm run docker:stack:down
```

API seule :

```powershell
npm run docker:api
```

UI seule (API sur l'hôte) :

```powershell
npm run docker:web:build
npm run dev:api
npm run docker:web:up
```

## Sécurité (Trivy)

Backend :

```powershell
npm run security:scan
```

Frontend :

```powershell
npm run security:web:scan
```
