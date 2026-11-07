"""Modèles de données représentant les produits du catalogue et les articles d'enseignes."""
from dataclasses import dataclass, field
from typing import Optional, Set


@dataclass
class CatalogueProduct:
    """Produit de référence issu du catalogue commun (P01 à P30)."""
    produit_id: str
    nom: str
    categorie: str
    marque: str
    norm: str = ""
    tokens: Set[str] = field(default_factory=set)


@dataclass
class StoreArticle:
    """Article collecté auprès d'une enseigne commerciale."""
    enseigne: str
    reference: str
    designation: str
    produit_id: Optional[str] = None
    prix_affiche: Optional[int] = None
    frais_livraison: int = 0
    remise_pct: float = 0.0
    prix_paye: Optional[int] = None
    en_stock: bool = True
    stock_dispo: int = 1
    note: Optional[float] = None
    nb_avis: int = 0
    rayon: Optional[str] = None
