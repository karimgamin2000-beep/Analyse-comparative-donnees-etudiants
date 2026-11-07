"""Chargeur et nettoyeur des données de Comptoir Ivoire (classeur Excel .xlsx)."""
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List
from config import COMPTOIR_IVOIRE_PATH
from app.models.produit import CatalogueProduct, StoreArticle
from app.models.journal import CleaningJournal
from app.loaders.utils import parse_price_string
from app.services.matching_service import match_article


def load_comptoir_ivoire(filepath: Path = None,
                         catalogue: Dict[str, CatalogueProduct] = None,
                         journal: CleaningJournal = None) -> List[StoreArticle]:
    """
    Charge et nettoie les données de Comptoir Ivoire depuis le classeur Excel (.xlsx)
    en utilisant exclusivement la bibliothèque standard (zipfile + xml.etree).
    Règles de calcul : Le client paie prix_catalogue * (1 - remise/100).
    """
    if filepath is None:
        filepath = COMPTOIR_IVOIRE_PATH

    articles = {}
    with zipfile.ZipFile(filepath, 'r') as z:
        sheet_xml = z.read('xl/worksheets/sheet1.xml')
        root = ET.fromstring(sheet_xml)
        
        ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        
        for r in root.findall('ns:sheetData/ns:row', ns):
            row_idx = int(r.attrib.get('r', 0))
            if row_idx < 4:
                continue  # Ligne 1 = Titre, Ligne 3 = En-têtes
                
            cells = {}
            for c in r.findall('ns:c', ns):
                cell_ref = c.attrib.get('r', '')
                col = ''.join(filter(str.isalpha, cell_ref))
                v_tag = c.find('ns:v', ns)
                is_tag = c.find('ns:is', ns)
                
                val = ""
                if v_tag is not None and v_tag.text:
                    val = v_tag.text
                elif is_tag is not None:
                    val = ''.join(is_tag.itertext())
                cells[col] = val
                
            code = cells.get('A', '').strip()
            article = cells.get('B', '').strip()
            rayon = cells.get('C', '').strip()
            prix_cat_str = cells.get('D', '').strip()
            remise_str = cells.get('E', '').strip()
            quantite_str = cells.get('F', '').strip()

            if not code or not article:
                continue

            prix_catalogue = parse_price_string(prix_cat_str)
            remise_pct = float(remise_str) if remise_str else 0.0
            quantite = int(quantite_str) if quantite_str and quantite_str.isdigit() else 0

            if prix_catalogue is not None:
                prix_paye = round(prix_catalogue * (1.0 - remise_pct / 100.0))
            else:
                prix_paye = None
                if journal:
                    journal.log("Comptoir Ivoire", code, "Prix manquant",
                                f"Prix brut : '{prix_cat_str}'",
                                "Prix payé marqué comme None")

            en_stock = (quantite > 0)
            if not en_stock and journal:
                journal.log("Comptoir Ivoire", code, "Rupture de stock",
                            f"Quantité en rayon : {quantite}",
                            "Produit en rupture physique, exclu du statut 'moins cher'")

            pid, score = match_article(article, catalogue)
            if journal:
                journal.log("Comptoir Ivoire", code, "Rapprochement",
                            f"Article : '{article}'",
                            f"Associé au produit {pid} ('{catalogue[pid].nom}') avec score {score}")

            articles[code] = StoreArticle(
                enseigne="Comptoir Ivoire",
                reference=code,
                designation=article,
                produit_id=pid,
                rayon=rayon,
                prix_affiche=prix_catalogue,
                remise_pct=remise_pct,
                prix_paye=prix_paye,
                en_stock=en_stock,
                stock_dispo=quantite
            )

    return list(articles.values())
