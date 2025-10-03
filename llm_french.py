"""
Module d'intégration du LLM français pour interpréter les demandes en langage naturel
"""
from llama_cpp import Llama
from typing import Dict, Any, Optional
import re
import json


class FrenchLLMManager:
    """
    Gestionnaire du LLM français pour interpréter les intentions utilisateur
    et interagir avec la base de données
    """
    
    def __init__(self, model_path: str, n_gpu_layers: int = 0, n_ctx: int = 4096):
        """
        Initialise le modèle LLM français
        
        Args:
            model_path: Chemin vers le modèle GGUF (Vigogne, CroissantLLM, ou Mistral-7B-Instruct)
            n_gpu_layers: Nombre de couches sur GPU (0 = CPU uniquement)
            n_ctx: Taille du contexte
        """
        print(f"🔄 Chargement du modèle LLM depuis {model_path}...")
        
        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,
            n_ctx=n_ctx,
            n_batch=512,
            verbose=False
        )
        
        print("✅ Modèle LLM chargé avec succès")
    
    def classify_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Classifie l'intention de l'utilisateur (ajouter, rechercher, supprimer)
        
        Args:
            user_input: Texte en français de l'utilisateur
            
        Returns:
            Dict avec 'action', 'type', et 'content' extraits
        """
        system_prompt = """Tu es un assistant intelligent pour gérer une base de données de vie quotidienne en français.
Ta tâche est d'analyser la demande de l'utilisateur et d'identifier :
1. L'ACTION souhaitée : 'AJOUTER', 'RECHERCHER', ou 'SUPPRIMER'
2. Le TYPE de contenu : 'RECETTE', 'ASTUCE', 'ROUTINE', ou 'CONSEIL'
3. Les DÉTAILS pertinents de la demande

Réponds UNIQUEMENT au format JSON suivant :
{
    "action": "AJOUTER|RECHERCHER|SUPPRIMER",
    "type": "RECETTE|ASTUCE|ROUTINE|CONSEIL",
    "query": "mots-clés de recherche si applicable",
    "details": "détails extraits de la demande"
}

Exemples :
- "Donne-moi une recette de crêpes" -> {"action": "RECHERCHER", "type": "RECETTE", "query": "crêpes", "details": ""}
- "Ajoute une recette de gâteau au chocolat" -> {"action": "AJOUTER", "type": "RECETTE", "query": "", "details": "gâteau au chocolat"}
- "Supprime la recette numéro 5" -> {"action": "SUPPRIMER", "type": "RECETTE", "query": "", "details": "id:5"}
"""
        
        user_prompt = f"Demande de l'utilisateur : {user_input}"
        
        # Format pour Mistral/Vigogne (prompt Llama-style)
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        output = self.llm(
            prompt,
            max_tokens=300,
            stop=["<|eot_id|>", "<|end_of_text|>"],
            temperature=0.1,
            echo=False
        )
        
        response_text = output['choices'][0]['text'].strip()
        
        # Extraire le JSON de la réponse
        try:
            # Chercher un JSON dans la réponse
            json_match = re.search(r'\{[^}]+\}', response_text)
            if json_match:
                result = json.loads(json_match.group(0))
                return result
        except json.JSONDecodeError:
            pass
        
        # Fallback : analyse simple par mots-clés
        return self._fallback_intent_classification(user_input)
    
    def _fallback_intent_classification(self, user_input: str) -> Dict[str, Any]:
        """Classification d'intention par mots-clés en cas d'échec du LLM"""
        user_lower = user_input.lower()
        
        # Détection de l'action
        if any(word in user_lower for word in ['ajoute', 'ajouter', 'créer', 'créé', 'enregistre', 'nouvelle', 'nouveau']):
            action = 'AJOUTER'
        elif any(word in user_lower for word in ['supprime', 'supprimer', 'efface', 'effacer', 'retire', 'retirer', 'enlève', 'enlever', 'delete']):
            action = 'SUPPRIMER'
        else:
            action = 'RECHERCHER'
        
        # Détection du type
        if any(word in user_lower for word in ['recette', 'cuisine', 'plat', 'dessert', 'gâteau', 'crêpe', 'tarte']):
            content_type = 'RECETTE'
        elif any(word in user_lower for word in ['astuce', 'ménage', 'nettoyage', 'nettoyer', 'laver']):
            content_type = 'ASTUCE'
        elif any(word in user_lower for word in ['routine', 'habitude', 'quotidien']):
            content_type = 'ROUTINE'
        else:
            content_type = 'CONSEIL'
        
        return {
            'action': action,
            'type': content_type,
            'query': user_input,
            'details': user_input
        }
    
    def extract_recipe_details(self, user_input: str) -> Dict[str, Any]:
        """
        Extrait les détails d'une recette depuis la demande utilisateur
        
        Args:
            user_input: Description de la recette en français
            
        Returns:
            Dict avec titre, ingrédients, instructions, etc.
        """
        system_prompt = """Tu es un assistant culinaire qui aide à structurer des recettes.
