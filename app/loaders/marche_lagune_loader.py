"""Chargeur et nettoyeur des données de Marché Lagune (CSV)."""
import csv
from pathlib import Path
from typing import Dict, List
from config import MARCHE_LAGUNE_PATH
from app.models.produit import CatalogueProduct, StoreArticle
from app.models.journal import CleaningJournal
from app.loaders.utils import parse_price_string
from app.services.matching_service import match_article


def load_marche_lagune(filepath: Path = None,
                       catalogue: Dict[str, CatalogueProduct] = None,
                       journal: CleaningJournal = None) -> List[StoreArticle]:
    """
    Charge et nettoie les données de Marché Lagune.
    Règles de calcul : Le prix affiché inclut la livraison.
    """
    if filepath is None:
        filepath = MARCHE_LAGUNE_PATH

    articles = {}
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row_num, row in enumerate(reader, start=2):
            ref = row.get('reference', '').strip()
            desig_brute = row.get('designation', '')
            desig = desig_brute.strip()
            prix_brut = row.get('prix', '').strip()
            ancien_prix_brut = row.get('ancien_prix', '').strip()
            dispo = row.get('disponibilite', '').strip()
            note = row.get('note_clients', '').strip().replace(',', '.')
            avis = row.get('nb_avis', '').strip()

            # 1. Gestion des espaces parasites dans la désignation
            if desig_brute != desig and journal:
                journal.log("Marché Lagune", ref, "Formatage texte",
                            f"Espaces superflus en début/fin : '{desig_brute}'",
                            f"Nettoyé en '{desig}'")

            # 2. Détection des doublons de référence
            if ref in articles:
                if journal:
                    journal.log("Marché Lagune", ref, "Doublon",
                                f"Ligne {row_num} : référence {ref} déjà chargée",
                                "Doublon ignoré (conservation de la 1ère occurrence)")
                continue

            # 3. Analyse du prix
            prix_num = parse_price_string(prix_brut)
            ancien_prix_num = parse_price_string(ancien_prix_brut)
            
            if prix_num is None and journal:
                journal.log("Marché Lagune", ref, "Prix non exploitable",
                            f"Prix affiché : '{prix_brut}'",
                            "Produit marqué comme non exploitable (prix = None)")

            # 4. Détection et correction de la coquille sur le Tecno Spark 20 (ML-1021)
            # Affiché à 779 000 FCFA pour un ancien prix de 88 700 FCFA -> facteur 10 évident
            if ref == "ML-1021" and prix_num == 779000:
                prix_corrige = 77900
                if journal:
                    journal.log("Marché Lagune", ref, "Prix aberrant (coquille)",
                                f"Prix affiché 779 000 FCFA avec ancien prix {ancien_prix_num} FCFA",
                                f"Coquille corrigée automatiquement à {prix_corrige} FCFA")
                prix_num = prix_corrige

            # 5. Disponibilité
            en_stock = (dispo != "Rupture")
            if not en_stock and journal:
                journal.log("Marché Lagune", ref, "Rupture de stock",
                            f"Disponibilité indiquée : '{dispo}'",
                            "Exclu du statut de 'moins cher' pour les comparatifs")

            # 6. Rapprochement catalogue
            pid, score = match_article(desig, catalogue)
            if journal:
                journal.log("Marché Lagune", ref, "Rapprochement",
                            f"Désignation : '{desig}'",
                            f"Associé au produit {pid} ('{catalogue[pid].nom}') avec score {score}")

            articles[ref] = StoreArticle(
                enseigne="Marché Lagune",
                reference=ref,
                designation=desig,
                produit_id=pid,
                prix_affiche=prix_num,
                prix_paye=prix_num,  # Livraison incluse
                en_stock=en_stock,
                stock_dispo=1 if en_stock else 0,
                note=float(note) if note else None,
                nb_avis=int(avis) if avis and avis.isdigit() else 0
            )

    return list(articles.values())
