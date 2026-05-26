# Nanoka scraper (Genshin Impact)

Scrape et post-traitement des données personnages / armes / objets depuis [gi.nanoka.cc](https://gi.nanoka.cc/).

## Structure

```
python-project/
├── src/
│   ├── paths.py          # Chemins data/raw, data/processed, …
│   ├── scrape.py         # Téléchargement API + images
│   ├── assign.py         # Loadouts + matériaux (used_by)
│   └── migrate_paths.py  # Correction des chemins d'images dans les JSON
├── data/
│   ├── raw/              # JSON bruts
│   ├── processed/        # Loadouts enrichis
│   └── images/           # characters, weapons, items
└── requirements.txt
```

## Installation

```powershell
cd c:\Users\iyous\python-project
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Utilisation

Depuis la racine du projet :

```powershell
python src/scrape.py
python src/assign.py
```

Test rapide :

```powershell
python src/scrape.py --max-characters 3 --max-weapons 3 --max-items 20 --skip-image-download
python src/assign.py
```

## Sorties

| Dossier | Contenu |
|---------|---------|
| `data/raw/` | `characters_nanoka.json`, `weapons_nanoka.json`, `items_nanoka.json` |
| `data/processed/` | `character_loadouts.json`, `weapon_loadouts.json`, index matériaux |
