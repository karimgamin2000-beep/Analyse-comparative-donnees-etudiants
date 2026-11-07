"""Chargeurs de données multi-sources (CSV, JSON, Excel)."""
from app.loaders.catalogue_loader import load_catalogue
from app.loaders.marche_lagune_loader import load_marche_lagune
from app.loaders.baobab_loader import load_baobab_shop
from app.loaders.comptoir_ivoire_loader import load_comptoir_ivoire
from app.loaders.history_loader import load_history

__all__ = [
    "load_catalogue",
    "load_marche_lagune",
    "load_baobab_shop",
    "load_comptoir_ivoire",
    "load_history"
]
