#!/usr/bin/env python3
"""
Script spécialisé pour scraper les sources scientifiques climatiques
Sources: IPCC, Environmental Defense Fund, et autres sources fiables
"""

import requests
from bs4 import BeautifulSoup
import time
import os
import re
from urllib.parse import urlparse, urljoin, urlunparse
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
        if body:
            text = body.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)
    
    # Nettoyer le texte
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)

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
