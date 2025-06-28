import requests
from bs4 import BeautifulSoup
import time
import os
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin

# --- Configuration ---
# Adaptez ceci si vous ciblez la version française explicitement
BASE_URL = "https://minecraft.wiki"
# Trouvez l'URL du sitemap dans le fichier robots.txt
SITEMAP_INDEX_URL = "https://minecraft.wiki/images/sitemaps/index.xml"
# *** IMPORTANT: Personnalisez ce User-Agent ! ***
USER_AGENT = "BotScrapingWikiMinecraftForPersonnaluse (Personnal use ; contact: bennostal@gmail.com)"
# Délai en secondes entre les requêtes pour être respectueux
DELAY_BETWEEN_REQUESTS = 2
# Dossier où sauvegarder les fichiers texte extraits
OUTPUT_DIR = "wiki_content"
# *** TRÈS IMPORTANT: Trouvez le bon sélecteur CSS pour la zone de contenu principal ***
# Inspectez une page article du wiki avec les outils de développement (F12)
# Cherchez le conteneur principal du texte (souvent <main>, <article>, ou une div avec un ID/classe spécifique)
# '.mw-parser-output' est un sélecteur fréquent sur les wikis MediaWiki, mais VÉRIFIEZ !
CONTENT_SELECTOR = ".mw-parser-output"
# Chemins à ignorer (basé sur robots.txt)
DISALLOWED_PATTERNS = [
    "/w/Property:", "/w/File:", "/w/User:", "/w/Special:",
    "/api.php", "/cdn-cgi/", "/cors/", "/geoip", "/rest_v1/", "/rest.php/", "/tags/",
    # Aussi ignorer les pages non-articles si possible (ex: Catégories, Modèles)
    "/w/Category:", "/w/Template:", "/w/Help:", "/w/Portail:"
    # Adaptez pour le français si nécessaire: "/w/Catégorie:", "/w/Modèle:", etc.
]
# Paramètres d'URL à ignorer
DISALLOWED_PARAMS = [
    "action=", "oldid=", "diff=", "search=", "printable=", "uselang=", "useskin=",
    "redirect=", "variant=", "veaction=", "filefrom=", "fileuntil=", "navbox=",
    "pageuntil=", "pagefrom=", "curid=", "section="
]

# --- Fonctions Utiles ---

def is_disallowed(url):
    """Vérifie si une URL est interdite par robots.txt ou nos règles."""
    parsed_url = urlparse(url)
    path = parsed_url.path
    query = parsed_url.query

    # Vérifier les chemins interdits
    for pattern in DISALLOWED_PATTERNS:
        # Gérer les %3A encodages si présents dans pattern (bien que non idéal ici)
        if pattern.replace('%3A', ':').lower() in path.lower():
            return True

    # Vérifier les paramètres interdits
    if query:
        for param in DISALLOWED_PARAMS:
            if param.lower() in query.lower():
                return True

    # Ajouter d'autres vérifications si nécessaire (ex: ignorer les .png, .jpg)
    if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.css', '.js')):
        return True

    # Si aucun interdit trouvé, l'URL est autorisée
    return False

def fetch_url(url, headers):
    """Télécharge le contenu d'une URL avec gestion des erreurs."""
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Lève une exception pour les erreurs HTTP (4xx, 5xx)
        # Vérifier le type de contenu si possible (optionnel)
        # if 'text/html' not in response.headers.get('Content-Type', ''):
        #     print(f"  -> Ignoré (pas HTML): {url}")
        #     return None
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"  -> Erreur lors du téléchargement de {url}: {e}")
        return None

def extract_clean_content(html_content, selector):
    """Parse le HTML, extrait le contenu principal et le nettoie (basique)."""
    if not html_content:
        return None

    try:
        soup = BeautifulSoup(html_content, 'lxml') # Utilise le parser lxml
        content_area = soup.select_one(selector)

        if not content_area:
            print(f"  -> Avertissement: Sélecteur '{selector}' non trouvé.")
            return None

        # --- Nettoyage (à adapter/améliorer !) ---
        # Supprimer les éléments non désirés à l'intérieur de la zone de contenu
        # Exemples: tables des matières, boîtes d'info, bandeaux de navigation internes
        elements_to_remove_selectors = [
            '.toc',             # Table des matières standard
            '.infobox',         # Boîtes d'information
            '.navbox',          # Bandeaux de navigation en bas
            '.metadata',        # Boîtes de métadonnées, de maintenance
            '.gallery',         # Galeries d'images
            '#siteSub',         # "De Wiki..."
            '#jump-to-nav',     # Liens "Aller à la navigation/recherche"
            '.mw-editsection',  # Liens "[modifier]"
            '.noprint',         # Éléments non imprimables
            'figure',           # Peut contenir des images et légendes non textuelles
            'table.wikitable'   # Les tables peuvent être utiles ou non, à décider
        ]
        for remove_selector in elements_to_remove_selectors:
            for element in content_area.select(remove_selector):
                element.decompose() # Supprime l'élément et son contenu

        # Obtenir le texte, utiliser \n comme séparateur pour garder les sauts de ligne
        # strip=True enlève les espaces superflus au début/fin de chaque ligne
        text = content_area.get_text(separator='\n', strip=True)

        # Nettoyages supplémentaires possibles avec regex (exemples) :
        # text = re.sub(r'\n{3,}', '\n\n', text) # Remplacer 3+ sauts de ligne par 2
        # text = re.sub(r'\[\d+\]', '', text) # Enlever les citations type [1], [2]

        return text.strip() # Enlever espaces début/fin du texte complet

    except Exception as e:
        print(f"  -> Erreur lors de l'extraction/nettoyage: {e}")
        return None

