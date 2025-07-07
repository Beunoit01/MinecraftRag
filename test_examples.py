#!/usr/bin/env python3
"""
Exemples d'affirmations climatiques à tester avec le système de détection de fake news
"""

# Exemples d'affirmations VRAIES (basées sur la science)
TRUE_CLAIMS = [
    "Le réchauffement climatique est principalement causé par les activités humaines",
    "Les concentrations de CO2 dans l'atmosphère ont augmenté de plus de 40% depuis l'ère pré-industrielle",
    "Les températures mondiales ont augmenté d'environ 1,1°C depuis la fin du 19e siècle",
    "La fonte des glaciers et des calottes glaciaires contribue à l'élévation du niveau de la mer",
    "Les événements climatiques extrêmes deviennent plus fréquents et plus intenses"
]

# Exemples d'affirmations FAUSSES (fake news communes)
FALSE_CLAIMS = [
    "Le réchauffement climatique a cessé depuis 1998",
    "Le CO2 n'est pas un gaz à effet de serre",
    "Les modèles climatiques ne sont jamais fiables",
    "Il n'y a pas de consensus scientifique sur le changement climatique",
    "Le réchauffement climatique est entièrement naturel et cyclique",
    "L'augmentation du CO2 est bénéfique pour les plantes donc pour le climat",
    "Les volcans émettent plus de CO2 que les humains"
]

# Exemples d'affirmations PARTIELLEMENT VRAIES (nuancées)
PARTIAL_CLAIMS = [
    "Le réchauffement climatique aura quelques effets positifs dans certaines régions",
    "Les modèles climatiques ont des incertitudes",
    "Il y a eu des périodes de réchauffement naturel dans le passé",
    "L'adaptation est aussi importante que l'atténuation du changement climatique"
]

def test_claims_interactively():
    """Permet de tester les affirmations de manière interactive."""
    print("🧪 EXEMPLES D'AFFIRMATIONS À TESTER")
    print("="*50)
    
    print("\n✅ AFFIRMATIONS VRAIES:")
    for i, claim in enumerate(TRUE_CLAIMS, 1):
        print(f"{i}. {claim}")
    
    print("\n❌ FAKE NEWS COMMUNES:")
    for i, claim in enumerate(FALSE_CLAIMS, 1):
        print(f"{i}. {claim}")
    
    print("\n⚠️ AFFIRMATIONS PARTIELLEMENT VRAIES:")
    for i, claim in enumerate(PARTIAL_CLAIMS, 1):
        print(f"{i}. {claim}")
    
    print("\n" + "="*50)
    print("Copiez une de ces affirmations dans le système principal pour la tester!")

if __name__ == "__main__":
    test_claims_interactively()
