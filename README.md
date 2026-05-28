# Nanoka scraper (Genshin Impact)

Scrape et post-traitement des données personnages / armes / objets depuis [gi.nanoka.cc](https://gi.nanoka.cc/).

## Structure

```
python-project/
├── nanoka/
│   ├── paths.py              # Chemins data/, fichiers JSON
│   ├── scrape.py             # Téléchargement API + images
│   ├── assign.py             # Loadouts + matériaux (used_by)
│   ├── ascension_report.py   # Rapport ascension personnages
│   ├── weapon_report.py      # Rapport ascension armes
│   ├── talent_report.py      # Rapport talents personnages
│   ├── exp_books.py          # Calcul des livres d'EXP (personnages)
│   ├── weapon_exp.py         # Calcul des minerais d'EXP (armes)
│   ├── report_common.py      # Helpers JSON / matériaux / totaux
│   └── migrate_paths.py      # Correction des chemins d'images
├── requirements/             # Dépendances pip
├── config/trivy/             # Scan sécurité Trivy
├── data/
│   ├── raw/
│   ├── processed/
│   └── images/
├── tests/
├── scripts/                  # Scripts utilitaires (ex. trivy-scan.ps1)
└── deploy/                   # Dockerfiles + docker-compose.yml
```

## Installation

```powershell
cd c:\Users\iyous\python-project
.\.venv\Scripts\Activate.ps1
pip install -r requirements/requirements.txt
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
python -m nanoka.ascension_report --print                  # personnages
python -m nanoka.weapon_report --weapon Aquila            # armes
python -m nanoka.talent_report --character Aino           # talents
```

Test rapide :

```powershell
python -m nanoka.scrape --max-characters 3 --max-weapons 3 --max-items 20 --skip-image-download
python -m nanoka.assign
```

## Docker

```powershell
docker compose -f deploy/docker-compose.yml build
docker compose -f deploy/docker-compose.yml run --rm scrape -m nanoka.scrape
docker compose -f deploy/docker-compose.yml run --rm pipeline -m nanoka.assign
docker compose -f deploy/docker-compose.yml run --rm pipeline -m nanoka.ascension_report --print
docker compose -f deploy/docker-compose.yml run --rm pipeline -m nanoka.weapon_report
docker compose -f deploy/docker-compose.yml run --rm pipeline -m nanoka.talent_report
docker compose -f deploy/docker-compose.yml --profile full up scrape post-process
```

Les données restent dans `./data` sur l'hôte.

Via npm (mêmes commandes raccourcies) : `npm run docker:build`, `npm run docker:assign`, etc.

## Sécurité (Trivy)

```powershell
.\scripts\trivy-scan.ps1
npm run security
```
