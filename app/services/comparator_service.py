"""Service d'élaboration du comparatif multi-enseignes, exports CSV et synthèses statistiques."""
import csv
from pathlib import Path
from typing import Dict, List, Any
from config import COMPARATIF_CSV_PATH, resolve_output_path, STORES
from app.models.produit import CatalogueProduct, StoreArticle


def build_comparison_table(all_items: List[StoreArticle],
                           catalogue: Dict[str, CatalogueProduct]) -> List[Dict[str, Any]]:
    """
    Construit le tableau comparatif pour chaque produit disponible dans au moins deux enseignes.
    Un produit est retenu s'il est en stock ET a un prix exploitable dans au moins 2 enseignes.
    """
    prod_store_map = {}
    for item in all_items:
        pid = item.produit_id
        ens = item.enseigne
        if pid not in prod_store_map:
            prod_store_map[pid] = {}
        prod_store_map[pid][ens] = item

    comparison_rows = []
    
    for pid in sorted(catalogue.keys(), key=lambda x: int(x[1:])):
        store_data = prod_store_map.get(pid, {})
        
        eligible_stores = {}
        all_store_prices = {}
        
        for ens in STORES:
            it = store_data.get(ens)
            if it:
                all_store_prices[ens] = it.prix_paye
                if it.en_stock and it.prix_paye is not None:
                    eligible_stores[ens] = it.prix_paye
            else:
                all_store_prices[ens] = None

        if len(eligible_stores) >= 2:
            min_store = min(eligible_stores, key=eligible_stores.get)
            min_price = eligible_stores[min_store]
            max_price = max(eligible_stores.values())
            
            ecart_fcfa = max_price - min_price
            ecart_pct = (ecart_fcfa / min_price * 100.0) if min_price > 0 else 0.0

            row = {
                'produit_id': pid,
                'nom_produit': catalogue[pid].nom,
                'categorie': catalogue[pid].categorie,
                'prix_marche_lagune': all_store_prices.get("Marché Lagune"),
                'dispo_marche_lagune': "En stock" if ("Marché Lagune" in eligible_stores) else ("Rupture / Indispo" if "Marché Lagune" in store_data else "Non référencé"),
                'prix_baobab_shop': all_store_prices.get("Baobab Shop"),
                'dispo_baobab_shop': "En stock" if ("Baobab Shop" in eligible_stores) else ("Rupture / Indispo" if "Baobab Shop" in store_data else "Non référencé"),
                'prix_comptoir_ivoire': all_store_prices.get("Comptoir Ivoire"),
                'dispo_comptoir_ivoire': "En stock" if ("Comptoir Ivoire" in eligible_stores) else ("Rupture / Indispo" if "Comptoir Ivoire" in store_data else "Non référencé"),
                'enseigne_moins_chere': min_store,
                'prix_le_plus_bas': min_price,
                'ecart_fcfa': ecart_fcfa,
                'ecart_pourcentage': round(ecart_pct, 2),
                'nb_enseignes_disponibles': len(eligible_stores)
            }
            comparison_rows.append(row)

    return comparison_rows


def export_comparatif_csv(comparison_rows: List[Dict[str, Any]], filepath: Path = None) -> Path:
    """Exporte le tableau comparatif dans un fichier CSV avec séparateur point-virgule."""
    if filepath is None:
        filepath = COMPARATIF_CSV_PATH
    filepath = resolve_output_path(filepath)
    tmp_path = filepath.with_suffix(filepath.suffix + ".tmp")
    fieldnames = [
        'produit_id', 'nom_produit', 'categorie',
        'prix_marche_lagune', 'dispo_marche_lagune',
        'prix_baobab_shop', 'dispo_baobab_shop',
        'prix_comptoir_ivoire', 'dispo_comptoir_ivoire',
        'enseigne_moins_chere', 'prix_le_plus_bas',
        'ecart_fcfa', 'ecart_pourcentage'
    ]
    try:
        with open(tmp_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for r in comparison_rows:
                writer.writerow({
                    'produit_id': r['produit_id'],
                    'nom_produit': r['nom_produit'],
                    'categorie': r['categorie'],
                    'prix_marche_lagune': r['prix_marche_lagune'] if r['prix_marche_lagune'] is not None else "N/A",
                    'dispo_marche_lagune': r['dispo_marche_lagune'],
                    'prix_baobab_shop': r['prix_baobab_shop'] if r['prix_baobab_shop'] is not None else "N/A",
                    'dispo_baobab_shop': r['dispo_baobab_shop'],
                    'prix_comptoir_ivoire': r['prix_comptoir_ivoire'] if r['prix_comptoir_ivoire'] is not None else "N/A",
                    'dispo_comptoir_ivoire': r['dispo_comptoir_ivoire'],
                    'enseigne_moins_chere': r['enseigne_moins_chere'],
                    'prix_le_plus_bas': r['prix_le_plus_bas'],
                    'ecart_fcfa': r['ecart_fcfa'],
                    'ecart_pourcentage': f"{r['ecart_pourcentage']}%"
                })
        tmp_path.replace(filepath)
        return filepath
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def compute_synthesis(comparison_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcule la synthèse demandée :
    - Nombre de victoires de chaque enseigne (moins chère)
    - Écart moyen par rapport au prix le plus bas
    - Top 3 des produits où il y a le plus à gagner
    """
    wins = {s: 0 for s in STORES}
    ecarts_store = {s: [] for s in STORES}
    
    for r in comparison_rows:
        gagnant = r['enseigne_moins_chere']
        wins[gagnant] += 1
        min_p = r['prix_le_plus_bas']
        
        store_col_map = {
            "Marché Lagune": (r['prix_marche_lagune'], r['dispo_marche_lagune']),
            "Baobab Shop": (r['prix_baobab_shop'], r['dispo_baobab_shop']),
            "Comptoir Ivoire": (r['prix_comptoir_ivoire'], r['dispo_comptoir_ivoire'])
        }
        for s in STORES:
            p, dispo = store_col_map[s]
            if dispo == "En stock" and p is not None:
                diff_fcfa = p - min_p
                diff_pct = (diff_fcfa / min_p * 100.0) if min_p > 0 else 0.0
                ecarts_store[s].append((diff_fcfa, diff_pct))

    avg_ecarts = {}
    for s in STORES:
        if ecarts_store[s]:
            mean_fcfa = sum(d[0] for d in ecarts_store[s]) / len(ecarts_store[s])
            mean_pct = sum(d[1] for d in ecarts_store[s]) / len(ecarts_store[s])
            avg_ecarts[s] = (mean_fcfa, mean_pct, len(ecarts_store[s]))
        else:
            avg_ecarts[s] = (0.0, 0.0, 0)

    top_3_gains = sorted(comparison_rows, key=lambda x: x['ecart_fcfa'], reverse=True)[:3]

    return {
        'victoires': wins,
        'ecarts_moyens': avg_ecarts,
        'top_3_gains': top_3_gains
    }