À partir de la description de l'utilisateur, extrais les informations suivantes au format JSON :
{
    "titre": "nom de la recette",
    "description": "courte description",
    "ingredients": "liste des ingrédients séparés par des virgules",
    "instructions": "étapes de préparation",
    "temps_preparation": nombre_minutes (ou null),
    "temps_cuisson": nombre_minutes (ou null),
    "nombre_portions": nombre (ou null),
    "difficulte": "facile|moyen|difficile",
    "categorie": "entrée|plat|dessert|boisson"
}

Si une information n'est pas fournie, mets null."""
        
        user_prompt = f"Description de la recette : {user_input}"
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        output = self.llm(
            prompt,
            max_tokens=500,
            stop=["<|eot_id|>", "<|end_of_text|>"],
            temperature=0.2,
            echo=False
        )
        
        response_text = output['choices'][0]['text'].strip()
        
        try:
            # Chercher un JSON dans la réponse
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                return result
        except json.JSONDecodeError:
            pass
        
        # Fallback simple
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
    
    def format_search_results(self, results: list, result_type: str) -> str:
        """
        Formate les résultats de recherche de manière lisible en français
        
        Args:
            results: Liste de résultats de la base de données
            result_type: Type de résultat (RECETTE, ASTUCE, etc.)
            
        Returns:
            Texte formaté en français
        """
        if not results:
            return "Aucun résultat trouvé."
        
        formatted = f"\n📋 {len(results)} résultat(s) trouvé(s) :\n\n"
        
        for i, item in enumerate(results[:5], 1):  # Limiter à 5 résultats
            if result_type == 'RECETTE':
                formatted += f"🍽️  {i}. **{item.get('titre', 'Sans titre')}** (ID: {item.get('id')})\n"
                if item.get('description'):
                    formatted += f"   {item.get('description')}\n"
                if item.get('temps_preparation') or item.get('temps_cuisson'):
                    temps = []
                    if item.get('temps_preparation'):
                        temps.append(f"Préparation: {item.get('temps_preparation')} min")
                    if item.get('temps_cuisson'):
                        temps.append(f"Cuisson: {item.get('temps_cuisson')} min")
                    formatted += f"   ⏱️  {', '.join(temps)}\n"
                formatted += "\n"
            
            elif result_type == 'ASTUCE':
                formatted += f"💡 {i}. **{item.get('titre', 'Sans titre')}** (ID: {item.get('id')})\n"
                formatted += f"   {item.get('description', '')[:150]}...\n"
                if item.get('categorie'):
                    formatted += f"   📁 Catégorie: {item.get('categorie')}\n"
                formatted += "\n"
        
        if len(results) > 5:
            formatted += f"\n... et {len(results) - 5} autre(s) résultat(s).\n"
        
        return formatted
    
    def generate_response(self, context: str, user_query: str) -> str:
        """
        Génère une réponse en français basée sur le contexte et la requête
        
        Args:
            context: Contexte (résultats de recherche, confirmations, etc.)
            user_query: Question de l'utilisateur
            
        Returns:
            Réponse en français naturel
        """
        system_prompt = """Tu es un assistant personnel sympathique qui aide à gérer la vie quotidienne en français.
Réponds de manière naturelle, amicale et concise. Utilise des emojis pour rendre tes réponses plus agréables."""
        
        user_prompt = f"""Contexte : {context}

Question de l'utilisateur : {user_query}

Réponds de manière naturelle et utile."""
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        output = self.llm(
            prompt,
            max_tokens=400,
            stop=["<|eot_id|>", "<|end_of_text|>"],
            temperature=0.7,
            echo=False
        )
        
        return output['choices'][0]['text'].strip()


# Configuration recommandée pour différents modèles français
RECOMMENDED_MODELS = {
    "vigogne": {
        "name": "Vigogne-2-7B-Instruct",
        "description": "Modèle français basé sur Llama 2, optimisé pour le français",
        "url": "https://huggingface.co/bofenghuang/vigogne-2-7b-instruct",
        "gguf": "vigogne-2-7b-instruct.Q4_K_M.gguf"
    },
    "croissant": {
        "name": "CroissantLLM",
        "description": "Modèle français natif développé par des chercheurs français",
        "url": "https://huggingface.co/croissantllm/CroissantLLM",
        "gguf": "croissantllm.Q4_K_M.gguf"
    },
    "mistral": {
        "name": "Mistral-7B-Instruct",
        "description": "Excellent modèle multilingue avec bon support du français",
        "url": "https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2",
        "gguf": "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    }
}


def print_model_recommendations():
    """Affiche les recommandations de modèles LLM français"""
    print("\n🤖 MODÈLES LLM FRANÇAIS RECOMMANDÉS :")
    print("=" * 60)
    for key, model in RECOMMENDED_MODELS.items():
        print(f"\n📦 {model['name']}")
        print(f"   Description: {model['description']}")
        print(f"   URL: {model['url']}")
        print(f"   Fichier GGUF recommandé: {model['gguf']}")
    print("\n" + "=" * 60)
    print("\n💡 Pour télécharger un modèle GGUF :")
    print("   1. Visitez le lien HuggingFace ci-dessus")
    print("   2. Allez dans l'onglet 'Files and versions'")
    print("   3. Téléchargez le fichier .gguf (format Q4_K_M recommandé)")
    print("   4. Placez-le dans un dossier local et notez le chemin")
    print("\n")


if __name__ == "__main__":
    print_model_recommendations()
