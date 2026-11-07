"""Service d'analyse temporelle (Black Friday) et de benchmarking de complexité algorithmique."""
import csv
import time
from pathlib import Path
from typing import Dict, Any, Tuple
from config import HISTORIQUE_PATH, BLACK_FRIDAY_START, BLACK_FRIDAY_END


def analyze_history(filepath: Path = None) -> Tuple[Dict[str, Any], int]:
    """
    Analyse l'historique des prix (20 000+ lignes) :
    - Prix moyen annuel par enseigne
    - Prix moyen durant la semaine du Black Friday
    - Évolution relative en pourcentage
    """
    if filepath is None:
        filepath = HISTORIQUE_PATH

    history_by_store = {}
    total_rows = 0

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1
            src = row['source']
            dt = row['date']
            prix = float(row['prix_fcfa'])

            if src not in history_by_store:
                history_by_store[src] = {'all': [], 'bf': []}
            history_by_store[src]['all'].append(prix)

            if BLACK_FRIDAY_START <= dt <= BLACK_FRIDAY_END:
                history_by_store[src]['bf'].append(prix)

    stats_globales = {}
    for src, d in history_by_store.items():
        avg_all = sum(d['all']) / len(d['all']) if d['all'] else 0.0
        avg_bf = sum(d['bf']) / len(d['bf']) if d['bf'] else 0.0
        diff = avg_bf - avg_all
        pct = (diff / avg_all * 100.0) if avg_all > 0 else 0.0
        stats_globales[src] = {
            'nb_releves': len(d['all']),
            'nb_releves_bf': len(d['bf']),
            'moyenne_annuelle': avg_all,
            'moyenne_bf': avg_bf,
            'ecart_fcfa': diff,
            'ecart_pct': pct
        }

    return stats_globales, total_rows


def benchmark_complexity(filepath: Path = None) -> Dict[str, Any]:
    """
    Démontre concrètement l'impact des choix de structures de données :
    - Recherche séquentielle naïve dans une liste (O(N) par requête -> O(M*N))
    - Recherche indexée par table de hachage / dictionnaire Python (O(1) par requête -> O(N + M))
    Mesure le temps d'exécution sur 500 requêtes types.
    """
    if filepath is None:
        filepath = HISTORIQUE_PATH

    raw_list = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for r in reader:
            raw_list.append((r['source'], r['produit_id'], r['date'], float(r['prix_fcfa'])))

    sample_queries = [
        ("Marché Lagune", "P04", "2025-11-28"),
        ("Baobab Shop", "P12", "2025-11-25"),
        ("Comptoir Ivoire", "P28", "2026-05-15"),
        ("Marché Lagune", "P15", "2026-01-10"),
        ("Baobab Shop", "P01", "2026-08-20")
    ] * 100  # 500 requêtes

    # Test 1 : Recherche linéaire
    t0 = time.perf_counter()
    linear_results = []
    for src, pid, dt in sample_queries:
        found_price = None
        for r_src, r_pid, r_dt, r_price in raw_list:
            if r_src == src and r_pid == pid and r_dt == dt:
                found_price = r_price
                break
        linear_results.append(found_price)
    t_linear = time.perf_counter() - t0

    # Test 2 : Table de hachage (dictionnaire Python)
    t0_idx = time.perf_counter()
    index_dict = {(r[0], r[1], r[2]): r[3] for r in raw_list}
    t_build_index = time.perf_counter() - t0_idx

    t0_hash = time.perf_counter()
    hash_results = []
    for src, pid, dt in sample_queries:
        hash_results.append(index_dict.get((src, pid, dt)))
    t_hash_lookup = time.perf_counter() - t0_hash

    return {
        'nb_lignes': len(raw_list),
        'nb_requetes': len(sample_queries),
        'temps_lineaire_sec': t_linear,
        'temps_construction_dict_sec': t_build_index,
        'temps_lookup_dict_sec': t_hash_lookup,
        'temps_total_dict_sec': t_build_index + t_hash_lookup,
        'facteur_acceleration': (t_linear / t_hash_lookup) if t_hash_lookup > 0 else float('inf')
    }
