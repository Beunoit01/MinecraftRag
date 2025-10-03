#!/usr/bin/env python3
"""
Script de démonstration de l'application Vie Quotidienne
Fonctionne sans connexion PostgreSQL réelle (utilise un mock)
"""


class MockDatabase:
    """Mock de la base de données pour démonstration"""
    
    def __init__(self):
        self.recettes = []
        self.astuces = []
        self.next_recette_id = 1
        self.next_astuce_id = 1
        print("✅ Mock de base de données initialisé")
    
    def create_tables(self):
        print("✅ Tables (mock) créées")
    
    def add_recette(self, titre, ingredients, instructions, **kwargs):
        recette = {
            'id': self.next_recette_id,
            'titre': titre,
            'ingredients': ingredients,
            'instructions': instructions,
            **kwargs
        }
        self.recettes.append(recette)
        recipe_id = self.next_recette_id
        self.next_recette_id += 1
        print(f"✅ Recette '{titre}' ajoutée (ID: {recipe_id})")
        return recipe_id
    
    def search_recettes(self, query=None, categorie=None):
        if not query and not categorie:
            return self.recettes
        
        results = []
        for r in self.recettes:
            if query:
                if query.lower() in r['titre'].lower() or query.lower() in r['ingredients'].lower():
                    results.append(r)
            elif categorie:
                if r.get('categorie', '').lower() == categorie.lower():
                    results.append(r)
        return results
    
    def delete_recette(self, recette_id):
        initial_len = len(self.recettes)
        self.recettes = [r for r in self.recettes if r['id'] != recette_id]
        if len(self.recettes) < initial_len:
            print(f"✅ Recette ID {recette_id} supprimée")
            return True
        return False
    
    def add_astuce_menagere(self, titre, description, **kwargs):
        astuce = {
            'id': self.next_astuce_id,
            'titre': titre,
            'description': description,
            **kwargs
        }
        self.astuces.append(astuce)
        astuce_id = self.next_astuce_id
        self.next_astuce_id += 1
        print(f"✅ Astuce '{titre}' ajoutée (ID: {astuce_id})")
        return astuce_id
    
    def search_astuces(self, query=None, categorie=None):
        if not query and not categorie:
            return self.astuces
        
        results = []
        for a in self.astuces:
            if query:
                if query.lower() in a['titre'].lower() or query.lower() in a['description'].lower():
                    results.append(a)
            elif categorie:
                if a.get('categorie', '').lower() == categorie.lower():
                    results.append(a)
        return results
    
    def delete_astuce(self, astuce_id):
        initial_len = len(self.astuces)
        self.astuces = [a for a in self.astuces if a['id'] != astuce_id]
        if len(self.astuces) < initial_len:
            print(f"✅ Astuce ID {astuce_id} supprimée")
            return True
        return False
    
    def close_all_connections(self):
        print("✅ Connexions (mock) fermées")


