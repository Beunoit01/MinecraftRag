#!/usr/bin/env python3
"""
Application interactive de gestion de la vie quotidienne en français
avec PostgreSQL et LLM local
"""
import os
import sys
from typing import Optional
from database import DatabaseManager, init_database
from llm_french import FrenchLLMManager, print_model_recommendations


class VieQuotidienneApp:
    """
    Application principale pour gérer les recettes, astuces et routines
    en utilisant un LLM français pour interpréter les demandes
    """
    
    def __init__(self, db: DatabaseManager, llm: FrenchLLMManager):
        """
        Initialise l'application
        
        Args:
            db: Gestionnaire de base de données
            llm: Gestionnaire du LLM français
        """
        self.db = db
        self.llm = llm
        print("\n✅ Application 'Vie Quotidienne' prête !")
    
    def display_welcome(self):
        """Affiche le message de bienvenue"""
        print("\n" + "=" * 60)
        print("🏠 ASSISTANT VIE QUOTIDIENNE")
        print("=" * 60)
        print("\n👋 Bonjour ! Je suis votre assistant personnel en français.")
        print("\nVous pouvez me demander de :")
        print("  📝 Ajouter une recette, astuce, routine ou conseil")
        print("  🔍 Rechercher des informations")
        print("  🗑️  Supprimer une entrée (avec confirmation)")
        print("\n💡 Exemples de commandes :")
        print("  • 'Donne-moi une recette de crêpes'")
        print("  • 'Ajoute une recette de gâteau au chocolat'")
        print("  • 'Trouve des astuces de nettoyage'")
        print("  • 'Supprime la recette numéro 5'")
        print("\n📌 Tapez 'aide' pour plus d'informations, 'quitter' pour sortir")
        print("=" * 60 + "\n")
    
    def handle_search(self, intent: dict):
        """
        Gère les recherches dans la base de données
        
        Args:
            intent: Dictionnaire contenant l'action, le type et la requête
        """
        content_type = intent.get('type', 'RECETTE')
        query = intent.get('query', '').strip()
        
        print(f"\n🔍 Recherche de {content_type.lower()}s...")
        
        if content_type == 'RECETTE':
            results = self.db.search_recettes(query if query else None)
        elif content_type == 'ASTUCE':
            results = self.db.search_astuces(query if query else None)
        else:
            print("⚠️  Ce type de contenu n'est pas encore supporté.")
            return
        
        if not results:
            print(f"\n❌ Aucun résultat trouvé pour '{query}'")
            return
        
        # Formater et afficher les résultats
        formatted = self.llm.format_search_results(results, content_type)
        print(formatted)
        
        # Demander si l'utilisateur veut voir les détails
        if results:
            choice = input("\n💬 Voulez-vous voir les détails d'une entrée ? (numéro ou 'non') : ").strip()
            if choice.lower() not in ['non', 'n', '']:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(results):
                        self.display_details(results[idx], content_type)
                except ValueError:
                    pass
    
    def display_details(self, item: dict, item_type: str):
        """
        Affiche les détails complets d'une entrée
        
        Args:
            item: Données de l'entrée
            item_type: Type d'entrée
        """
        print("\n" + "=" * 60)
        if item_type == 'RECETTE':
            print(f"🍽️  {item.get('titre', 'Sans titre').upper()}")
            print("=" * 60)
            if item.get('description'):
                print(f"\n📝 Description: {item.get('description')}")
            
            print(f"\n🥕 Ingrédients:")
            print(item.get('ingredients', 'Non spécifié'))
            
            print(f"\n👨‍🍳 Instructions:")
            print(item.get('instructions', 'Non spécifié'))
            
            if item.get('temps_preparation') or item.get('temps_cuisson'):
                print(f"\n⏱️  Temps:")
                if item.get('temps_preparation'):
                    print(f"  • Préparation: {item.get('temps_preparation')} minutes")
                if item.get('temps_cuisson'):
                    print(f"  • Cuisson: {item.get('temps_cuisson')} minutes")
            
            if item.get('nombre_portions'):
                print(f"\n🍽️  Portions: {item.get('nombre_portions')}")
            
            if item.get('difficulte'):
                print(f"\n📊 Difficulté: {item.get('difficulte')}")
            
            if item.get('categorie'):
                print(f"📁 Catégorie: {item.get('categorie')}")
        
        elif item_type == 'ASTUCE':
            print(f"💡 {item.get('titre', 'Sans titre').upper()}")
            print("=" * 60)
            print(f"\n📝 {item.get('description', '')}")
            
            if item.get('materiel_necessaire'):
                print(f"\n🛠️  Matériel nécessaire:")
                print(item.get('materiel_necessaire'))
            
            if item.get('etapes'):
                print(f"\n📋 Étapes:")
                print(item.get('etapes'))
            
            if item.get('conseils'):
                print(f"\n💡 Conseils:")
                print(item.get('conseils'))
            
            if item.get('categorie'):
                print(f"\n📁 Catégorie: {item.get('categorie')}")
        
        print("=" * 60)
    
    def handle_add(self, intent: dict):
        """
        Gère l'ajout de nouvelles entrées
        
        Args:
            intent: Dictionnaire contenant l'action, le type et les détails
        """
        content_type = intent.get('type', 'RECETTE')
        details = intent.get('details', '')
        
        print(f"\n➕ Ajout d'une nouvelle {content_type.lower()}...")
        
        if content_type == 'RECETTE':
            self.add_recipe_interactive(details)
        elif content_type == 'ASTUCE':
            self.add_astuce_interactive(details)
        else:
            print("⚠️  Ce type de contenu n'est pas encore supporté.")
    
    def add_recipe_interactive(self, initial_text: str):
        """
        Ajoute une recette de manière interactive
        
        Args:
            initial_text: Texte initial fourni par l'utilisateur
        """
        print("\n📝 Création d'une nouvelle recette")
        print("-" * 40)
        
        # Si le texte initial contient déjà des infos, essayer de les extraire
        if len(initial_text) > 20:
            print(f"\n🔄 Analyse de votre description...")
            extracted = self.llm.extract_recipe_details(initial_text)
            
            print("\nℹ️  Informations extraites :")
            print(f"Titre: {extracted.get('titre', 'Non extrait')}")
            
            confirm = input("\n💬 Utiliser ces informations comme base ? (oui/non) : ").strip().lower()
            if confirm in ['oui', 'o', 'yes', 'y', '']:
                titre = extracted.get('titre', '')
                ingredients = extracted.get('ingredients', '')
                instructions = extracted.get('instructions', '')
            else:
                titre = ""
                ingredients = ""
                instructions = ""
        else:
            titre = ""
            ingredients = ""
            instructions = ""
        
        # Demander les informations manquantes
        if not titre:
            titre = input("\n📌 Titre de la recette : ").strip()
        
        description = input("📝 Description courte (optionnel) : ").strip()
        
        if not ingredients:
            print("\n🥕 Ingrédients (tapez 'fin' sur une ligne vide pour terminer) :")
            ingredients_list = []
            while True:
                ing = input("  • ").strip()
                if ing.lower() == 'fin' or not ing:
                    break
                ingredients_list.append(ing)
            ingredients = ", ".join(ingredients_list)
        
        if not instructions:
            print("\n👨‍🍳 Instructions (tapez 'fin' sur une ligne vide pour terminer) :")
            instructions_list = []
            step = 1
            while True:
                inst = input(f"  {step}. ").strip()
                if inst.lower() == 'fin' or not inst:
                    break
                instructions_list.append(f"{step}. {inst}")
                step += 1
            instructions = "\n".join(instructions_list)
        
        # Informations optionnelles
        temps_prep = input("\n⏱️  Temps de préparation (minutes, optionnel) : ").strip()
        temps_cuisson = input("⏱️  Temps de cuisson (minutes, optionnel) : ").strip()
        portions = input("🍽️  Nombre de portions (optionnel) : ").strip()
        difficulte = input("📊 Difficulté (facile/moyen/difficile, optionnel) : ").strip()
        categorie = input("📁 Catégorie (entrée/plat/dessert, optionnel) : ").strip()
        
        # Convertir en types appropriés
        try:
            temps_prep = int(temps_prep) if temps_prep else None
        except ValueError:
            temps_prep = None
        
        try:
            temps_cuisson = int(temps_cuisson) if temps_cuisson else None
        except ValueError:
            temps_cuisson = None
        
        try:
            portions = int(portions) if portions else None
        except ValueError:
            portions = None
        
        # Confirmation
        print("\n" + "=" * 40)
        print("📋 RÉCAPITULATIF")
        print("=" * 40)
        print(f"Titre: {titre}")
        if description:
            print(f"Description: {description}")
        print(f"Ingrédients: {ingredients[:100]}...")
        print(f"Instructions: {instructions[:100]}...")
        
        confirm = input("\n💬 Confirmer l'ajout ? (oui/non) : ").strip().lower()
        
        if confirm in ['oui', 'o', 'yes', 'y', '']:
            try:
                recipe_id = self.db.add_recette(
                    titre=titre,
                    description=description if description else None,
                    ingredients=ingredients,
                    instructions=instructions,
                    temps_preparation=temps_prep,
                    temps_cuisson=temps_cuisson,
                    nombre_portions=portions,
                    difficulte=difficulte if difficulte else None,
                    categorie=categorie if categorie else None
                )
                print(f"\n✅ Recette ajoutée avec succès ! (ID: {recipe_id})")
            except Exception as e:
                print(f"\n❌ Erreur lors de l'ajout : {e}")
        else:
            print("\n❌ Ajout annulé.")
    
    def add_astuce_interactive(self, initial_text: str):
        """
        Ajoute une astuce ménagère de manière interactive
        
        Args:
            initial_text: Texte initial fourni par l'utilisateur
        """
        print("\n📝 Création d'une nouvelle astuce ménagère")
        print("-" * 40)
        
        titre = input("\n📌 Titre de l'astuce : ").strip()
        description = input("📝 Description : ").strip()
        categorie = input("📁 Catégorie (nettoyage/organisation/économie, optionnel) : ").strip()
        materiel = input("🛠️  Matériel nécessaire (optionnel) : ").strip()
        
        print("\n📋 Étapes (tapez 'fin' sur une ligne vide pour terminer) :")
        etapes_list = []
        step = 1
        while True:
            etape = input(f"  {step}. ").strip()
            if etape.lower() == 'fin' or not etape:
                break
            etapes_list.append(f"{step}. {etape}")
            step += 1
        etapes = "\n".join(etapes_list) if etapes_list else None
        
        conseils = input("\n💡 Conseils supplémentaires (optionnel) : ").strip()
        
        # Confirmation
        print("\n" + "=" * 40)
        print("📋 RÉCAPITULATIF")
        print("=" * 40)
        print(f"Titre: {titre}")
        print(f"Description: {description[:100]}...")
        
        confirm = input("\n💬 Confirmer l'ajout ? (oui/non) : ").strip().lower()
        
        if confirm in ['oui', 'o', 'yes', 'y', '']:
            try:
                astuce_id = self.db.add_astuce_menagere(
                    titre=titre,
                    description=description,
                    categorie=categorie if categorie else None,
                    materiel_necessaire=materiel if materiel else None,
                    etapes=etapes,
                    conseils=conseils if conseils else None
                )
                print(f"\n✅ Astuce ajoutée avec succès ! (ID: {astuce_id})")
            except Exception as e:
                print(f"\n❌ Erreur lors de l'ajout : {e}")
        else:
            print("\n❌ Ajout annulé.")
    
    def handle_delete(self, intent: dict):
        """
        Gère la suppression d'entrées avec confirmation
        
        Args:
            intent: Dictionnaire contenant l'action, le type et les détails
        """
        content_type = intent.get('type', 'RECETTE')
        details = intent.get('details', '')
        
        # Extraire l'ID si présent
        import re
        id_match = re.search(r'(?:id|numéro|numero|number)[\s:]*(\d+)', details.lower())
        
        if id_match:
            item_id = int(id_match.group(1))
        else:
            item_id = input(f"\n🔢 Entrez l'ID de la {content_type.lower()} à supprimer : ").strip()
            try:
                item_id = int(item_id)
            except ValueError:
                print("❌ ID invalide.")
                return
        
        # Confirmation de sécurité
        print(f"\n⚠️  ATTENTION : Vous êtes sur le point de supprimer la {content_type.lower()} ID {item_id}")
        confirm = input("💬 Êtes-vous sûr ? Tapez 'SUPPRIMER' pour confirmer : ").strip()
        
        if confirm == 'SUPPRIMER':
            if content_type == 'RECETTE':
                success = self.db.delete_recette(item_id)
            elif content_type == 'ASTUCE':
                success = self.db.delete_astuce(item_id)
            else:
                print("⚠️  Ce type de contenu n'est pas encore supporté.")
                return
            
            if success:
                print(f"\n✅ {content_type.capitalize()} supprimée avec succès !")
            else:
                print(f"\n❌ Impossible de supprimer la {content_type.lower()}.")
        else:
            print("\n❌ Suppression annulée (vous deviez taper exactement 'SUPPRIMER').")
    
    def display_help(self):
        """Affiche l'aide"""
        print("\n" + "=" * 60)
        print("📚 AIDE - COMMENT UTILISER L'APPLICATION")
        print("=" * 60)
        print("\n🔍 RECHERCHER :")
        print("  • 'Donne-moi une recette de crêpes'")
        print("  • 'Trouve des astuces de nettoyage'")
        print("  • 'Cherche des recettes de desserts'")
        print("\n➕ AJOUTER :")
        print("  • 'Ajoute une recette de gâteau'")
        print("  • 'Crée une astuce pour nettoyer les vitres'")
        print("  • 'Nouvelle recette : ...'")
        print("\n🗑️  SUPPRIMER :")
        print("  • 'Supprime la recette numéro 5'")
        print("  • 'Efface l'astuce ID 3'")
        print("\n💡 CONSEILS :")
        print("  • Parlez naturellement en français")
        print("  • Soyez précis dans vos demandes")
        print("  • Utilisez 'quitter' pour sortir de l'application")
        print("=" * 60 + "\n")
    
    def process_command(self, user_input: str):
        """
        Traite une commande utilisateur
        
        Args:
            user_input: Commande en français
        """
        # Commandes spéciales
        if user_input.lower() in ['aide', 'help', '?']:
            self.display_help()
            return
        
        if user_input.lower() in ['quitter', 'exit', 'quit', 'q']:
            print("\n👋 Au revoir ! À bientôt !\n")
            sys.exit(0)
        
        # Analyser l'intention avec le LLM
        print("\n🤔 Analyse de votre demande...")
        intent = self.llm.classify_intent(user_input)
        
        action = intent.get('action', 'RECHERCHER')
        
        # Dispatcher vers la bonne fonction
        if action == 'RECHERCHER':
            self.handle_search(intent)
        elif action == 'AJOUTER':
            self.handle_add(intent)
        elif action == 'SUPPRIMER':
            self.handle_delete(intent)
        else:
            print("❌ Je n'ai pas compris votre demande. Tapez 'aide' pour plus d'informations.")
    
    def run(self):
        """Lance la boucle principale de l'application"""
        self.display_welcome()
        
        while True:
            try:
                user_input = input("\n💬 Votre demande : ").strip()
                
                if not user_input:
                    continue
                
                self.process_command(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Au revoir !\n")
                break
            except Exception as e:
                print(f"\n❌ Erreur inattendue : {e}")
                print("Tapez 'aide' pour obtenir de l'assistance.\n")


def main():
    """Fonction principale"""
    print("\n🚀 DÉMARRAGE DE L'APPLICATION VIE QUOTIDIENNE")
    print("=" * 60)
    
    # Configuration de la base de données (à adapter)
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'database': os.getenv('DB_NAME', 'vie_quotidienne'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    }
    
    # Chemin du modèle LLM (à adapter selon votre configuration)
    MODEL_PATH = os.getenv('LLM_MODEL_PATH', './models/mistral-7b-instruct-v0.2.Q4_K_M.gguf')
    
    # Vérifier si le modèle existe
    if not os.path.exists(MODEL_PATH):
        print(f"\n⚠️  ATTENTION : Le modèle LLM n'a pas été trouvé à : {MODEL_PATH}")
        print("\n💡 Pour utiliser cette application, vous devez télécharger un modèle LLM français.")
        print_model_recommendations()
        print("\n📝 Ensuite, mettez à jour la variable MODEL_PATH dans ce script")
        print("   ou définissez la variable d'environnement LLM_MODEL_PATH\n")
        
        choice = input("❓ Voulez-vous continuer en mode démonstration (sans LLM) ? (oui/non) : ").strip().lower()
        if choice not in ['oui', 'o', 'yes', 'y']:
            print("\n👋 Au revoir !\n")
            return
        
        print("\n⚠️  Mode démonstration : les fonctionnalités LLM seront limitées.")
        llm = None
    else:
        # Charger le LLM
        try:
            llm = FrenchLLMManager(MODEL_PATH, n_gpu_layers=0)
        except Exception as e:
            print(f"\n❌ Erreur lors du chargement du LLM : {e}")
            print("Passage en mode démonstration...")
            llm = None
    
    # Initialiser la base de données
    try:
        print(f"\n🔄 Connexion à PostgreSQL ({DB_CONFIG['host']}:{DB_CONFIG['port']})...")
        db = init_database(**DB_CONFIG)
    except Exception as e:
        print(f"\n❌ Impossible de se connecter à PostgreSQL : {e}")
        print("\n💡 Assurez-vous que :")
        print("  1. PostgreSQL est installé et démarré")
        print("  2. La base de données 'vie_quotidienne' existe")
        print("  3. Les identifiants de connexion sont corrects")
        print("\n📚 Commandes utiles PostgreSQL :")
        print("  • Créer la base : createdb vie_quotidienne")
        print("  • Vérifier le statut : sudo systemctl status postgresql")
        print("  • Démarrer le service : sudo systemctl start postgresql\n")
        return
    
    # Créer l'instance de l'application avec un LLM mock si nécessaire
    if llm is None:
        # Mode démonstration : créer un mock
        from llm_french import FrenchLLMManager
        class MockLLM:
            def classify_intent(self, user_input):
                # Classification simple par mots-clés
                user_lower = user_input.lower()
                if any(word in user_lower for word in ['ajoute', 'ajouter', 'créer']):
                    action = 'AJOUTER'
                elif any(word in user_lower for word in ['supprime', 'supprimer', 'efface']):
                    action = 'SUPPRIMER'
                else:
                    action = 'RECHERCHER'
                
                if any(word in user_lower for word in ['recette', 'cuisine', 'plat']):
                    content_type = 'RECETTE'
                elif any(word in user_lower for word in ['astuce', 'ménage']):
                    content_type = 'ASTUCE'
                else:
                    content_type = 'RECETTE'
                
                return {'action': action, 'type': content_type, 'query': user_input, 'details': user_input}
            
            def extract_recipe_details(self, user_input):
                return {
                    'titre': 'Nouvelle recette',
                    'description': user_input[:200],
                    'ingredients': 'À définir',
                    'instructions': user_input,
                    'temps_preparation': None,
                    'temps_cuisson': None,
                    'nombre_portions': None,
                    'difficulte': 'moyen',
                    'categorie': 'plat'
                }
            
            def format_search_results(self, results, result_type):
                if not results:
                    return "Aucun résultat trouvé."
                formatted = f"\n📋 {len(results)} résultat(s) :\n\n"
                for i, item in enumerate(results[:5], 1):
                    formatted += f"{i}. {item.get('titre', 'Sans titre')} (ID: {item.get('id')})\n"
                return formatted
        
        llm = MockLLM()
    
    app = VieQuotidienneApp(db, llm)
    
    try:
        app.run()
    finally:
        db.close_all_connections()


if __name__ == "__main__":
    main()
