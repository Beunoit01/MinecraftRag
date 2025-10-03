#!/usr/bin/env python3
"""
Script pour ajouter des exemples de données dans la base de données
"""
from database import init_database


def add_sample_data(db):
    """Ajoute des données d'exemple"""
    
    print("\n📝 Ajout de recettes d'exemple...")
    
    # Recette 1 : Crêpes
    db.add_recette(
        titre="Crêpes Françaises Traditionnelles",
        description="Des crêpes légères et délicieuses, parfaites pour le goûter ou le dessert",
        ingredients="250g de farine, 4 œufs, 500ml de lait, 2 cuillères à soupe de sucre, 1 pincée de sel, 50g de beurre fondu",
        instructions="""1. Versez la farine dans un saladier avec le sel et le sucre
2. Faites un puits au centre et ajoutez les œufs
3. Mélangez doucement en incorporant progressivement le lait
4. Ajoutez le beurre fondu et mélangez bien
5. Laissez reposer la pâte 1 heure
6. Faites cuire les crêpes dans une poêle chaude légèrement huilée
7. Retournez-les quand les bords se détachent""",
        temps_preparation=15,
        temps_cuisson=20,
        nombre_portions=8,
        difficulte="facile",
        categorie="dessert"
    )
    
    # Recette 2 : Quiche Lorraine
    db.add_recette(
        titre="Quiche Lorraine",
        description="La quiche classique aux lardons et à la crème",
        ingredients="1 pâte brisée, 200g de lardons, 3 œufs, 20cl de crème fraîche, 20cl de lait, 100g de fromage râpé, sel, poivre, muscade",
        instructions="""1. Préchauffez le four à 180°C
2. Étalez la pâte dans un moule à tarte
3. Faites revenir les lardons dans une poêle
4. Battez les œufs avec la crème et le lait
5. Ajoutez sel, poivre et muscade
6. Répartissez les lardons sur la pâte
7. Versez le mélange œufs-crème
8. Parsemez de fromage râpé
9. Enfournez pour 35 minutes""",
        temps_preparation=20,
        temps_cuisson=35,
        nombre_portions=6,
        difficulte="facile",
        categorie="plat"
    )
    
    # Recette 3 : Ratatouille
    db.add_recette(
        titre="Ratatouille Provençale",
        description="Plat méditerranéen aux légumes d'été",
        ingredients="2 aubergines, 2 courgettes, 2 poivrons, 4 tomates, 1 oignon, 3 gousses d'ail, huile d'olive, herbes de Provence, sel, poivre",
        instructions="""1. Coupez tous les légumes en dés
2. Faites revenir l'oignon et l'ail dans l'huile d'olive
3. Ajoutez les aubergines et faites cuire 5 minutes
4. Ajoutez les courgettes et les poivrons
5. Incorporez les tomates
6. Assaisonnez avec les herbes, sel et poivre
7. Laissez mijoter 30 minutes à feu doux
8. Servez chaud ou froid""",
        temps_preparation=25,
        temps_cuisson=40,
        nombre_portions=4,
        difficulte="moyen",
        categorie="plat"
    )
    
    print("\n💡 Ajout d'astuces ménagères d'exemple...")
    
    # Astuce 1 : Nettoyer les vitres
    db.add_astuce_menagere(
        titre="Nettoyer les vitres sans traces",
        description="Une méthode simple et efficace pour des vitres impeccables sans produits chimiques",
        categorie="nettoyage",
        materiel_necessaire="Vinaigre blanc, eau, vaporisateur, chiffon microfibre, papier journal",
        etapes="""1. Mélangez 50% de vinaigre blanc et 50% d'eau dans un vaporisateur
2. Vaporisez généreusement sur les vitres
3. Essuyez avec un chiffon microfibre en mouvements circulaires
4. Finalisez avec du papier journal pour faire briller
5. Pour les vitres très sales, ajoutez une goutte de liquide vaisselle""",
        conseils="Nettoyez les vitres par temps nuageux pour éviter les traces de séchage rapide. Le vinaigre blanc est un dégraissant naturel et économique."
    )
    
    # Astuce 2 : Déboucher un évier
    db.add_astuce_menagere(
        titre="Déboucher un évier naturellement",
        description="Méthode écologique pour déboucher un évier sans produits chimiques",
        categorie="nettoyage",
        materiel_necessaire="Bicarbonate de soude, vinaigre blanc, eau bouillante",
        etapes="""1. Versez 3-4 cuillères à soupe de bicarbonate dans l'évier
2. Ajoutez un verre de vinaigre blanc
3. Laissez agir et mousser pendant 15-30 minutes
4. Versez une casserole d'eau bouillante
5. Répétez si nécessaire""",
        conseils="Cette méthode fonctionne aussi comme entretien préventif une fois par mois. Pour les bouchons tenaces, utilisez une ventouse avant le traitement."
    )
    
    # Astuce 3 : Organisation du frigo
    db.add_astuce_menagere(
        titre="Organiser son réfrigérateur efficacement",
        description="Conseils pour optimiser l'espace et la conservation des aliments",
        categorie="organisation",
        materiel_necessaire="Boîtes de rangement transparentes, étiquettes, film alimentaire",
        etapes="""1. Zone froide (en haut) : viandes, poissons, produits laitiers entamés
2. Zone tempérée (milieu) : produits laitiers fermés, plats cuisinés
3. Zone la moins froide (en bas) : fruits et légumes dans le bac prévu
4. Porte : condiments, boissons, œufs
5. Utilisez des boîtes transparentes pour voir le contenu
6. Étiquetez avec les dates d'ouverture
7. Faites un inventaire hebdomadaire""",
        conseils="Ne surchargez pas le frigo pour permettre la circulation de l'air froid. Rangez les produits à consommer rapidement devant."
    )
    
    # Astuce 4 : Économie d'énergie
    db.add_astuce_menagere(
        titre="Réduire sa facture d'électricité facilement",
        description="Astuces simples pour économiser de l'énergie au quotidien",
        categorie="économie",
        materiel_necessaire="Multiprises avec interrupteur, ampoules LED, programmateur",
        etapes="""1. Débranchez les appareils en veille (box, chargeurs, TV)
2. Utilisez des multiprises à interrupteur
3. Remplacez toutes les ampoules par des LED
4. Dégivrez régulièrement le congélateur
5. Lavez le linge à 30°C au lieu de 40°C
6. Utilisez le couvercle sur les casseroles
7. Programmez le chauffage pour baisser la nuit""",
        conseils="Les appareils en veille consomment 10% de votre facture. Un congélateur givré consomme 30% de plus."
    )
    
    print("\n✅ Données d'exemple ajoutées avec succès !")


def main():
    """Fonction principale"""
    print("\n🚀 AJOUT DE DONNÉES D'EXEMPLE")
    print("=" * 60)
    
    try:
        # Connexion à la base de données
        db = init_database()
        
        # Ajouter les données d'exemple
        add_sample_data(db)
        
        # Vérification
        print("\n📊 Vérification des données :")
        recettes = db.search_recettes()
        astuces = db.search_astuces()
        
        print(f"  • {len(recettes)} recettes dans la base")
        print(f"  • {len(astuces)} astuces dans la base")
        
        print("\n✅ Base de données initialisée avec succès !")
        print("\n💡 Vous pouvez maintenant lancer : python app_vie_quotidienne.py")
        
        db.close_all_connections()
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        print("\n💡 Assurez-vous que PostgreSQL est démarré et que la base 'vie_quotidienne' existe.")


if __name__ == "__main__":
    main()
