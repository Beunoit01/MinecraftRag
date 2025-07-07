#!/usr/bin/env python3
"""
Script spécialisé pour scraper les sources scientifiques climatiques
Sources: IPCC, Environmental Defense Fund, et autres sources fiables
Version modifiée pour nettoyer le texte pour un système RAG.
"""

import requests
from bs4 import BeautifulSoup
import time
import os
import re  # <-- NOUVEAU: Importation du module pour les expressions régulières
from urllib.parse import urlparse
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
USER_AGENT = "ClimateFactChecker/1.0 (Educational research; contact: votre-email@exemple.com)"
DELAY_BETWEEN_REQUESTS = 3  # Respectueux pour les sites institutionnels
OUTPUT_DIR = "climate_facts_content"

# Sources fiables pour le fact-checking climatique
CLIMATE_SOURCES = {
    "IPCC_AR6_WG1": {
        "name": "IPCC AR6 Working Group I",
        "urls": [
            "https://www.ipcc.ch/report/ar6/wg1/chapter/summary-for-policymakers/",
            "https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-1/",
            "https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-2/",
            "https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-3/",
        ]
    },
    "IPCC_SR15": {
        "name": "IPCC Special Report 1.5°C",
        "urls": [
            "https://www.ipcc.ch/sr15/chapter/spm/",
            "https://www.ipcc.ch/sr15/chapter/chapter-1/",
            "https://www.ipcc.ch/sr15/chapter/chapter-2/",
        ]
    },
    "EDF_CLIMATE": {
        "name": "Environmental Defense Fund - Climate",
        "urls": [
            "https://www.edf.org/climate/climate-change-science",
            "https://www.edf.org/climate/what-climate-change",
            "https://www.edf.org/climate/greenhouse-gas-emissions",
        ]
    }
}


# --- NOUVELLE FONCTION DE NETTOYAGE ---
def clean_rag_text(text):
    """
    Nettoie le texte brut pour le rendre plus adapté à un système RAG.
    Supprime les éléments non pertinents comme les références de figures, les citations, etc.
    """
    # Liste de motifs regex à supprimer.
    # Chaque tuple contient le motif et par quoi le remplacer (ici, une chaîne vide).
    patterns_to_remove = [
        # Supprimer les lignes commençant par "Figure", "Table", "Box", "FAQ" etc.
        # Ex: "Figure 1.1 | The structure of the AR6 WGI Report."
        (r'^(Figure|Table|Box|FAQ|Cross-Chapter Box|Cross-Working Group Box)[\s\d.A-Za-z,|:]+.*$', ''),
        # Supprimer les références entre accolades
        # Ex: "{1.2.1, 1.3, Box 1.2, Appendix 1.A}"
        (r'\{[^{}]+\}', ''),
        # Supprimer les lignes de navigation et de méta-informations
        # Ex: "Open figure", "View", "Downloads", "Copy doi"
        (
        r'^(Open section|Downloads|Authors|Figures|How to cite|Expand all sections|View|Open figure|Copy|doi|Share on .*|Share via .*|Read more|Explore more)$',
        ''),
        # Supprimer les listes d'auteurs et d'éditeurs
        (
        r'^(Coordinatin g Lead Authors:|Lead Authors:|Contri buting Authors:|Review Editors:|Chapter Scientists:|Contributing Authors:).*$',
        ''),
        # Supprimer les instructions de citation
        (r'^This chapter should be cited as:.*$', ''),
        # Supprimer les lignes de notes de bas de page numérotées (souvent courtes)
        (r'^\d+\s+.{,100}$', ''),
        # Supprimer les lignes contenant seulement des pieds de page ou des en-têtes répétitifs
        (r'^(Executive Summary|Technical Summary|Summary for Policymakers|Frequently Asked Questions)$', ''),
    ]

    for pattern, replacement in patterns_to_remove:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE | re.IGNORECASE)

    # Supprimer les sauts de ligne excessifs (plus de 2 consécutifs)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def create_output_directory():
    """Crée le dossier de sortie s'il n'existe pas."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logger.info(f"Dossier créé: {OUTPUT_DIR}")


def clean_filename(filename):
    """Nettoie le nom de fichier pour le système de fichiers."""
    # Remplacer les caractères non autorisés
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limiter la longueur
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def extract_text_content(soup):
    """Extrait le contenu textuel principal d'une page."""
    # Supprimer les éléments indésirables
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        element.decompose()
    
    # Chercher le contenu principal
    main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
    
    if main_content:
        text = main_content.get_text(separator='\n', strip=True)
    else:
        # Fallback: prendre tout le body
        body = soup.find('body')
        text = body.get_text(separator='\n', strip=True) if body else soup.get_text(separator='\n', strip=True)

    # --- ÉTAPE DE NETTOYAGE MODIFIÉE ---

    # 1. Appliquer le nettoyage regex spécifique au RAG
    cleaned_text = clean_rag_text(text)

    # 2. Nettoyage final des lignes
    final_lines = []
    for line in cleaned_text.split('\n'):
        stripped_line = line.strip()
        # Conserver uniquement les lignes qui contiennent du texte significatif
        if stripped_line and len(stripped_line) > 25:  # Augmenter le seuil pour être plus strict
            final_lines.append(stripped_line)

    return '\n'.join(final_lines)


def scrape_url(url, source_name):
    """Scrape une URL spécifique."""
    logger.info(f"Scraping: {url}")
    
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parser le HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraire le titre
        title = soup.find('title')
        if title:
            title = title.get_text().strip()
        else:
            title = urlparse(url).path.split('/')[-1]
        
        # Extraire le contenu
        content = extract_text_content(soup)
        
        if len(content) < 100:  # Contenu trop court
            logger.warning(f"Contenu trop court pour {url}")
            return False
        
        # Créer un nom de fichier
        filename = clean_filename(f"{source_name}_{title}")
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Sauvegarder
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Source: {source_name}\n")
            f.write(f"URL: {url}\n")
            f.write(f"Titre: {title}\n")
            f.write("="*80 + "\n\n")
            f.write(content)
        
        logger.info(f"Sauvegardé: {filepath} ({len(content)} caractères)")
        return True
        
    except requests.RequestException as e:
        logger.error(f"Erreur réseau pour {url}: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur lors du scraping de {url}: {e}")
        return False


def main():
    """Fonction principale."""
    logger.info("🌍 Début du scraping des sources climatiques scientifiques")
    
    create_output_directory()
    
    total_urls = sum(len(source['urls']) for source in CLIMATE_SOURCES.values())
    processed = 0
    successful = 0
    
    for source_key, source_data in CLIMATE_SOURCES.items():
        logger.info(f"\n📚 Traitement de la source: {source_data['name']}")
        
        for url in source_data['urls']:
            processed += 1
            logger.info(f"[{processed}/{total_urls}] {url}")
            
            if scrape_url(url, source_key):
                successful += 1
            
            # Pause respectueuse
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    logger.info(f"\n✅ Scraping terminé!")
    logger.info(f"URLs traitées: {processed}")
    logger.info(f"Succès: {successful}")
    logger.info(f"Échecs: {processed - successful}")
    logger.info(f"Contenu sauvegardé dans: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
