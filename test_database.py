#!/usr/bin/env python3
"""
Script de test pour vérifier le module database.py sans connexion PostgreSQL réelle
"""


def test_database_module():
    """Test l'importation et la structure du module database"""
    print("🧪 Test du module database.py")
    print("=" * 60)
    
    try:
        import database
        print("✅ Module database importé avec succès")
        
        # Vérifier que les classes et fonctions existent
        assert hasattr(database, 'DatabaseManager'), "❌ DatabaseManager manquant"
        print("✅ Classe DatabaseManager présente")
        
        assert hasattr(database, 'init_database'), "❌ Fonction init_database manquante"
        print("✅ Fonction init_database présente")
        
        # Vérifier les méthodes de DatabaseManager
        methods = ['create_tables', 'add_recette', 'search_recettes', 
                   'delete_recette', 'add_astuce_menagere', 'search_astuces', 
                   'delete_astuce']
        
        for method in methods:
            assert hasattr(database.DatabaseManager, method), f"❌ Méthode {method} manquante"
        print(f"✅ Toutes les méthodes requises sont présentes ({len(methods)} méthodes)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'importation : {e}")
        return False
    except AssertionError as e:
        print(f"❌ Test échoué : {e}")
        return False


def test_llm_module():
    """Test l'importation et la structure du module llm_french"""
    print("\n🧪 Test du module llm_french.py")
    print("=" * 60)
    
    try:
        import llm_french
        print("✅ Module llm_french importé avec succès")
        
        # Vérifier que les classes et fonctions existent
        assert hasattr(llm_french, 'FrenchLLMManager'), "❌ FrenchLLMManager manquant"
        print("✅ Classe FrenchLLMManager présente")
        
        assert hasattr(llm_french, 'RECOMMENDED_MODELS'), "❌ RECOMMENDED_MODELS manquant"
        print("✅ Dictionnaire RECOMMENDED_MODELS présent")
        
        # Vérifier les méthodes de FrenchLLMManager
        methods = ['classify_intent', 'extract_recipe_details', 
                   'format_search_results', 'generate_response']
        
        for method in methods:
            assert hasattr(llm_french.FrenchLLMManager, method), f"❌ Méthode {method} manquante"
        print(f"✅ Toutes les méthodes requises sont présentes ({len(methods)} méthodes)")
        
        # Afficher les modèles recommandés
        print("\n📋 Modèles LLM recommandés détectés :")
        for key, model in llm_french.RECOMMENDED_MODELS.items():
            print(f"  • {model['name']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'importation : {e}")
        return False
    except AssertionError as e:
        print(f"❌ Test échoué : {e}")
        return False


def test_app_module():
    """Test l'importation du module app_vie_quotidienne"""
    print("\n🧪 Test du module app_vie_quotidienne.py")
    print("=" * 60)
    
    try:
        import app_vie_quotidienne
        print("✅ Module app_vie_quotidienne importé avec succès")
        
        # Vérifier que la classe principale existe
        assert hasattr(app_vie_quotidienne, 'VieQuotidienneApp'), "❌ VieQuotidienneApp manquant"
        print("✅ Classe VieQuotidienneApp présente")
        
        # Vérifier les méthodes principales
        methods = ['handle_search', 'handle_add', 'handle_delete', 
                   'display_welcome', 'run']
        
        for method in methods:
            assert hasattr(app_vie_quotidienne.VieQuotidienneApp, method), f"❌ Méthode {method} manquante"
        print(f"✅ Toutes les méthodes requises sont présentes ({len(methods)} méthodes)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'importation : {e}")
        return False
    except AssertionError as e:
        print(f"❌ Test échoué : {e}")
        return False


def test_examples_module():
    """Test l'importation du module examples_vie_quotidienne"""
    print("\n🧪 Test du module examples_vie_quotidienne.py")
    print("=" * 60)
    
    try:
        import examples_vie_quotidienne
        print("✅ Module examples_vie_quotidienne importé avec succès")
        
        assert hasattr(examples_vie_quotidienne, 'add_sample_data'), "❌ Fonction add_sample_data manquante"
        print("✅ Fonction add_sample_data présente")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'importation : {e}")
        return False
    except AssertionError as e:
        print(f"❌ Test échoué : {e}")
        return False


def main():
    """Fonction principale de test"""
    print("\n" + "=" * 60)
    print("🚀 TESTS DES MODULES VIE QUOTIDIENNE")
    print("=" * 60)
    print("\nNote : Ces tests vérifient la structure des modules,")
    print("pas la connexion à PostgreSQL ou au LLM.\n")
    
    results = []
    
    # Test de chaque module
    results.append(("database", test_database_module()))
    results.append(("llm_french", test_llm_module()))
    results.append(("app_vie_quotidienne", test_app_module()))
    results.append(("examples_vie_quotidienne", test_examples_module()))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for module, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} : {module}.py")
    
    print("\n" + "=" * 60)
    print(f"Résultat : {passed}/{total} modules validés")
    
    if passed == total:
        print("✅ Tous les tests sont passés !")
        print("\n💡 Prochaines étapes :")
        print("  1. Installer PostgreSQL : sudo apt install postgresql")
        print("  2. Créer la base : sudo -u postgres createdb vie_quotidienne")
        print("  3. Télécharger un modèle LLM français (voir README_VIE_QUOTIDIENNE.md)")
        print("  4. Initialiser les données : python examples_vie_quotidienne.py")
        print("  5. Lancer l'application : python app_vie_quotidienne.py")
    else:
        print("❌ Certains tests ont échoué.")
    
    print("=" * 60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
