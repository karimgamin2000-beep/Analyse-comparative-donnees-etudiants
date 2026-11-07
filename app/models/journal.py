"""Journal de nettoyage traçant toutes les anomalies détectées et les actions prises."""
from datetime import datetime
from pathlib import Path
from config import resolve_output_path, JOURNAL_TXT_PATH


class CleaningJournal:
    """Consigne toutes les anomalies détectées et les corrections appliquées."""
    def __init__(self):
        self.entries = []

    def log(self, source: str, item_ref: str, nature: str, description: str, action_taken: str):
        entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'source': source,
            'reference': item_ref,
            'nature': nature,
            'description': description,
            'action': action_taken
        }
        self.entries.append(entry)

    def export(self, filepath: Path = None) -> Path:
        """Exporte le journal dans un fichier texte structuré de manière atomique."""
        if filepath is None:
            filepath = JOURNAL_TXT_PATH
        filepath = resolve_output_path(filepath)
        tmp_path = filepath.with_suffix(filepath.suffix + ".tmp")
        try:
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("JOURNAL DE NETTOYAGE DES DONNÉES - ANALYSE COMPARATIVE DE MARCHÉ\n")
                f.write(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Nombre total d'anomalies / opérations consignées : {len(self.entries)}\n")
                f.write("=" * 80 + "\n\n")
                
                for idx, e in enumerate(self.entries, start=1):
                    f.write(f"[{idx:02d}] {e['source']} | Réf : {e['reference']}\n")
                    f.write(f"     Nature      : {e['nature']}\n")
                    f.write(f"     Description : {e['description']}\n")
                    f.write(f"     Action      : {e['action']}\n")
                    f.write("-" * 80 + "\n")
            tmp_path.replace(filepath)
            return filepath
        finally:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
