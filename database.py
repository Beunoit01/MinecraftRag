"""
Module de gestion de la base de données PostgreSQL pour les sujets de la vie quotidienne
"""
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
import os
from datetime import datetime

class DatabaseManager:
    """Gestionnaire de connexion et opérations PostgreSQL"""
    
    def __init__(self, host: str = "localhost", port: int = 5432, 
                 database: str = "vie_quotidienne", user: str = "postgres", 
                 password: str = "postgres"):
        """
        Initialise la connexion à la base de données PostgreSQL
        
        Args:
            host: Hôte de la base de données
            port: Port de la base de données
            database: Nom de la base de données
            user: Nom d'utilisateur
            password: Mot de passe
        """
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20,
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            if self.connection_pool:
                print(f"✅ Connexion à PostgreSQL établie (base: {database})")
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Erreur de connexion à PostgreSQL: {error}")
            raise
    
    def get_connection(self):
        """Obtient une connexion depuis le pool"""
        return self.connection_pool.getconn()
    
    def return_connection(self, connection):
        """Retourne une connexion au pool"""
        self.connection_pool.putconn(connection)
    
    def close_all_connections(self):
        """Ferme toutes les connexions"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✅ Toutes les connexions PostgreSQL fermées")
    
    def create_tables(self):
        """Crée les tables nécessaires dans la base de données"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Table des recettes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recettes (
                    id SERIAL PRIMARY KEY,
                    titre VARCHAR(255) NOT NULL,
                    description TEXT,
                    ingredients TEXT NOT NULL,
                    instructions TEXT NOT NULL,
                    temps_preparation INTEGER,  -- en minutes
                    temps_cuisson INTEGER,      -- en minutes
                    nombre_portions INTEGER,
                    difficulte VARCHAR(50),     -- facile, moyen, difficile
                    categorie VARCHAR(100),     -- entrée, plat, dessert, etc.
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des astuces ménagères
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS astuces_menageres (
                    id SERIAL PRIMARY KEY,
                    titre VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    categorie VARCHAR(100),     -- nettoyage, organisation, économie, etc.
                    materiel_necessaire TEXT,
                    etapes TEXT,
                    conseils TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des routines quotidiennes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS routines (
                    id SERIAL PRIMARY KEY,
                    titre VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    type_routine VARCHAR(50),   -- matinale, soirée, hebdomadaire, etc.
                    duree_estimee INTEGER,      -- en minutes
                    etapes TEXT NOT NULL,
                    conseils TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des conseils généraux
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conseils (
                    id SERIAL PRIMARY KEY,
                    titre VARCHAR(255) NOT NULL,
                    contenu TEXT NOT NULL,
                    categorie VARCHAR(100),     -- santé, bien-être, productivité, etc.
                    tags TEXT,                  -- mots-clés séparés par des virgules
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            connection.commit()
            print("✅ Tables créées avec succès")
            
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Erreur lors de la création des tables: {error}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.return_connection(connection)
    
    def add_recette(self, titre: str, ingredients: str, instructions: str,
                    description: str = None, temps_preparation: int = None,
                    temps_cuisson: int = None, nombre_portions: int = None,
                    difficulte: str = None, categorie: str = None) -> int:
        """Ajoute une nouvelle recette"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.execute("""
                INSERT INTO recettes (titre, description, ingredients, instructions,
                                    temps_preparation, temps_cuisson, nombre_portions,
                                    difficulte, categorie)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (titre, description, ingredients, instructions, temps_preparation,
                  temps_cuisson, nombre_portions, difficulte, categorie))
            
            recette_id = cursor.fetchone()[0]
            connection.commit()
            print(f"✅ Recette '{titre}' ajoutée avec succès (ID: {recette_id})")
            return recette_id
            
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Erreur lors de l'ajout de la recette: {error}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.return_connection(connection)
    
    def search_recettes(self, query: str = None, categorie: str = None) -> List[Dict[str, Any]]:
        """Recherche des recettes par mot-clé ou catégorie"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            if query:
                cursor.execute("""
                    SELECT * FROM recettes
                    WHERE titre ILIKE %s OR description ILIKE %s OR ingredients ILIKE %s
                    ORDER BY date_creation DESC
                """, (f"%{query}%", f"%{query}%", f"%{query}%"))
            elif categorie:
                cursor.execute("""
                    SELECT * FROM recettes
                    WHERE categorie ILIKE %s
                    ORDER BY date_creation DESC
                """, (f"%{categorie}%",))
            else:
                cursor.execute("""
                    SELECT * FROM recettes
                    ORDER BY date_creation DESC
                    LIMIT 50
                """)
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
            
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Erreur lors de la recherche de recettes: {error}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.return_connection(connection)
    
    def delete_recette(self, recette_id: int) -> bool:
        """Supprime une recette par son ID"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.execute("DELETE FROM recettes WHERE id = %s", (recette_id,))
            connection.commit()
            
            if cursor.rowcount > 0:
                print(f"✅ Recette ID {recette_id} supprimée avec succès")
                return True
            else:
                print(f"⚠️  Aucune recette trouvée avec l'ID {recette_id}")
                return False
                
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Erreur lors de la suppression de la recette: {error}")
            if connection:
                connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.return_connection(connection)
    
    def add_astuce_menagere(self, titre: str, description: str,
                           categorie: str = None, materiel_necessaire: str = None,
                           etapes: str = None, conseils: str = None) -> int:
        """Ajoute une nouvelle astuce ménagère"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.execute("""
                INSERT INTO astuces_menageres (titre, description, categorie,
                                              materiel_necessaire, etapes, conseils)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (titre, description, categorie, materiel_necessaire, etapes, conseils))
            
            astuce_id = cursor.fetchone()[0]
            connection.commit()
            print(f"✅ Astuce '{titre}' ajoutée avec succès (ID: {astuce_id})")
            return astuce_id
            
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Erreur lors de l'ajout de l'astuce: {error}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.return_connection(connection)
    
    def search_astuces(self, query: str = None, categorie: str = None) -> List[Dict[str, Any]]:
        """Recherche des astuces ménagères"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            if query:
                cursor.execute("""
                    SELECT * FROM astuces_menageres
                    WHERE titre ILIKE %s OR description ILIKE %s
                    ORDER BY date_creation DESC
                """, (f"%{query}%", f"%{query}%"))
            elif categorie:
                cursor.execute("""
                    SELECT * FROM astuces_menageres
                    WHERE categorie ILIKE %s
                    ORDER BY date_creation DESC
                """, (f"%{categorie}%",))
            else:
                cursor.execute("""
                    SELECT * FROM astuces_menageres
                    ORDER BY date_creation DESC
                    LIMIT 50
                """)
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
            
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Erreur lors de la recherche d'astuces: {error}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.return_connection(connection)
    
    def delete_astuce(self, astuce_id: int) -> bool:
        """Supprime une astuce par son ID"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.execute("DELETE FROM astuces_menageres WHERE id = %s", (astuce_id,))
            connection.commit()
            
            if cursor.rowcount > 0:
                print(f"✅ Astuce ID {astuce_id} supprimée avec succès")
                return True
            else:
                print(f"⚠️  Aucune astuce trouvée avec l'ID {astuce_id}")
                return False
                
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Erreur lors de la suppression de l'astuce: {error}")
            if connection:
                connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.return_connection(connection)


def init_database(host: str = "localhost", port: int = 5432,
                 database: str = "vie_quotidienne", user: str = "postgres",
                 password: str = "postgres") -> DatabaseManager:
    """
    Initialise la base de données et retourne le gestionnaire
    """
    db = DatabaseManager(host, port, database, user, password)
    db.create_tables()
    return db


if __name__ == "__main__":
    # Test de connexion et création des tables
    print("🔧 Initialisation de la base de données...")
    db = init_database()
    print("✅ Base de données prête à l'emploi!")
