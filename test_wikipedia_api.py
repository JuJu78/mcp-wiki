"""Script de test pour l'API Wikipedia"""

import asyncio
from services.wikipedia_api import WikipediaAPIService

async def test_search():
    """Test de recherche Wikipedia"""
    print("=" * 60)
    print("TEST 1: Recherche de pages Wikipedia")
    print("=" * 60)
    
    service = WikipediaAPIService(language="en")
    
    # Test de recherche
    keyword = "python programming"
    print(f"\nRecherche pour: '{keyword}'")
    results = service.search_pages(keyword, limit=5)
    
    if results.get("success"):
        print(f"✅ Trouvé {results['total_results']} résultats")
        for i, page in enumerate(results['results'], 1):
            print(f"\n  {i}. {page['title']}")
            print(f"     URL: {page['url']}")
            print(f"     Description: {page['description'][:100]}...")
    else:
        print(f"❌ Erreur: {results.get('error')}")

async def test_stats():
    """Test de récupération des statistiques"""
    print("\n" + "=" * 60)
    print("TEST 2: Statistiques d'une page")
    print("=" * 60)
    
    service = WikipediaAPIService(language="en")
    
    page_title = "Python (programming language)"
    print(f"\nRécupération des stats pour: '{page_title}'")
    
    stats = service.get_comprehensive_stats(page_title)
    
    if stats.get("success"):
        print("✅ Statistiques récupérées avec succès\n")
        
        page_info = stats['page_info']
        statistics = stats['statistics']
        
        print(f"  Titre: {page_info['title']}")
        print(f"  URL: {page_info['url']}")
        print(f"  Créée: {page_info.get('created_formatted', 'Unknown')}")
        print(f"\n  Statistiques:")
        print(f"    - Vues dernier mois: {statistics['past_month_total_views']:,}")
        print(f"    - Vues dernière année: {statistics['past_year_total_views']:,}")
        print(f"    - Vues quotidiennes (mois actuel): {statistics['daily_views_current_month']:,}")
        print(f"    - Vues quotidiennes (même mois l'an dernier): {statistics['daily_views_last_year_same_month']:,}")
        print(f"    - Changement YoY: {statistics['yoy_change_percent']:+.1f}%")
    else:
        print(f"❌ Erreur: {stats.get('error')}")

async def test_french():
    """Test avec Wikipedia français"""
    print("\n" + "=" * 60)
    print("TEST 3: Recherche en français")
    print("=" * 60)
    
    service = WikipediaAPIService(language="fr")
    
    keyword = "intelligence artificielle"
    print(f"\nRecherche pour: '{keyword}'")
    results = service.search_pages(keyword, limit=3)
    
    if results.get("success"):
        print(f"✅ Trouvé {results['total_results']} résultats en français")
        for i, page in enumerate(results['results'], 1):
            print(f"\n  {i}. {page['title']}")
            print(f"     URL: {page['url']}")
    else:
        print(f"❌ Erreur: {results.get('error')}")

async def main():
    """Fonction principale"""
    print("\n🧪 Tests du service Wikipedia API\n")
    
    try:
        await test_search()
        await test_stats()
        await test_french()
        
        print("\n" + "=" * 60)
        print("✅ Tous les tests terminés !")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")

if __name__ == "__main__":
    asyncio.run(main())
