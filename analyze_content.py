#!/usr/bin/env python3
"""
Script pour analyser le contenu scrapé des sources climatiques
"""

import os
import glob

def analyze_scraped_content():
    """Analyse le contenu scrapé dans le dossier climate_facts_content."""
    
    content_dir = "climate_facts_content"
    
    if not os.path.exists(content_dir):
        print(f"❌ Le dossier {content_dir} n'existe pas.")
        return
    
    # Lister tous les fichiers .txt
    txt_files = glob.glob(os.path.join(content_dir, "*.txt"))
    
    if not txt_files:
        print(f"❌ Aucun fichier .txt trouvé dans {content_dir}")
        return
    
    print("🌍 ANALYSE DU CONTENU SCRAPÉ")
    print("="*60)
    
    total_chars = 0
    total_lines = 0
    
    for i, filepath in enumerate(txt_files, 1):
        filename = os.path.basename(filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Extraire les métadonnées du fichier
            source_line = lines[0] if lines else "Source: Inconnue"
            url_line = lines[1] if len(lines) > 1 else "URL: Inconnue"
            title_line = lines[2] if len(lines) > 2 else "Titre: Inconnu"
            
            source = source_line.replace("Source: ", "")
            url = url_line.replace("URL: ", "")
            title = title_line.replace("Titre: ", "")
            
            char_count = len(content)
            line_count = len(lines)
            word_count = len(content.split())
            
            total_chars += char_count
            total_lines += line_count
            
            print(f"\n📄 [{i}/{len(txt_files)}] {filename}")
            print(f"   📚 Source: {source}")
            print(f"   🔗 URL: {url[:80]}{'...' if len(url) > 80 else ''}")
            print(f"   📝 Titre: {title[:60]}{'...' if len(title) > 60 else ''}")
            print(f"   📊 Stats: {char_count:,} caractères | {line_count:,} lignes | {word_count:,} mots")
            
            # Afficher un extrait du contenu (après les métadonnées)
            content_start = content.find("="*80)
            if content_start != -1:
                actual_content = content[content_start + 82:content_start + 382]  # 300 chars
                print(f"   🔍 Extrait: {actual_content.strip()[:200]}...")
            
        except Exception as e:
            print(f"   ❌ Erreur lors de la lecture de {filename}: {e}")
    
    print("\n" + "="*60)
    print("📈 STATISTIQUES GLOBALES")
    print("="*60)
    print(f"📁 Fichiers traités: {len(txt_files)}")
    print(f"📝 Total caractères: {total_chars:,}")
    print(f"📄 Total lignes: {total_lines:,}")
    print(f"💾 Taille approximative: {total_chars / 1024 / 1024:.2f} MB")
    
    # Analyser les sources
    sources = {}
    for filepath in txt_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                source = first_line.replace("Source: ", "")
                sources[source] = sources.get(source, 0) + 1
        except:
            pass
    
    print(f"\n📚 RÉPARTITION PAR SOURCE:")
    for source, count in sources.items():
        print(f"   • {source}: {count} fichier(s)")
    
    print(f"\n✅ Analyse terminée ! Le contenu est prêt pour le chunking.")

if __name__ == "__main__":
    analyze_scraped_content()
