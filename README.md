# Analyse Comparative de Marché — Électronique et Électroménager (Abidjan)

**DA Python · L2 Computer Science · Séance 3**

Application modulaire d'analyse et de comparaison des prix entre trois enseignes fictives d'Abidjan :
- **Marché Lagune** (site marchand, export CSV)
- **Baobab Shop** (application mobile, API JSON)
- **Comptoir Ivoire** (boutique physique d'Adjamé, classeur Excel `.xlsx`)

---

## 🏗️ Architecture du Projet (Pattern MVC)

Le projet est structuré selon les meilleures pratiques logicielles en séparant modèles, chargeurs, services métier, vues et contrôleur :

```text
├── config.py                      # Constantes globales, chemins et configuration
├── main.py                        # Point d'entrée léger CLI (argparse)
├── requirements.txt               # 100% Bibliothèque standard Python (>= 3.10)
├── LISEZ-MOI.md                   # Énoncé initial du projet
├── donnees/                       # Fichiers sources de données
│   ├── catalogue_reference.csv    # 30 produits de référence commune
│   ├── marche_lagune.csv          # Données Marché Lagune
│   ├── baobab_shop.json           # Données Baobab Shop
│   ├── comptoir_ivoire.xlsx       # Tarifs Comptoir Ivoire
│   └── historique_prix.csv        # 20 876 relevés journaliers
├── app/
│   ├── models/                    # Modèles de données (dataclasses)
│   │   ├── produit.py             # CatalogueProduct, StoreArticle
│   │   └── journal.py             # CleaningJournal (traçabilité des anomalies)
│   ├── loaders/                   # Ingestion multi-formats (CSV, JSON, Excel)
│   │   ├── catalogue_loader.py
│   │   ├── marche_lagune_loader.py
│   │   ├── baobab_loader.py
│   │   ├── comptoir_ivoire_loader.py
│   │   └── history_loader.py
│   ├── services/                  # Logique métier & algorithmes
│   │   ├── matching_service.py    # Normalisation textuelle et matching déterministe
│   │   ├── comparator_service.py  # Tableau comparatif, exports et synthèses
│   │   ├── basket_service.py      # Valorisation et optimisation du panier
│   │   └── history_service.py     # Analyse Black Friday et benchmark complexité O(1) vs O(N)
│   ├── views/                     # Interface utilisateur console
│   │   └── console_view.py        # Affichage structuré et soigné du rapport
│   └── controllers/               # Orchestration applicative
│       └── analysis_controller.py # Pipeline d'exécution complet
└── exports/ (ou racine)
    ├── comparatif.csv             # Tableau comparatif exporté
    └── journal_nettoyage.txt      # Journal d'audit des 94 anomalies traitées
```

---

## 🚀 Exécution du Projet

Sans aucune dépendance externe à installer, lancez simplement :

```bash
python main.py
```

### Options en ligne de commande :
```bash
python main.py --help
python main.py --data-dir "donnees" --export-dir "."
```

---

## 📊 Fonctionnalités et Résultats Clés

1. **Chargement & Nettoyage** : Dédoublonnage, correction tracée de coquilles (ex: Tecno Spark 20 à 779 000 F ramené à 77 900 F), détection des ruptures de stock et export du journal d'audit (`journal_nettoyage.txt`).
2. **Rapprochement 100% Automatisé** : Normalisation des libellés (synonymes, abréviations Go/GB, To/TB, Frigo/Réfrigérateur, DD/Disque dur) et matching par tokens.
3. **Tableau Comparatif** : Écart FCFA et % pour chaque produit disponible dans au moins deux enseignes (`comparatif.csv`).
4. **Synthèse Marché** : Baobab Shop le moins cher (9 fois), suivi de Comptoir Ivoire (8 fois) et Marché Lagune (6 fois).
5. **Panier de Rentrée** : Coût mono-enseigne vs panier optimisé multi-enseignes (économie de 6 500 FCFA vs le meilleur magasin unique).
6. **Historique & Black Friday** : Baisse réelle de -11,2% chez Marché Lagune et -11,6% chez Baobab Shop durant le Black Friday (vs +3,7% chez Comptoir Ivoire).
7. **Complexité Algorithmique** : Accélération de plus de 3 000x grâce à l'indexation par table de hachage $\mathcal{O}(1)$ comparée au parcours linéaire $\mathcal{O}(N)$.
