"""Services métier pour le traitement, l'analyse et la comparaison des données."""
from app.services.matching_service import normalize_text, match_article
from app.services.comparator_service import build_comparison_table, export_comparatif_csv, compute_synthesis
from app.services.basket_service import evaluate_basket
from app.services.history_service import analyze_history, benchmark_complexity

__all__ = [
    "normalize_text",
    "match_article",
    "build_comparison_table",
    "export_comparatif_csv",
    "compute_synthesis",
    "evaluate_basket",
    "analyze_history",
    "benchmark_complexity"
]
