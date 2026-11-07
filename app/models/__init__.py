"""Modèles de données du projet."""
from app.models.produit import CatalogueProduct, StoreArticle
from app.models.journal import CleaningJournal

__all__ = ["CatalogueProduct", "StoreArticle", "CleaningJournal"]
