#!/usr/bin/env python3
"""
Extraction de texte propre depuis les PDFs climatiques
Alternative de haute qualité au scraping HTML
"""

import os
import glob
from pathlib import Path

# Choix de la bibliothèque PDF (décommentez celle que vous préférez)
PDF_LIBRARY = "pdfplumber"  # Plus précis pour la mise en page
# PDF_LIBRARY = "PyPDF2"    # Plus rapide, moins précis

if PDF_LIBRARY == "pdfplumber":
    try:
        import pdfplumber
    except ImportError:
        print("❌ pdfplumber non installé. Exécutez: pip install pdfplumber")
        exit(1)
elif PDF_LIBRARY == "PyPDF2":
    try:
        import PyPDF2
    except ImportError:
        print("❌ PyPDF2 non installé. Exécutez: pip install PyPDF2")
        exit(1)

INPUT_DIR = "climate_pdfs_quality"  # Dossier avec les PDFs de sources.txt
OUTPUT_DIR = "climate_facts_content_from_pdfs"

def extract_text_pdfplumber(pdf_path):
    """Extrait le texte avec pdfplumber (plus précis) - Version améliorée."""
    text_content = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            try:
                text = page.extract_text()
                if text:
                    # Nettoyer le texte de base
                    text = text.strip()
                    if text:  # Ignorer les pages vides
                        # Filtrer les sections de figures avant d'ajouter
                        filtered_text = filter_figure_sections(text)
                        if filtered_text.strip():
                            text_content.append(f"=== Page {page_num} ===\n{filtered_text}\n")
            except Exception as e:
                print(f"      ⚠️  Erreur page {page_num}: {e}")
    
    return "\n".join(text_content)

def filter_figure_sections(text):
    """Filtre les sections entières dédiées aux figures et tableaux."""
    import re
    
    # Diviser en paragraphes
    paragraphs = text.split('\n\n')
    filtered_paragraphs = []
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        
        # Ignorer les paragraphes courts (souvent des labels)
        if len(paragraph) < 20:
            continue
        
        # Ignorer les paragraphes qui sont principalement des références de figures
        figure_keywords = [
            'Figure', 'Fig.', 'Table', 'Box', 'Panel', 
            'Chart', 'Graph', 'Diagram', 'Map', 'Image'
        ]
        
        # Compter les mots liés aux figures
        words = paragraph.split()
        figure_word_count = sum(1 for word in words if any(keyword in word for keyword in figure_keywords))
        
        # Si plus de 20% des mots sont liés aux figures, ignorer
        if len(words) > 0 and figure_word_count / len(words) > 0.2:
            continue
        
        # Ignorer les paragraphes qui sont des listes de références
        if paragraph.count('(') > len(paragraph) / 20:  # Trop de parenthèses
            continue
        
        # Ignorer les paragraphes qui sont principalement des chiffres et symboles
        alpha_chars = re.sub(r'[^a-zA-Z]', '', paragraph)
        if len(alpha_chars) < len(paragraph) * 0.5:
            continue
        
        filtered_paragraphs.append(paragraph)
    
    return '\n\n'.join(filtered_paragraphs)

def extract_text_pypdf2(pdf_path):
    """Extrait le texte avec PyPDF2 (plus rapide) - Version améliorée."""
    text_content = []
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        for page_num, page in enumerate(pdf_reader.pages, 1):
            try:
                text = page.extract_text()
                if text:
                    text = text.strip()
                    if text:
                        # Filtrer les sections de figures
                        filtered_text = filter_figure_sections(text)
                        if filtered_text.strip():
                            text_content.append(f"=== Page {page_num} ===\n{filtered_text}\n")
            except Exception as e:
                print(f"      ⚠️  Erreur page {page_num}: {e}")
    
    return "\n".join(text_content)

