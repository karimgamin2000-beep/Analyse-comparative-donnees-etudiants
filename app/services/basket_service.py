"""Service de valorisation et d'optimisation du panier de rentrée scolaire."""
from typing import Dict, List, Any
from config import BASKET_SPEC, STORES
from app.models.produit import CatalogueProduct, StoreArticle


def evaluate_basket(all_items: List[StoreArticle],
                    catalogue: Dict[str, CatalogueProduct]) -> Dict[str, Any]:
    """
    Évalue le panier de rentrée scolaire :
    - Coût dans chaque enseigne unique
    - Panier optimisé multi-enseignes (achat au moins cher par article)
    - Économie réalisée
    """
    prod_store = {}
    for it in all_items:
        if it.en_stock and it.prix_paye is not None:
            pid = it.produit_id
            ens = it.enseigne
            if pid not in prod_store:
                prod_store[pid] = {}
            prod_store[pid][ens] = it.prix_paye

    basket_store_costs = {}
    basket_store_details = {s: [] for s in STORES}

    for s in STORES:
        total = 0
        complet = True
        for pid, qty, label in BASKET_SPEC:
            price = prod_store.get(pid, {}).get(s)
            if price is not None:
                subtot = price * qty
                total += subtot
                basket_store_details[s].append({
                    'produit_id': pid, 'label': label, 'qty': qty,
                    'unit_price': price, 'total': subtot
                })
            else:
                complet = False
                basket_store_details[s].append({
                    'produit_id': pid, 'label': label, 'qty': qty,
                    'unit_price': None, 'total': None
                })
        basket_store_costs[s] = total if complet else None

    # Panier optimisé (achat de chaque article chez le moins cher)
    optimal_basket = []
    total_optimal = 0
    for pid, qty, label in BASKET_SPEC:
        avail_prices = prod_store.get(pid, {})
        if avail_prices:
            best_s = min(avail_prices, key=avail_prices.get)
            best_p = avail_prices[best_s]
            subtot = best_p * qty
            total_optimal += subtot
            optimal_basket.append({
                'produit_id': pid, 'label': label, 'qty': qty,
                'meilleure_enseigne': best_s, 'unit_price': best_p, 'total': subtot
            })
        else:
            optimal_basket.append({
                'produit_id': pid, 'label': label, 'qty': qty,
                'meilleure_enseigne': "Aucune", 'unit_price': 0, 'total': 0
            })

    # Calcul de l'économie par rapport à la meilleure enseigne unique
    valides = {s: c for s, c in basket_store_costs.items() if c is not None}
    best_single_store = min(valides, key=valides.get) if valides else None
    best_single_cost = valides[best_single_store] if best_single_store else 0
    economie_vs_meilleur = (best_single_cost - total_optimal) if best_single_cost else 0
    economie_pct = (economie_vs_meilleur / best_single_cost * 100.0) if best_single_cost else 0.0

    return {
        'spec': BASKET_SPEC,
        'par_enseigne': basket_store_costs,
        'details_enseignes': basket_store_details,
        'optimal': optimal_basket,
        'total_optimal': total_optimal,
        'meilleure_enseigne_unique': best_single_store,
        'cout_meilleure_enseigne_unique': best_single_cost,
        'economie_fcfa': economie_vs_meilleur,
        'economie_pct': economie_pct
    }
