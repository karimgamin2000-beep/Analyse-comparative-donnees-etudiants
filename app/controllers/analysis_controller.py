"""Contrôleur principal orchestrant le chargement, le nettoyage, l'analyse et la restitution."""
import time
from pathlib import Path
from typing import Optional

from app.models.journal import CleaningJournal
from app.loaders.catalogue_loader import load_catalogue
from app.loaders.marche_lagune_loader import load_marche_lagune
from app.loaders.baobab_loader import load_baobab_shop
from app.loaders.comptoir_ivoire_loader import load_comptoir_ivoire
from app.services.comparator_service import build_comparison_table, export_comparatif_csv, compute_synthesis
from app.services.basket_service import evaluate_basket
from app.services.history_service import analyze_history, benchmark_complexity
from app.views.console_view import ConsoleView
from config import (
    CATALOGUE_PATH, MARCHE_LAGUNE_PATH, BAOBAB_SHOP_PATH, COMPTOIR_IVOIRE_PATH,
    HISTORIQUE_PATH, COMPARATIF_CSV_PATH, JOURNAL_TXT_PATH
)


class AnalysisController:
    """Contrôleur responsable du pipeline complet d'analyse comparative de marché."""

    def __init__(self,
                 view: Optional[ConsoleView] = None,
                 journal: Optional[CleaningJournal] = None,
                 catalogue_path: Path = CATALOGUE_PATH,
                 marche_lagune_path: Path = MARCHE_LAGUNE_PATH,
                 baobab_path: Path = BAOBAB_SHOP_PATH,
                 comptoir_ivoire_path: Path = COMPTOIR_IVOIRE_PATH,
                 historique_path: Path = HISTORIQUE_PATH,
                 comparatif_out: Path = COMPARATIF_CSV_PATH,
                 journal_out: Path = JOURNAL_TXT_PATH):
        self.view = view or ConsoleView()
        self.journal = journal or CleaningJournal()
        self.catalogue_path = catalogue_path
        self.marche_lagune_path = marche_lagune_path
        self.baobab_path = baobab_path
        self.comptoir_ivoire_path = comptoir_ivoire_path
        self.historique_path = historique_path
        self.comparatif_out = comparatif_out
        self.journal_out = journal_out

    def run(self):
        """Exécute l'intégralité du pipeline d'analyse et de restitution."""
        t_start = time.perf_counter()
        self.view.header()

        # 1. Chargement du catalogue
        self.view.step(1, 7, "Chargement du catalogue de référence...")
        catalogue = load_catalogue(self.catalogue_path)
        self.view.info(f"{len(catalogue)} produits de référence enregistrés (P01 à P30).")

        # 2. Chargement et nettoyage des enseignes
        self.view.step(2, 7, "Chargement et nettoyage des données des enseignes...")
        items_ml = load_marche_lagune(self.marche_lagune_path, catalogue, self.journal)
        self.view.info(f"Marché Lagune    : {len(items_ml)} articles traités.")

        items_bb = load_baobab_shop(self.baobab_path, catalogue, self.journal)
        self.view.info(f"Baobab Shop      : {len(items_bb)} articles traités.")

        items_ci = load_comptoir_ivoire(self.comptoir_ivoire_path, catalogue, self.journal)
        self.view.info(f"Comptoir Ivoire  : {len(items_ci)} articles traités.")

        all_items = items_ml + items_bb + items_ci
        self.journal.export(self.journal_out)
        self.view.info(f"Journal de nettoyage exporté dans '{self.journal_out.name}' ({len(self.journal.entries)} entrées).")

        # 3. Comparatif des prix
        self.view.step(3, 7, "Rapprochement et génération du comparatif des prix...")
        comp_rows = build_comparison_table(all_items, catalogue)
        export_comparatif_csv(comp_rows, self.comparatif_out)
        self.view.info(f"{len(comp_rows)} produits comparables (disponibles dans au moins 2 enseignes).")
        self.view.info(f"Tableau comparatif exporté dans '{self.comparatif_out.name}'.")
        self.view.afficher_apercu_comparatif(comp_rows)

        # 4. Synthèse statistique
        self.view.step(4, 7, "Synthèse des résultats comparatifs :")
        synth = compute_synthesis(comp_rows)
        self.view.afficher_synthese(synth, len(comp_rows))

        # 5. Panier de rentrée
        self.view.step(5, 7, "Analyse du panier de rentrée scolaire :")
        basket_res = evaluate_basket(all_items, catalogue)
        self.view.afficher_panier(basket_res)

        # 6. Historique et Black Friday
        self.view.step(6, 7, "Analyse de l'historique des prix (Quand fallait-il acheter ?) :")
        stats_bf, nb_hist = analyze_history(self.historique_path)
        self.view.afficher_historique(stats_bf, nb_hist)

        # 7. Mesure de performance et complexité
        self.view.step(7, 7, "Mesure de complexité et temps d'exécution (20 000+ lignes) :")
        bench = benchmark_complexity(self.historique_path)
        self.view.afficher_complexite(bench)

        # Fin et bilan
        t_total = time.perf_counter() - t_start
        self.view.footer(t_total, self.comparatif_out.name, self.journal_out.name)