def demo_database_operations():
    """Démontre les opérations de base de données"""
    print("\n" + "=" * 60)
    print("📊 DÉMONSTRATION DES OPÉRATIONS DE BASE DE DONNÉES")
    print("=" * 60)
    
    db = MockDatabase()
    db.create_tables()
    
    print("\n1️⃣  AJOUT DE RECETTES")
    print("-" * 40)
    
    db.add_recette(
        titre="Crêpes Françaises",
        description="Crêpes traditionnelles légères",
        ingredients="250g farine, 4 œufs, 500ml lait, sucre, sel, beurre",
        instructions="1. Mélanger la farine et les œufs\n2. Ajouter le lait progressivement\n3. Cuire à la poêle",
        temps_preparation=15,
        temps_cuisson=20,
        nombre_portions=8,
        difficulte="facile",
        categorie="dessert"
    )
    
    db.add_recette(
        titre="Quiche Lorraine",
        description="Quiche classique aux lardons",
        ingredients="Pâte brisée, lardons, œufs, crème, fromage",
        instructions="1. Préchauffer le four\n2. Faire revenir les lardons\n3. Mélanger œufs et crème\n4. Enfourner 35 min",
        temps_preparation=20,
        temps_cuisson=35,
        nombre_portions=6,
        difficulte="facile",
        categorie="plat"
    )
    
    print("\n2️⃣  AJOUT D'ASTUCES MÉNAGÈRES")
    print("-" * 40)
    
    db.add_astuce_menagere(
        titre="Nettoyer les vitres sans traces",
        description="Méthode simple avec vinaigre blanc et eau",
        categorie="nettoyage",
        materiel_necessaire="Vinaigre blanc, eau, chiffon microfibre",
        etapes="1. Mélanger 50/50 vinaigre et eau\n2. Vaporiser\n3. Essuyer",
        conseils="Nettoyer par temps nuageux"
    )
    
    db.add_astuce_menagere(
        titre="Déboucher un évier naturellement",
        description="Solution écologique au bicarbonate",
        categorie="nettoyage",
        materiel_necessaire="Bicarbonate, vinaigre blanc, eau bouillante",
        etapes="1. Verser bicarbonate\n2. Ajouter vinaigre\n3. Laisser agir 30 min\n4. Rincer à l'eau bouillante",
        conseils="Préventif une fois par mois"
    )
    
    print("\n3️⃣  RECHERCHE DE RECETTES")
    print("-" * 40)
    
    print("\n🔍 Recherche: 'crêpes'")
    results = db.search_recettes(query="crêpes")
    for r in results:
        print(f"  • {r['titre']} (ID: {r['id']}) - {r.get('categorie', 'N/A')}")
    
    print("\n🔍 Recherche par catégorie: 'plat'")
    results = db.search_recettes(categorie="plat")
    for r in results:
        print(f"  • {r['titre']} (ID: {r['id']})")
    
    print("\n4️⃣  RECHERCHE D'ASTUCES")
    print("-" * 40)
    
    print("\n🔍 Recherche: 'nettoyage'")
    results = db.search_astuces(categorie="nettoyage")
    for a in results:
        print(f"  • {a['titre']} (ID: {a['id']})")
    
    print("\n5️⃣  AFFICHAGE DES DÉTAILS")
    print("-" * 40)
    
    recettes = db.search_recettes()
    if recettes:
        r = recettes[0]
        print(f"\n🍽️  {r['titre'].upper()}")
        print("=" * 40)
        print(f"📝 Description: {r.get('description', 'N/A')}")
        print(f"\n🥕 Ingrédients:\n{r['ingredients']}")
        print(f"\n👨‍🍳 Instructions:\n{r['instructions']}")
        if r.get('temps_preparation'):
            print(f"\n⏱️  Préparation: {r['temps_preparation']} min")
        if r.get('temps_cuisson'):
            print(f"⏱️  Cuisson: {r['temps_cuisson']} min")
        if r.get('nombre_portions'):
            print(f"🍽️  Portions: {r['nombre_portions']}")
    
    print("\n6️⃣  STATISTIQUES")
    print("-" * 40)
    print(f"📊 Total recettes: {len(db.recettes)}")
    print(f"💡 Total astuces: {len(db.astuces)}")
    
    db.close_all_connections()


def demo_llm_intent_classification():
    """Démontre la classification d'intention (sans LLM réel)"""
    print("\n" + "=" * 60)
    print("🤖 DÉMONSTRATION DE LA CLASSIFICATION D'INTENTION")
    print("=" * 60)
    
    test_queries = [
        "Donne-moi une recette de crêpes",
        "Ajoute une recette de gâteau au chocolat",
        "Trouve des astuces de nettoyage",
        "Supprime la recette numéro 5",
        "Recherche des plats faciles à faire",
        "Crée une nouvelle astuce pour les vitres"
    ]
    
    def mock_classify(query):
        """Classification simple par mots-clés"""
        q_lower = query.lower()
        
        # Action
        if any(w in q_lower for w in ['ajoute', 'ajouter', 'créer', 'crée', 'nouvelle', 'nouveau']):
            action = 'AJOUTER'
        elif any(w in q_lower for w in ['supprime', 'supprimer', 'efface', 'delete']):
            action = 'SUPPRIMER'
        else:
            action = 'RECHERCHER'
        
        # Type
        if any(w in q_lower for w in ['recette', 'cuisine', 'plat', 'gâteau', 'crêpe']):
            content_type = 'RECETTE'
        elif any(w in q_lower for w in ['astuce', 'ménage', 'nettoyage', 'vitre']):
            content_type = 'ASTUCE'
        else:
            content_type = 'CONSEIL'
        
        return {'action': action, 'type': content_type, 'query': query}
    
    print("\n📝 Exemples de requêtes et leur classification :\n")
    
    for query in test_queries:
        intent = mock_classify(query)
        print(f"💬 Requête: \"{query}\"")
        print(f"   → Action: {intent['action']}")
        print(f"   → Type: {intent['type']}")
        print()


