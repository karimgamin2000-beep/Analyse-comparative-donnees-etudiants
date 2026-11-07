"""Chargeur et nettoyeur des données de Baobab Shop (JSON)."""
import json
from pathlib import Path
from typing import Dict, List
from config import BAOBAB_SHOP_PATH
from app.models.produit import CatalogueProduct, StoreArticle
from app.models.journal import CleaningJournal
from app.services.matching_service import match_article


def load_baobab_shop(filepath: Path = None,
                     catalogue: Dict[str, CatalogueProduct] = None,
                     journal: CleaningJournal = None) -> List[StoreArticle]:
    """
    Charge et nettoie les données de Baobab Shop.
    Règles de calcul : Le client paie amount + delivery_fee.
    """
    if filepath is None:
        filepath = BAOBAB_SHOP_PATH

    articles = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data.get('items', []):
        sku = item.get('sku', '').strip()
        title = item.get('title', '').strip()
        pricing = item.get('pricing', {})
        amount = pricing.get('amount')
        delivery_fee = pricing.get('delivery_fee', 0)
        stock = item.get('stock', 0)
        rating = item.get('rating', {})

        # Détection doublon
        if sku in articles:
            if journal:
                journal.log("Baobab Shop", sku, "Doublon",
                            f"SKU {sku} en doublon dans le flux JSON",
                            "Conservation de la 1ère occurrence")
            continue

        # Prix payé
        if amount is not None and isinstance(amount, (int, float)):
            prix_paye = int(amount + delivery_fee)
        else:
            prix_paye = None
            if journal:
                journal.log("Baobab Shop", sku, "Prix non exploitable",
                            f"Montant invalide : {amount}",
                            "Prix marqué comme None")

        # Disponibilité
        en_stock = (stock is not None and stock > 0)
        if not en_stock and journal:
            journal.log("Baobab Shop", sku, "Rupture de stock",
                        f"Stock disponible : {stock}",
                        "Produit en rupture, exclu du statut 'moins cher'")

        # Rapprochement catalogue
        pid, score = match_article(title, catalogue)
        if journal:
            journal.log("Baobab Shop", sku, "Rapprochement",
                        f"Titre : '{title}'",
                        f"Associé au produit {pid} ('{catalogue[pid].nom}') avec score {score}")

        articles[sku] = StoreArticle(
            enseigne="Baobab Shop",
            reference=sku,
            designation=title,
            produit_id=pid,
            prix_affiche=amount,
            frais_livraison=delivery_fee,
            prix_paye=prix_paye,
            en_stock=en_stock,
            stock_dispo=stock,
            note=rating.get('average'),
            nb_avis=rating.get('count', 0)
        )

    return list(articles.values())
