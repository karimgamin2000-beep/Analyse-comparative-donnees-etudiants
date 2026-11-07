"""Chargeur de l'historique des prix (20 000+ lignes)."""
import csv
from pathlib import Path
from typing import List, Tuple
from config import HISTORIQUE_PATH


def load_history(filepath: Path = None) -> List[Tuple[str, str, str, float]]:
    """Charge l'historique brut des prix sous forme de liste de tuples (source, produit_id, date, prix)."""
    if filepath is None:
        filepath = HISTORIQUE_PATH
    history = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for r in reader:
            history.append((r['source'], r['produit_id'], r['date'], float(r['prix_fcfa'])))
    return history