def demo_workflow():
    """Démontre le flux de travail complet"""
    print("\n" + "=" * 60)
    print("🔄 DÉMONSTRATION DU FLUX DE TRAVAIL COMPLET")
    print("=" * 60)
    
    print("\n📌 SCÉNARIO : Utilisateur demande 'Donne-moi une recette de crêpes'")
    print("-" * 60)
    
    print("\n1. 🤔 L'utilisateur saisit sa demande en français naturel")
    user_query = "Donne-moi une recette de crêpes"
    print(f"   Input: '{user_query}'")
    
    print("\n2. 🤖 Le LLM analyse l'intention")
    print("   • Détection de l'action: RECHERCHER")
    print("   • Détection du type: RECETTE")
    print("   • Extraction du mot-clé: 'crêpes'")
    
    print("\n3. 🔍 Recherche dans PostgreSQL")
    print("   SQL: SELECT * FROM recettes WHERE titre ILIKE '%crêpes%'")
    
    print("\n4. 📋 Résultats trouvés")
    print("   • 1 résultat(s)")
    print("   • Crêpes Françaises Traditionnelles (ID: 1)")
    
    print("\n5. 💬 Formatage et affichage à l'utilisateur")
    print("   Format: Titre, description, temps de préparation")
    
    print("\n6. ✅ L'utilisateur reçoit la recette complète")
    print("=" * 60)


def demo_security():
    """Démontre les fonctionnalités de sécurité"""
    print("\n" + "=" * 60)
    print("🔒 DÉMONSTRATION DE LA SÉCURITÉ")
    print("=" * 60)
    
    print("\n📌 SUPPRESSION AVEC CONFIRMATION")
    print("-" * 60)
    print("1. L'utilisateur demande: 'Supprime la recette numéro 5'")
    print("2. Le système identifie l'action de SUPPRESSION")
    print("3. ⚠️  Un message d'avertissement s'affiche:")
    print("   'ATTENTION : Vous êtes sur le point de supprimer...'")
    print("4. L'utilisateur doit taper EXACTEMENT 'SUPPRIMER' pour confirmer")
    print("5. Si confirmation = 'SUPPRIMER' → Suppression effectuée ✅")
    print("6. Sinon → Suppression annulée ❌")
    
    print("\n💡 Cette double confirmation évite les suppressions accidentelles")


def main():
    """Fonction principale de démonstration"""
    print("\n" + "=" * 60)
    print("🚀 DÉMONSTRATION - APPLICATION VIE QUOTIDIENNE")
    print("=" * 60)
    print("\n👋 Bienvenue dans la démo de l'application !")
    print("\nCette démonstration montre les fonctionnalités sans")
    print("nécessiter PostgreSQL ou un modèle LLM installé.")
    
    # Démonstrations
    demo_database_operations()
    demo_llm_intent_classification()
    demo_workflow()
    demo_security()
    
    # Conclusion
    print("\n" + "=" * 60)
    print("🎉 FIN DE LA DÉMONSTRATION")
    print("=" * 60)
    print("\n📚 Pour utiliser l'application complète :")
    print("  1. Installez PostgreSQL")
    print("  2. Créez la base de données: createdb vie_quotidienne")
    print("  3. Téléchargez un modèle LLM français (Mistral, Vigogne)")
    print("  4. Installez les dépendances:")
    print("     pip install psycopg2-binary llama-cpp-python")
    print("  5. Ajoutez des données d'exemple:")
    print("     python examples_vie_quotidienne.py")
    print("  6. Lancez l'application:")
    print("     python app_vie_quotidienne.py")
    print("\n📖 Documentation complète: README_VIE_QUOTIDIENNE.md")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
