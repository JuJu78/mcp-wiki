"""Script de test pour l'extraction de liens internes Wikipedia"""

import asyncio
from services.wikipedia_api import WikipediaAPIService

async def test_internal_links_fr():
    """Test d'extraction de liens internes en français"""
    print("=" * 80)
    print("TEST: Extraction des liens internes - Page SEO (français)")
    print("=" * 80)
    
    service = WikipediaAPIService(language="fr")
    
    # Test avec la page "Optimisation pour les moteurs de recherche"
    page_title = "Optimisation pour les moteurs de recherche"
    print(f"\nPage: '{page_title}'")
    print("Extraction des liens internes...")
    
    result = service.get_internal_links(page_title)
    
    if result.get("success"):
        print(f"\n✅ Extraction réussie !")
        print(f"   Page: {result['page_title']}")
        print(f"   Nombre total de liens internes: {result['total_internal_links']}")
        
        # Afficher les 20 premiers liens
        print(f"\n📌 Premiers liens internes trouvés:\n")
        for i, link in enumerate(result['internal_links'][:20], 1):
            print(f"   {i}. \"{link['anchor_text']}\"")
            print(f"      → {link['linked_page_title']}")
            print(f"      → {link['url']}\n")
        
        # Vérifier si on trouve les liens mentionnés par l'utilisateur
        print("=" * 80)
        print("VÉRIFICATION des liens spécifiques mentionnés:")
        print("=" * 80)
        
        expected_anchors = [
            "application web",
            "Google",
            "PageRank",
            "référencement"
        ]
        
        found_links = {link['anchor_text'].lower(): link for link in result['internal_links']}
        
        for expected in expected_anchors:
            if expected.lower() in found_links:
                link = found_links[expected.lower()]
                print(f"✅ Trouvé: \"{link['anchor_text']}\" → {link['url']}")
            else:
                # Chercher dans les titres de pages liées
                found_in_title = False
                for link in result['internal_links']:
                    if expected.lower() in link['linked_page_title'].lower():
                        print(f"✅ Trouvé (dans le titre): \"{link['anchor_text']}\" → {link['url']}")
                        found_in_title = True
                        break
                
                if not found_in_title:
                    print(f"⚠️  Non trouvé: \"{expected}\"")
        
    else:
        print(f"❌ Erreur: {result.get('error')}")

async def test_internal_links_en():
    """Test d'extraction de liens internes en anglais"""
    print("\n" + "=" * 80)
    print("TEST: Extraction des liens internes - Page Python (anglais)")
    print("=" * 80)
    
    service = WikipediaAPIService(language="en")
    
    page_title = "Python (programming language)"
    print(f"\nPage: '{page_title}'")
    print("Extraction des liens internes...")
    
    result = service.get_internal_links(page_title)
    
    if result.get("success"):
        print(f"\n✅ Extraction réussie !")
        print(f"   Page: {result['page_title']}")
        print(f"   Nombre total de liens internes: {result['total_internal_links']}")
        
        # Afficher les 15 premiers liens
        print(f"\n📌 Premiers liens internes trouvés:\n")
        for i, link in enumerate(result['internal_links'][:15], 1):
            print(f"   {i}. \"{link['anchor_text']}\" → {link['linked_page_title']}")
        
    else:
        print(f"❌ Erreur: {result.get('error')}")

async def main():
    """Fonction principale"""
    print("\n🧪 Tests d'extraction de liens internes Wikipedia\n")
    
    try:
        await test_internal_links_fr()
        await test_internal_links_en()
        
        print("\n" + "=" * 80)
        print("✅ Tous les tests terminés !")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
