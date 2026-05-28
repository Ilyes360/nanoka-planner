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
