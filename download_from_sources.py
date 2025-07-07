#!/usr/bin/env python3
"""
Script pour télécharger et traiter les PDFs climatiques depuis sources.txt
Optimisé pour la qualité et le fact-checking
"""

import requests
import os
from pathlib import Path
import time
from urllib.parse import urlparse
import hashlib

# Configuration
SOURCES_FILE = "sources.txt"
OUTPUT_DIR = "climate_pdfs_quality"
DELAY_BETWEEN_DOWNLOADS = 2  # Respectueux
MAX_RETRIES = 3

def read_sources_file():
    """Lit le fichier sources.txt et retourne la liste des URLs."""
    try:
        with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return [url for url in urls if url.startswith('http')]
    except FileNotFoundError:
        print(f"❌ Fichier {SOURCES_FILE} non trouvé")
        return []

def get_filename_from_url(url):
    """Génère un nom de fichier approprié depuis l'URL."""
    parsed = urlparse(url)
    
    # Extraire le nom depuis l'URL
    if parsed.path.endswith('.pdf'):
        filename = os.path.basename(parsed.path)
    else:
        # Créer un nom basé sur l'URL
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"document_{url_hash}.pdf"
    
    # Nettoyer le nom de fichier
    filename = filename.replace('%20', '_').replace('%', '_')
    
    return filename

def download_pdf(url, max_retries=MAX_RETRIES):
    """Télécharge un PDF avec gestion des erreurs et des tentatives."""
    filename = get_filename_from_url(url)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Vérifier si déjà téléchargé
    if os.path.exists(filepath):
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"    ⏭️  Déjà téléchargé: {filename} ({size_mb:.1f} MB)")
        return True, filename, size_mb
    
    print(f"    📥 Téléchargement: {filename}")
    print(f"        URL: {url}")
    
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Climate Research) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=60, stream=True)
            response.raise_for_status()
            
            # Vérifier le type de contenu
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and 'application/octet-stream' not in content_type:
                print(f"        ⚠️  Type de contenu inattendu: {content_type}")
            
            # Télécharger
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Vérifier la taille
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if size_mb < 0.1:  # Moins de 100KB = probablement une erreur
                print(f"        ⚠️  Fichier très petit ({size_mb:.1f} MB), possible erreur")
                os.remove(filepath)
                return False, filename, 0
            
            print(f"        ✅ Succès: {filename} ({size_mb:.1f} MB)")
            return True, filename, size_mb
            
        except requests.exceptions.RequestException as e:
            print(f"        ❌ Tentative {attempt + 1}/{max_retries} échouée: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)  # Attendre avant la prochaine tentative
            continue
    
    print(f"        ❌ Échec définitif après {max_retries} tentatives")
    return False, filename, 0

def categorize_source(url, filename):
    """Catégorise le type de source basé sur l'URL."""
    url_lower = url.lower()
    filename_lower = filename.lower()
    
    if 'spm' in url_lower or 'summaryforpolicymakers' in filename_lower:
        return "📋 Summary for Policymakers"
    elif 'faq' in url_lower:
        return "❓ FAQ"
    elif 'srocc' in url_lower:
        return "🌊 Ocean & Cryosphere"
    elif 'srccl' in url_lower:
        return "🌱 Land Use"
    elif 'ar6' in url_lower:
        return "📊 AR6 Report"
    elif 'ar5' in url_lower:
        return "📈 AR5 Report"
    elif 'ajph' in url_lower:
        return "📰 Journal Article"
    else:
        return "📄 Document"

def main():
    """Fonction principale."""
    print("🌍 TÉLÉCHARGEMENT DES SOURCES CLIMATIQUES DE QUALITÉ")
    print("="*60)
    
    # Créer le dossier de sortie
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    # Lire les sources
    urls = read_sources_file()
    if not urls:
        print("❌ Aucune URL trouvée dans sources.txt")
        return
    
    print(f"📚 {len(urls)} sources à télécharger")
    print("-" * 60)
    
    # Statistiques
    successful_downloads = 0
    total_size_mb = 0
    categories = {}
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Traitement de la source")
        
        success, filename, size_mb = download_pdf(url)
        
        if success:
            successful_downloads += 1
            total_size_mb += size_mb
            
            # Catégoriser
            category = categorize_source(url, filename)
            categories[category] = categories.get(category, 0) + 1
        
        # Pause entre téléchargements
        if i < len(urls):
            time.sleep(DELAY_BETWEEN_DOWNLOADS)
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DU TÉLÉCHARGEMENT")
    print("="*60)
    print(f"✅ Succès: {successful_downloads}/{len(urls)} PDFs")
    print(f"💾 Taille totale: {total_size_mb:.1f} MB")
    print(f"📁 Dossier: {OUTPUT_DIR}")
    
    print(f"\n📚 RÉPARTITION PAR CATÉGORIE:")
    for category, count in sorted(categories.items()):
        print(f"   {category}: {count} document(s)")
    
    if successful_downloads > 0:
        print(f"\n🎯 PROCHAINES ÉTAPES:")
        print(f"   1. Installer: pip install pdfplumber")
        print(f"   2. Extraire le texte: python extract_pdf_text.py")
        print(f"   3. Continuer avec le pipeline RAG")
    
    print(f"\n💡 QUALITÉ ATTENDUE: EXCELLENTE")
    print(f"   • Sources officielles IPCC")
    print(f"   • Documents optimisés pour le fact-checking")
    print(f"   • Format PDF = texte propre et structuré")

if __name__ == "__main__":
    main()
