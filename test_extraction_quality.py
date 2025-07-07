#!/usr/bin/env python3
"""
Script pour tester l'extraction PDF améliorée et comparer avec l'ancienne version
"""

import os
import glob

def compare_extractions():
    """Compare l'extraction avant et après amélioration."""
    
    old_dir = "climate_facts_content_from_pdfs"
    new_dir = "climate_facts_content_from_pdfs_clean"
    
    print("🔍 COMPARAISON DES EXTRACTIONS PDF")
    print("="*60)
    
    # Créer le nouveau dossier
    os.makedirs(new_dir, exist_ok=True)
    
    # Lister les anciens fichiers
    old_files = glob.glob(os.path.join(old_dir, "*.txt"))
    
    if not old_files:
        print("❌ Aucun fichier trouvé dans l'ancienne extraction")
        return
    
    print(f"📊 {len(old_files)} fichiers à comparer")
    
    for old_file in old_files:
        filename = os.path.basename(old_file)
        
        try:
            with open(old_file, 'r', encoding='utf-8') as f:
                old_content = f.read()
            
            # Statistiques de l'ancien fichier
            old_lines = old_content.split('\n')
            old_char_count = len(old_content)
            old_word_count = len(old_content.split())
            
            # Compter les lignes suspectes (figures, etc.)
            suspicious_lines = 0
            for line in old_lines:
                line = line.strip()
                if (line.startswith('Figure') or 
                    line.startswith('Fig.') or 
                    line.startswith('Table') or
                    line.startswith('Box') or
                    len(line) < 5 or
                    line.isdigit()):
                    suspicious_lines += 1
            
            print(f"\n📄 {filename}")
            print(f"   📈 Ancien: {old_char_count:,} caractères, {old_word_count:,} mots")
            print(f"   ⚠️  Lignes suspectes: {suspicious_lines}")
            
            # Afficher un échantillon des lignes problématiques
            sample_suspicious = []
            for line in old_lines[:50]:  # Premiers 50 lignes
                line = line.strip()
                if (line.startswith('Figure') or 
                    line.startswith('Fig.') or 
                    line.startswith('Table') or
                    line.startswith('Box') or
                    (len(line) < 5 and line) or
                    line.isdigit()):
                    sample_suspicious.append(line)
                    if len(sample_suspicious) >= 3:
                        break
            
            if sample_suspicious:
                print(f"   🔍 Exemples de pollution:")
                for example in sample_suspicious:
                    print(f"      - '{example}'")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    print(f"\n💡 SOLUTION:")
    print(f"   1. Sauvegardez l'ancienne extraction: mv {old_dir} {old_dir}_backup")
    print(f"   2. Relancez l'extraction améliorée: python extract_pdf_text.py")
    print(f"   3. Comparez les résultats")

if __name__ == "__main__":
    compare_extractions()
