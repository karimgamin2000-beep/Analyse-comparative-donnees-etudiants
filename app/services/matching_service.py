"""Service de normalisation textuelle et de rapprochement déterministe avec le catalogue."""
import re
import unicodedata
from typing import Dict, Tuple
from app.models.produit import CatalogueProduct


def normalize_text(text: str) -> str:
    """
    Normalise une chaîne de texte pour le rapprochement :
    - Décomposition Unicode (suppression des accents)
    - Minuscules
    - Substitution des synonymes et abréviations techniques
    - Suppression des caractères spéciaux
    """
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', str(text))
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    
    # Séparation des chiffres et des unités collées (ex: 1To -> 1 To, 128Go -> 128 Go, 205L -> 205 L)
    text = re.sub(r'(\d+)([a-zA-Z]+)', r'\1 \2', text)

    mappings = [
        (r'\bfrigo\b', 'refrigerateur'),
        (r'\bdd\b', 'disque dur'),
        (r'\bventilo\b', 'ventilateur'),
        (r'\bclim\b', 'climatiseur'),
        (r'\bgb\b', 'go'),
        (r'\btb\b', 'to'),
        (r'\bsamsun\b', 'samsung'),
        (r'\bwireless\s+mouse\b', 'souris sans fil'),
        (r'\bmouse\b', 'souris'),
        (r'\bmicrowave\b', 'micro ondes'),
        (r'\brefrigerator\b', 'refrigerateur'),
        (r'\bfreezer\b', 'congelateur'),
        (r'\biron\b', 'fer a repasser'),
        (r'\bkettle\b', 'bouilloire'),
        (r'\bblender\b', 'mixeur'),
        (r'\bstand fan\b', 'ventilateur'),
        (r'\bair conditioner\b', 'climatiseur'),
        (r'\bpc portable\b', ''),
        (r'\blaptop\b', ''),
        (r'\bflash drive\b', 'cle usb'),
        (r'\bexternal hard drive\b', 'disque dur externe'),
        (r'\bhard drive\b', 'disque dur'),
        (r'1\.5cv', '1,5 cv'),
        (r'1\.5l', '1,5 l'),
        (r'1\.7l', '1,7 l'),
    ]
    for pattern, repl in mappings:
        text = re.sub(pattern, repl, text)
        
    text = re.sub(r'[^a-z0-9]', ' ', text)
    return ' '.join(text.split())


def match_article(designation: str, catalogue: Dict[str, CatalogueProduct]) -> Tuple[str, int]:
    """
    Associe de façon déterministe une désignation d'article à un produit du catalogue.
    Retourne (produit_id, score_confiance).
    """
    clean_desig = normalize_text(designation)
    tokens = set(clean_desig.split())
    
    best_pid = None
    best_score = -1
    
    for pid, cat in catalogue.items():
        score = 0
        common = tokens.intersection(cat.tokens)
        score += len(common) * 2
        
        # Bonus fort pour la présence d'identifiants techniques ou modèles numériques
        for tok in common:
            if any(c.isdigit() for c in tok):
                score += 5
                
        # Bonus de correspondance de marque
        if cat.marque.lower() in clean_desig:
            score += 3
            
        if score > best_score:
            best_score = score
            best_pid = pid
            
    return best_pid, best_score
