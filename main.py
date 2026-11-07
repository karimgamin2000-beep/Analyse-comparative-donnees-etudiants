#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Point d'entrée principal : Application console d'analyse comparative de marché.
Projet : DA Python · L2 Computer Science · Séance 3
Enseignes : Marché Lagune, Baobab Shop, Comptoir Ivoire
"""
import sys
import argparse
from pathlib import Path

from config import DATA_DIR, EXPORT_DIR
from app.views.console_view import ConsoleView
from app.controllers.analysis_controller import AnalysisController

# Configuration de l'encodage standard UTF-8 sur Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Analyse comparative de marché - Électronique et électroménager à Abidjan"
    )
    parser.add_argument(
        "--data-dir",
        default=str(DATA_DIR),
        help="Chemin du répertoire contenant les fichiers de données sources"
    )
    parser.add_argument(
        "--export-dir",
        default=str(EXPORT_DIR),
        help="Chemin du répertoire pour les fichiers générés (comparatif.csv, journal_nettoyage.txt)"
    )
    args = parser.parse_args()

    data_path = Path(args.data_dir).resolve()
    export_path = Path(args.export_dir).resolve()

    controller = AnalysisController(
        view=ConsoleView(),
        catalogue_path=data_path / "catalogue_reference.csv",
        marche_lagune_path=data_path / "marche_lagune.csv",
        baobab_path=data_path / "baobab_shop.json",
        comptoir_ivoire_path=data_path / "comptoir_ivoire.xlsx",
        historique_path=data_path / "historique_prix.csv",
        comparatif_out=export_path / "comparatif.csv",
        journal_out=export_path / "journal_nettoyage.txt"
    )
    controller.run()


if __name__ == "__main__":
    main()
