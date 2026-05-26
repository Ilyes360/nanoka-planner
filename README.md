# Nanoka scraper (Genshin Impact)

Scrape et post-traitement des données personnages / armes / objets depuis [gi.nanoka.cc](https://gi.nanoka.cc/).

## Structure

```
python-project/
├── nanoka/
│   ├── paths.py              # Chemins data/, fichiers JSON
│   ├── scrape.py             # Téléchargement API + images
│   ├── assign.py             # Loadouts + matériaux (used_by)
│   ├── ascension_report.py   # Matériaux + livres d'EXP par phase
│   ├── exp_books.py          # Calcul des livres d'EXP
│   └── migrate_paths.py      # Correction des chemins d'images
├── data/
│   ├── raw/
│   ├── processed/
│   └── images/
├── tests/
├── deploy/                   # Dockerfiles (Alpine)
└── docker-compose.yml
```

## Installation

```powershell
cd c:\Users\iyous\python-project
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Tests

```powershell
pytest
pytest --cov=nanoka --cov-report=term-missing
```

## Utilisation

```powershell
python -m nanoka.scrape
python -m nanoka.assign
python -m nanoka.ascension_report --print
python -m nanoka.ascension_report --character Aino --print
```

Test rapide :

```powershell
python -m nanoka.scrape --max-characters 3 --max-weapons 3 --max-items 20 --skip-image-download
python -m nanoka.assign
```

## Docker

```powershell
docker compose build
docker compose run --rm scrape -m nanoka.scrape
docker compose run --rm pipeline -m nanoka.assign
docker compose run --rm pipeline -m nanoka.ascension_report --print
docker compose --profile full up scrape post-process
```

Les données restent dans `./data` sur l'hôte.

## Sécurité (Trivy)

```powershell
.\scripts\trivy-scan.ps1
```
