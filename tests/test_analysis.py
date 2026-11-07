"""Tests unitaires pour l'application d'analyse comparative de marché."""
import unittest
from pathlib import Path

from config import DATA_DIR, BASKET_SPEC
from app.loaders.catalogue_loader import load_catalogue
from app.loaders.marche_lagune_loader import load_marche_lagune
from app.loaders.baobab_loader import load_baobab_shop
from app.loaders.comptoir_ivoire_loader import load_comptoir_ivoire
from app.loaders.utils import parse_price_string
from app.models.journal import CleaningJournal
from app.services.matching_service import normalize_text, match_article
from app.services.comparator_service import build_comparison_table, compute_synthesis
from app.services.basket_service import evaluate_basket
from app.services.history_service import analyze_history, benchmark_complexity


class TestMarketAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = load_catalogue(DATA_DIR / "catalogue_reference.csv")
        cls.journal = CleaningJournal()
        cls.items_ml = load_marche_lagune(DATA_DIR / "marche_lagune.csv", cls.catalogue, cls.journal)
        cls.items_bb = load_baobab_shop(DATA_DIR / "baobab_shop.json", cls.catalogue, cls.journal)
        cls.items_ci = load_comptoir_ivoire(DATA_DIR / "comptoir_ivoire.xlsx", cls.catalogue, cls.journal)
        cls.all_items = cls.items_ml + cls.items_bb + cls.items_ci

    def test_catalogue_loaded(self):
        """Vérifie que les 30 produits du catalogue sont bien chargés."""
        self.assertEqual(len(self.catalogue), 30)
        self.assertIn('P01', self.catalogue)
        self.assertIn('P30', self.catalogue)

    def test_normalize_text_and_synonyms(self):
        """Vérifie le remplacement des synonymes et la suppression des accents."""
        self.assertEqual(normalize_text("Frigo Hisense"), "refrigerateur hisense")
        self.assertEqual(normalize_text("DD externe Seagate 1To"), "disque dur externe seagate 1 to")
        self.assertEqual(normalize_text("Samsun Galaxy A15 128Go"), "samsung galaxy a15 128 go")

    def test_matching_accuracy(self):
        """Vérifie le rapprochement exact de cas complexes."""
        pid_frigo, score1 = match_article("Frigo Hisense 205L", self.catalogue)
        self.assertEqual(pid_frigo, "P20")

        pid_dd, score2 = match_article("DD externe Seagate 1To", self.catalogue)
        self.assertEqual(pid_dd, "P15")

        pid_microwave, score3 = match_article("Samsung Microwave 23L", self.catalogue)
        self.assertEqual(pid_microwave, "P28")

    def test_aberrant_price_correction(self):
        """Vérifie la correction de la coquille du Tecno Spark 20 (ML-1021)."""
        spark_ml = next(it for it in self.items_ml if it.reference == "ML-1021")
        self.assertEqual(spark_ml.prix_paye, 77900)

    def test_parse_price_string(self):
        """Vérifie la conversion robuste des prix textuels avec espaces insécables."""
        self.assertEqual(parse_price_string("102\u202f900 FCFA"), 102900)
        self.assertEqual(parse_price_string("279 300"), 279300)
        self.assertIsNone(parse_price_string("Prix sur demande"))
        self.assertIsNone(parse_price_string(""))

    def test_comparison_table_and_out_of_stock_rule(self):
        """Vérifie qu'un produit en rupture n'est pas retenu comme le moins cher."""
        comp_rows = build_comparison_table(self.all_items, self.catalogue)
        self.assertGreaterEqual(len(comp_rows), 20)

        # P22 : TV Samsung 43" (Comptoir Ivoire a le prix le plus bas mais est en rupture de stock !)
        p22 = next(r for r in comp_rows if r['produit_id'] == "P22")
        self.assertEqual(p22['dispo_comptoir_ivoire'], "Rupture / Indispo")
        # Le vainqueur retenu doit être en stock (Baobab Shop à 244 400 F)
        self.assertEqual(p22['enseigne_moins_chere'], "Baobab Shop")

    def test_basket_evaluation(self):
        """Vérifie les calculs du panier de rentrée."""
        basket = evaluate_basket(self.all_items, self.catalogue)
        self.assertIsNotNone(basket['total_optimal'])
        self.assertEqual(basket['total_optimal'], 477575)
        self.assertEqual(basket['meilleure_enseigne_unique'], "Comptoir Ivoire")
        self.assertEqual(basket['cout_meilleure_enseigne_unique'], 484075)
        self.assertEqual(basket['economie_fcfa'], 6500)

    def test_history_and_complexity(self):
        """Vérifie l'analyse de l'historique et la complexité."""
        stats, count = analyze_history(DATA_DIR / "historique_prix.csv")
        self.assertEqual(count, 20876)
        self.assertIn("Marché Lagune", stats)

        bench = benchmark_complexity(DATA_DIR / "historique_prix.csv")
        self.assertGreater(bench['facteur_acceleration'], 50.0)


if __name__ == "__main__":
    unittest.main()
