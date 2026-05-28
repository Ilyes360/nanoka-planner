# Nanoka scraper (Genshin Impact)

Scrape et post-traitement des données personnages / armes / objets depuis [gi.nanoka.cc](https://gi.nanoka.cc/), avec interface web de planification.

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

Prérequis : loadouts dans `backend/data/processed/` (`python -m nanoka.assign` depuis `backend/`).

```powershell
pip install -r backend/requirements/requirements-dev.txt
cd frontend && npm install && cd ..

npm run dev:api    # API http://127.0.0.1:8000
npm run dev:web    # UI  http://localhost:5173
```

## Docker

```powershell
docker compose -f backend/deploy/docker-compose.yml build
docker compose -f backend/deploy/docker-compose.yml run --rm scrape -m nanoka.scrape
docker compose -f backend/deploy/docker-compose.yml run --rm pipeline -m nanoka.assign
docker compose -f backend/deploy/docker-compose.yml --profile full up scrape post-process
```

Données montées depuis `backend/data` sur l'hôte.

### Frontend (UI statique + nginx)

Build et run séparés du backend. L'UI proxifie `/api` et `/media` vers l'API (par défaut `http://host.docker.internal:8000`).

```powershell
npm run docker:web:build
npm run dev:api   # API sur l'hôte, port 8000
npm run docker:web:up   # UI http://localhost:8080
```

Variables utiles (`.env` à côté de `frontend/deploy/docker-compose.yml` ou export) :

- `WEB_PORT` — port hôte (défaut `8080`)
- `API_UPSTREAM` — URL de l'API (ex. `http://host.docker.internal:8000`)

Image CI : `ghcr.io/<owner>/nanoka-web:latest`

## Sécurité (Trivy)

Backend :

```powershell
npm run security:scan
```

Frontend :

```powershell
npm run security:web:scan
```
