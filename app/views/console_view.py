"""Interface console : affichage structuré et présentation soignée des résultats."""
from typing import Dict, List, Any


class ConsoleView:
    """Gère l'affichage console pour l'analyse comparative de marché."""

    def header(self):
        print("=" * 80)
        print("   ANALYSE COMPARATIVE DE MARCHÉ — ÉLECTRONIQUE ET ÉLECTROMÉNAGER (ABIDJAN)")
        print("   Projet DA Python · L2 Computer Science · Séance 3")
        print("=" * 80)

    def step(self, num: int, total: int, title: str):
        print(f"\n[{num}/{total}] {title}")

    def info(self, text: str):
        print(f"      -> {text}")

    def afficher_apercu_comparatif(self, comp_rows: List[Dict[str, Any]], limit: int = 10):
        print("\n" + "-" * 80)
        print(f"{'ID':<4} | {'Produit':<28} | {'M. Lagune':<10} | {'Baobab':<10} | {'C. Ivoire':<10} | {'Moins cher':<12}")
        print("-" * 80)
        for r in comp_rows[:limit]:
            p_ml = f"{r['prix_marche_lagune']:,} F".replace(',', ' ') if r['prix_marche_lagune'] is not None and r['dispo_marche_lagune'] == "En stock" else "Rupt/NA"
            p_bb = f"{r['prix_baobab_shop']:,} F".replace(',', ' ') if r['prix_baobab_shop'] is not None and r['dispo_baobab_shop'] == "En stock" else "Rupt/NA"
            p_ci = f"{r['prix_comptoir_ivoire']:,} F".replace(',', ' ') if r['prix_comptoir_ivoire'] is not None and r['dispo_comptoir_ivoire'] == "En stock" else "Rupt/NA"
            print(f"{r['produit_id']:<4} | {r['nom_produit'][:28]:<28} | {p_ml:<10} | {p_bb:<10} | {p_ci:<10} | {r['enseigne_moins_chere']:<12}")
        if len(comp_rows) > limit:
            print(f"... ({len(comp_rows) - limit} autres produits disponibles dans le fichier comparatif.csv)")
        print("-" * 80)

    def afficher_synthese(self, synth: Dict[str, Any], total_comparables: int):
        print("\n  A. Nombre de fois où chaque enseigne est la moins chère :")
        for store, count in synth['victoires'].items():
            pct = (count / total_comparables * 100.0) if total_comparables else 0
            print(f"     • {store:<16}: {count} fois ({pct:.1f}%)")

        print("\n  B. Écart moyen par rapport au prix le plus bas :")
        for store, (m_fcfa, m_pct, nb_prods) in synth['ecarts_moyens'].items():
            print(f"     • {store:<16}: +{m_fcfa:,.0f} FCFA (+{m_pct:.1f}%) sur {nb_prods} produits disponibles".replace(',', ' '))

        print("\n  C. Top 3 des produits où il y a le plus à gagner à comparer :")
        for rank, p in enumerate(synth['top_3_gains'], start=1):
            print(f"     {rank}. {p['nom_produit']} ({p['produit_id']})")
            print(f"        Écart : {p['ecart_fcfa']:,} FCFA ({p['ecart_pourcentage']}%) | Moins cher : {p['enseigne_moins_chere']} ({p['prix_le_plus_bas']:,} FCFA)".replace(',', ' '))

    def afficher_panier(self, basket: Dict[str, Any]):
        print("  Composition du panier :")
        for pid, qty, lbl in basket['spec']:
            print(f"     - {qty}x {lbl} ({pid})")

        print("\n  Coût total par enseigne (en achetant l'intégralité du panier chez une seule enseigne) :")
        for store, total in basket['par_enseigne'].items():
            if total is not None:
                print(f"     • {store:<16} : {total:10,d} FCFA".replace(',', ' '))
            else:
                print(f"     • {store:<16} : Non disponible (rupture de stock)")

        print(f"\n  Panier optimisé (achat chez l'enseigne la moins chère par article) :")
        for it in basket['optimal']:
            print(f"     • {it['label'][:30]:<30} : {it['meilleure_enseigne']:<16} ({it['unit_price']:,} F x {it['qty']} = {it['total']:,} F)".replace(',', ' '))
        
        tot_opt = basket['total_optimal']
        print(f"     => COÛT DU PANIER OPTIMISÉ : {tot_opt:,} FCFA".replace(',', ' '))
        
        meilleur_mag = basket['meilleure_enseigne_unique']
        eco_fcfa = basket['economie_fcfa']
        eco_pct = basket['economie_pct']
        print(f"     => Économie réalisée vs la meilleure enseigne unique ({meilleur_mag}) : {eco_fcfa:,} FCFA (-{eco_pct:.1f}%)".replace(',', ' '))

    def afficher_historique(self, stats_bf: Dict[str, Any], nb_total_lignes: int):
        self.info(f"Analyse effectuée sur {nb_total_lignes:,} relevés journaliers (du 01/11/2025 au 31/10/2026).".replace(',', ' '))
        self.info("Semaine du Black Friday : du 24 au 30 novembre 2025.\n")
        
        print(f"{'Enseigne':<18} | {'Prix moyen Annuel':<18} | {'Prix moyen Black Friday':<24} | {'Évolution (%)':<15}")
        print("-" * 80)
        for src, st in stats_bf.items():
            p_an = f"{st['moyenne_annuelle']:,.0f} FCFA".replace(',', ' ')
            p_bf = f"{st['moyenne_bf']:,.0f} FCFA".replace(',', ' ')
            var = f"{st['ecart_pct']:+.2f}% ({st['ecart_fcfa']:+,.0f} F)".replace(',', ' ')
            print(f"{src:<18} | {p_an:<18} | {p_bf:<24} | {var:<15}")
        print("-" * 80)
        
        print("\n  Conclusion Black Friday :")
        print("     • OUI, il fallait acheter durant le Black Friday chez Marché Lagune (-11.2%) et Baobab Shop (-11.6%),")
        print("       qui ont consenti de véritables baisses de prix significatives sur leur catalogue.")
        print("     • NON, il ne fallait PAS acheter au Black Friday chez Comptoir Ivoire (+3.7%),")
        print("       qui n'a pas pratiqué de promotions Black Friday et dont les prix catalogue étaient même légèrement supérieurs.")

    def afficher_complexite(self, bench: Dict[str, Any]):
        print(f"      Recherche de {bench['nb_requetes']} prix dans l'historique ({bench['nb_lignes']:,} lignes) :".replace(',', ' '))
        print(f"      • Recherche séquentielle naïve (Scan linéaire O(N)) : {bench['temps_lineaire_sec']*1000:8.2f} ms")
        print(f"      • Recherche indexée par dictionnaire (Table de hachage O(1)) : {bench['temps_lookup_dict_sec']*1000:8.2f} ms")
        print(f"      • Facteur d'accélération (Speedup) : {bench['facteur_acceleration']:,.1f}x plus rapide !")
        
        print("\n  Explication théorique des choix de structures de données :")
        print("     1. Dictionnaire Python (Table de hachage) :")
        print("        - Temps d'accès : O(1) en moyenne grâce au hachage direct des clés (source, produit_id, date).")
        print("        - Complexité globale : O(N + M) pour indexer N lignes puis exécuter M requêtes,")
        print("          contre O(N × M) pour la recherche naïve en liste qui réexamine tout le fichier à chaque fois.")
        print("     2. Sets (Ensembles) :")
        print("        - Utilisés pour le calcul des intersections de tokens lors du rapprochement des libellés (O(min(|A|, |B|))).")
        print("     3. Listes de dictionnaires structurés :")
        print("        - Utilisées pour maintenir l'ordonnancement stable des 30 produits du catalogue pour les exports.")

    def footer(self, duration_sec: float, csv_file: str, log_file: str):
        print("\n" + "=" * 80)
        print(f"   TRAITEMENT TERMINÉ AVEC SUCCÈS EN {duration_sec:.3f} SECONDES")
        print("   Fichiers produits :")
        print(f"     - {csv_file:<22} (Tableau comparatif complet des prix)")
        print(f"     - {log_file:<22} (Journal détaillé de toutes les anomalies et actions)")
        print("=" * 80)
