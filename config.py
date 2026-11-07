"""Configuration et constantes du projet d'analyse comparative de marché."""
from pathlib import Path
import os
import stat

# Répertoires principaux
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "donnees"
EXPORT_DIR = PROJECT_ROOT

# Fichiers sources (données)
CATALOGUE_PATH = DATA_DIR / "catalogue_reference.csv"
MARCHE_LAGUNE_PATH = DATA_DIR / "marche_lagune.csv"
BAOBAB_SHOP_PATH = DATA_DIR / "baobab_shop.json"
COMPTOIR_IVOIRE_PATH = DATA_DIR / "comptoir_ivoire.xlsx"
HISTORIQUE_PATH = DATA_DIR / "historique_prix.csv"

# Fichiers de sortie générés
COMPARATIF_CSV_PATH = EXPORT_DIR / "comparatif.csv"
JOURNAL_TXT_PATH = EXPORT_DIR / "journal_nettoyage.txt"

# Période Black Friday 2025
BLACK_FRIDAY_START = "2025-11-24"
BLACK_FRIDAY_END = "2025-11-30"

# Enseignes de référence
STORES = ["Marché Lagune", "Baobab Shop", "Comptoir Ivoire"]

# Spécification du panier de rentrée scolaire
BASKET_SPEC = [
    ('P04', 1, "Tecno Spark 20 128 Go"),
    ('P12', 1, "Lenovo IdeaPad 3 Core i3"),
    ('P14', 2, "Clé USB SanDisk 64 Go"),
    ('P15', 1, "Disque dur externe Seagate 1 To"),
    ('P28', 1, "Micro-ondes Samsung 23 L")
]


def resolve_output_path(filepath: Path) -> Path:
    """Retourne un chemin absolu et retire le drapeau lecture seule si présent."""
    path = Path(filepath)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if path.exists():
        try:
            os.chmod(path, os.stat(path).st_mode | stat.S_IWRITE)
        except OSError:
            pass
    return path