def clean_extracted_text(text):
    """Nettoie le texte extrait des PDFs - Version améliorée pour éliminer les figures."""
    lines = text.split('\n')
    cleaned_lines = []
    
    # Patterns à ignorer (figures, tableaux, navigation)
    ignore_patterns = [
        # Figures et tableaux
        r'^\s*Figure\s+\d+',
        r'^\s*Fig\.\s+\d+',
        r'^\s*Table\s+\d+',
        r'^\s*Box\s+\d+',
        r'^\s*Panel\s+[A-Z]',
        r'^\s*\([a-z]\)\s*$',  # (a), (b), etc.
        r'^\s*[A-Z]\)\s*$',    # A), B), etc.
        
        # Navigation et références
        r'^\s*SPM-\d+',
        r'^\s*WG[I]+\s*-\s*\d+',
        r'^\s*AR6\s+',
        r'^\s*IPCC\s+',
        r'^\s*See\s+',
        r'^\s*\{[^}]*\}',      # {références}
        
        # Numéros de page et headers
        r'^\s*\d+\s*$',
        r'^\s*Page\s+\d+',
        r'^\s*Chapter\s+\d+',
        r'^\s*Summary\s+for\s+Policymakers',
        
        # Éléments de structure PDF
        r'^\s*===\s*Page\s+\d+\s*===',
        r'^\s*\.\.\.',
        r'^\s*…',
        
        # Légendes courtes et labels
        r'^\s*[a-z]\.\s*$',
        r'^\s*\d+\.\s*$',
        r'^\s*\([^)]{1,3}\)\s*$',
    ]
    
    import re
    
    for line in lines:
        line = line.strip()
        
        # Ignorer les lignes très courtes
        if len(line) < 5:
            continue
        
        # Ignorer les lignes qui matchent les patterns
        should_ignore = False
        for pattern in ignore_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                should_ignore = True
                break
        
        if should_ignore:
            continue
        
        # Ignorer les lignes qui sont principalement des caractères spéciaux
        if len(re.sub(r'[^a-zA-Z]', '', line)) < len(line) * 0.3:
            continue
        
        # Ignorer les lignes répétitives (souvent des artefacts)
        if line.count('.') > len(line) * 0.5:  # Ligne avec trop de points
            continue
        
        if line.count('_') > len(line) * 0.3:  # Ligne avec trop de underscores
            continue
        
        # Nettoyer la ligne
        line = re.sub(r'\s+', ' ', line)  # Espaces multiples -> un seul
        line = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', line)  # Caractères de contrôle
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def process_pdf(pdf_path):
    """Traite un PDF et extrait le texte propre."""
    filename = os.path.basename(pdf_path)
    print(f"    📄 Traitement: {filename}")
    
    try:
        # Extraire le texte selon la bibliothèque choisie
        if PDF_LIBRARY == "pdfplumber":
            raw_text = extract_text_pdfplumber(pdf_path)
        else:
            raw_text = extract_text_pypdf2(pdf_path)
        
        if not raw_text.strip():
            print(f"      ❌ Aucun texte extrait de {filename}")
            return False
        
        # Nettoyer le texte
        clean_text = clean_extracted_text(raw_text)
        
        # Créer le nom de fichier de sortie
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_clean.txt"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # Sauvegarder
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Source PDF: {filename}\n")
            f.write(f"Bibliothèque: {PDF_LIBRARY}\n")
            f.write("="*80 + "\n\n")
            f.write(clean_text)
        
        char_count = len(clean_text)
        word_count = len(clean_text.split())
        print(f"      ✅ Extrait: {char_count:,} caractères, {word_count:,} mots")
        print(f"      💾 Sauvé: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"      ❌ Erreur lors du traitement de {filename}: {e}")
        return False

def main():
    """Traite tous les PDFs dans le dossier d'entrée."""
    
    if not os.path.exists(INPUT_DIR):
        print(f"❌ Le dossier {INPUT_DIR} n'existe pas.")
        print("💡 Exécutez d'abord download_pdfs.py pour télécharger les PDFs.")
        return
    
    # Créer le dossier de sortie
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    # Lister les PDFs
    pdf_files = glob.glob(os.path.join(INPUT_DIR, "*.pdf"))
    
    if not pdf_files:
        print(f"❌ Aucun PDF trouvé dans {INPUT_DIR}")
        return
    
    print("📖 EXTRACTION DE TEXTE DEPUIS LES PDFs CLIMATIQUES")
    print(f"🔧 Bibliothèque utilisée: {PDF_LIBRARY}")
    print("="*60)
    
    successful = 0
    
    for pdf_path in pdf_files:
        if process_pdf(pdf_path):
            successful += 1
    
    print(f"\n{'='*60}")
    print(f"📊 RÉSULTATS: {successful}/{len(pdf_files)} PDFs traités avec succès")
    print(f"📁 Texte propre sauvé dans: {OUTPUT_DIR}")
    
    if successful > 0:
        print(f"\n💡 Le texte extrait est maintenant prêt pour le chunking !")
        print(f"   Modifiez chunking.py pour utiliser le dossier: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
