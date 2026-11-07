"""Chargeur du catalogue de référence commun (30 produits)."""
import csv
from pathlib import Path
from typing import Dict
from config import CATALOGUE_PATH
from app.models.produit import CatalogueProduct
from app.services.matching_service import normalize_text


def load_catalogue(filepath: Path = None) -> Dict[str, CatalogueProduct]:
    """Charge le catalogue de référence et précalcule les tokens pour le rapprochement."""
    if filepath is None:
        filepath = CATALOGUE_PATH
    catalogue = {}
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row['produit_id']
            norm = normalize_text(row['nom'])
            tokens = set(norm.split())
            catalogue[pid] = CatalogueProduct(
                produit_id=pid,
                nom=row['nom'],
                categorie=row['categorie'],
                marque=row['marque'],
                norm=norm,
                tokens=tokens
            )
    return catalogue
