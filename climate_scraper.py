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
import re
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


USER_AGENT = "ClimateFactChecker/1.0 (Educational research; contact: bennostal@gmail.com)"
DELAY_BETWEEN_REQUESTS = 3
OUTPUT_DIR = "climate_facts_content"

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


def clean_rag_text(text):
    patterns_to_remove = [
        (r'^(Figure|Table|Box|FAQ|Cross-Chapter Box|Cross-Working Group Box)[\s\d.A-Za-z,|:]+.*$', ''),
        (r'\{[^{}]+\}', ''),
        (
        r'^(Open section|Downloads|Authors|Figures|How to cite|Expand all sections|View|Open figure|Copy|doi|Share on .*|Share via .*|Read more|Explore more)$',
        ''),
        (
        r'^(Coordinatin g Lead Authors:|Lead Authors:|Contri buting Authors:|Review Editors:|Chapter Scientists:|Contributing Authors:).*$',
        ''),
        (r'^This chapter should be cited as:.*$', ''),
        (r'^\d+\s+.{,100}$', ''),
        (r'^(Executive Summary|Technical Summary|Summary for Policymakers|Frequently Asked Questions)$', ''),
    ]

    for pattern, replacement in patterns_to_remove:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def create_output_directory():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logger.info(f"create folder: {OUTPUT_DIR}")


def clean_filename(filename):
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def extract_text_content(soup):
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        element.decompose()

    main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
    
    if main_content:
        text = main_content.get_text(separator='\n', strip=True)
    else:
        body = soup.find('body')
        text = body.get_text(separator='\n', strip=True) if body else soup.get_text(separator='\n', strip=True)


    cleaned_text = clean_rag_text(text)

    final_lines = []
    for line in cleaned_text.split('\n'):
        stripped_line = line.strip()
        if stripped_line and len(stripped_line) > 25:
            final_lines.append(stripped_line)

    return '\n'.join(final_lines)


def scrape_url(url, source_name):
    logger.info(f"Scraping: {url}")
    
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('title')
        if title:
            title = title.get_text().strip()
        else:
            title = urlparse(url).path.split('/')[-1]

        content = extract_text_content(soup)
        
        if len(content) < 100:
            logger.warning(f"Contenu trop court pour {url}")
            return False

        filename = clean_filename(f"{source_name}_{title}")
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Source: {source_name}\n")
            f.write(f"URL: {url}\n")
            f.write(f"Titre: {title}\n")
            f.write("="*80 + "\n\n")
            f.write(content)
        
        logger.info(f"Sauvegardé: {filepath} ({len(content)} caractères)")
        return True
        
    except requests.RequestException as e:
        logger.error(f"network error{url}: {e}")
        return False
    except Exception as e:
        logger.error(f"error of scrap {url}: {e}")
        return False


def main():
    
    create_output_directory()
    
    total_urls = sum(len(source['urls']) for source in CLIMATE_SOURCES.values())
    processed = 0
    successful = 0
    
    for source_key, source_data in CLIMATE_SOURCES.items():
        logger.info(f"\nsource : {source_data['name']}")
        
        for url in source_data['urls']:
            processed += 1
            logger.info(f"[{processed}/{total_urls}] {url}")
            
            if scrape_url(url, source_key):
                successful += 1

            time.sleep(DELAY_BETWEEN_REQUESTS)


if __name__ == "__main__":
    main()
