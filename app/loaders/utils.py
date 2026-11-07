"""Utilitaires communs pour le parsing et le nettoyage des données brutes."""
import re
from typing import Optional


def parse_price_string(price_str) -> Optional[int]:
    """Extrait la valeur entière d'un prix sous forme de texte (ex: '102 900 FCFA')."""
    if not price_str or "demande" in str(price_str).lower():
        return None
    cleaned = re.sub(r'[^\d]', '', str(price_str))
    return int(cleaned) if cleaned else None