def get_sitemap_urls(sitemap_index_url, headers):
    """Récupère toutes les URLs des sitemaps individuels à partir de l'index."""
    print(f"Fetching sitemap index: {sitemap_index_url}")
    index_content = fetch_url(sitemap_index_url, headers)
    if not index_content:
        return []

    sitemap_urls = []
    try:
        root = ET.fromstring(index_content)
        # Les namespaces XML peuvent varier, il faut parfois les gérer explicitement
        namespaces = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        for sitemap in root.findall('sitemap:sitemap', namespaces):
            loc = sitemap.find('sitemap:loc', namespaces)
            if loc is not None and loc.text:
                sitemap_urls.append(loc.text)
    except ET.ParseError as e:
        print(f"  -> Erreur parsing sitemap index XML: {e}")
    print(f"Found {len(sitemap_urls)} sitemaps in index.")
    return sitemap_urls

def get_article_urls_from_sitemaps(sitemap_urls, headers):
    """Récupère toutes les URLs d'articles à partir des sitemaps individuels."""
    all_article_urls = set()
    total_sitemaps = len(sitemap_urls)
    for i, sitemap_url in enumerate(sitemap_urls):
        print(f"Processing sitemap {i+1}/{total_sitemaps}: {sitemap_url}")
        sitemap_content = fetch_url(sitemap_url, headers)
        if not sitemap_content:
            time.sleep(DELAY_BETWEEN_REQUESTS) # Attendre même en cas d'erreur
            continue

        try:
            root = ET.fromstring(sitemap_content)
            namespaces = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls_in_sitemap = 0
            for url_entry in root.findall('sitemap:url', namespaces):
                loc = url_entry.find('sitemap:loc', namespaces)
                if loc is not None and loc.text:
                    article_url = loc.text
                    # Filtrer les URLs interdites
                    if not is_disallowed(article_url):
                        all_article_urls.add(article_url)
                        urls_in_sitemap += 1
            print(f"  -> Found {urls_in_sitemap} potential article URLs.")

        except ET.ParseError as e:
            print(f"  -> Erreur parsing sitemap XML: {e}")

        time.sleep(DELAY_BETWEEN_REQUESTS) # Pause après chaque fichier sitemap

    print(f"Total unique potential article URLs found: {len(all_article_urls)}")
    return list(all_article_urls)


# --- Script Principal ---

if __name__ == "__main__":
    print("Démarrage du scraper pour Minecraft Wiki...")
    headers = {'User-Agent': USER_AGENT}

    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Dossier de sortie créé: {OUTPUT_DIR}")

    """
    # 1. Obtenir les URLs des sitemaps depuis l'index
    sitemap_urls = get_sitemap_urls(SITEMAP_INDEX_URL, headers)

    if not sitemap_urls:
        print("Impossible de récupérer les URLs des sitemaps. Vérifiez SITEMAP_INDEX_URL.")
        exit()

    # 2. Obtenir toutes les URLs d'articles des sitemaps
    article_urls = get_article_urls_from_sitemaps(sitemap_urls, headers)

    if not article_urls:
        print("Aucune URL d'article valide trouvée dans les sitemaps.")
        exit()
    """
    article_urls = ["https://minecraft.wiki/w/Egg#Brown", "https://minecraft.wiki/w/Ender_Pearl"]
    print(f"\nDébut du scraping de {len(article_urls)} articles...")
    processed_count = 0
    error_count = 0



    # 3. Boucle de scraping pour chaque URL d'article
    for i, url in enumerate(article_urls):
        print(f"\n[{i+1}/{len(article_urls)}] Scraping: {url}")

        # Attendre avant la requête
        # print(f"  -> Attente de {DELAY_BETWEEN_REQUESTS} secondes...") # Décommenter pour voir l'attente
        time.sleep(DELAY_BETWEEN_REQUESTS)

        # Télécharger la page
        html = fetch_url(url, headers)
        if not html:
            error_count += 1
            continue # Passer à l'URL suivante en cas d'erreur de téléchargement

        # Extraire et nettoyer le contenu
        print(f"  -> Extraction du contenu avec le sélecteur '{CONTENT_SELECTOR}'...")
        content = extract_clean_content(html, CONTENT_SELECTOR)

        if not content:
            print("  -> Impossible d'extraire ou contenu vide.")
            error_count += 1
            continue # Passer à l'URL suivante

        # Sauvegarder le contenu dans un fichier
        # Utiliser une partie de l'URL pour nommer le fichier (nettoyée)
        try:
            filename_base = urlparse(url).path.split('/')[-1]
            # Nettoyer le nom de fichier
            filename_safe = re.sub(r'[\\/*?:"<>|]', "", filename_base)
            if not filename_safe: # Si le nom est vide après nettoyage
                filename_safe = f"article_{i+1}"
            filepath = os.path.join(OUTPUT_DIR, f"{filename_safe}.txt")

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  -> Contenu sauvegardé dans: {filepath}")
            processed_count += 1
        except Exception as e:
            print(f"  -> Erreur lors de la sauvegarde du fichier pour {url}: {e}")
            error_count += 1

    print("\n--- Scraping Terminé ---")
    print(f"Articles traités avec succès: {processed_count}")
    print(f"Erreurs rencontrées: {error_count}")
    print(f"Contenu sauvegardé dans le dossier: {OUTPUT_DIR}")