"""Script de test pour l'extraction de liens internes avec statistiques"""

import asyncio
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.wikipedia_api import WikipediaAPIService

async def test_links_with_stats():
    """Test d'extraction de liens internes avec statistiques"""
    print("=" * 80)
    print("TEST: Extraction de liens internes AVEC statistiques")
    print("=" * 80)
    
    # Configuration du test
    keyword = "optimisation pour les moteurs de recherche"
    language = "fr"
    max_links = 5  # Limiter à 5 pour le test (plus rapide)
    
    print(f"\nMot-clé: '{keyword}'")
    print(f"Langue: {language}")
    print(f"Nombre max de liens avec stats: {max_links}")
    print("\n" + "=" * 80)
    
    service = WikipediaAPIService(language=language)
    
    # Étape 1: Rechercher la page
    print("\n[1/3] Recherche de la page...")
    search_results = service.search_pages(keyword, limit=1)
    
    if not search_results.get("success") or not search_results.get("results"):
        print(f"❌ Aucune page trouvée pour '{keyword}'")
        return
    
    page_title = search_results["results"][0]["title"]
    page_url = search_results["results"][0]["url"]
    print(f"✅ Page trouvée: {page_title}")
    print(f"   URL: {page_url}")
    
    # Étape 2: Extraire les liens internes
    print(f"\n[2/3] Extraction des liens internes...")
    links_data = service.get_internal_links(page_title)
    
    if not links_data.get("success"):
        print(f"❌ Erreur: {links_data.get('error')}")
        return
    
    total_links = links_data.get("total_internal_links", 0)
    print(f"✅ {total_links} liens internes trouvés")
    
    # Étape 3: Récupérer les statistiques pour les N premiers liens
    print(f"\n[3/3] Récupération des statistiques pour {max_links} liens...")
    print("   (cela peut prendre ~20-30 secondes)")
    
    links_to_process = links_data["internal_links"][:max_links]
    
    for idx, link in enumerate(links_to_process, 1):
        print(f"\n   [{idx}/{max_links}] {link['linked_page_title']}")
        print(f"        Texte ancre: \"{link['anchor_text']}\"")
        
        try:
            stats = service.get_comprehensive_stats(link["linked_page_title"])
            
            if stats.get("success"):
                link["statistics"] = stats.get("statistics", {})
                link["page_info"] = stats.get("page_info", {})
                
                # Afficher les stats
                st = link["statistics"]
                pi = link["page_info"]
                
                print(f"        ✅ Statistiques récupérées:")
                print(f"           - Vues (30j): {st.get('past_month_total_views', 0):,}")
                print(f"           - Vues (365j): {st.get('past_year_total_views', 0):,}")
                print(f"           - Vues/jour: {st.get('daily_views_current_month', 0):,}")
                print(f"           - Évolution YoY: {st.get('yoy_change_percent', 0):+.1f}%")
                if pi.get("created"):
                    print(f"           - Créée le: {pi['created']}")
            else:
                link["statistics"] = None
                link["stats_error"] = stats.get("error", "Unknown error")
                print(f"        ⚠️  Erreur: {link['stats_error']}")
                
        except Exception as e:
            print(f"        ❌ Exception: {e}")
            link["statistics"] = None
            link["stats_error"] = str(e)
    
    # Résumé final
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    print(f"Page analysée: {page_title}")
    print(f"Total de liens internes: {total_links}")
    print(f"Liens avec statistiques: {max_links}")
    
    # Afficher le top 5 par popularité
    links_with_valid_stats = [
        link for link in links_to_process 
        if link.get("statistics") and link["statistics"].get("past_month_total_views")
    ]
    
    if links_with_valid_stats:
        print(f"\n📊 Top {len(links_with_valid_stats)} par popularité (vues sur 30 jours):")
        sorted_links = sorted(
            links_with_valid_stats,
            key=lambda x: x["statistics"].get("past_month_total_views", 0),
            reverse=True
        )
        
        for i, link in enumerate(sorted_links, 1):
            views = link["statistics"].get("past_month_total_views", 0)
            print(f"   {i}. {link['linked_page_title']}: {views:,} vues")
    
    print("\n" + "=" * 80)
    print("✅ Test terminé avec succès !")
    print("=" * 80)

async def main():
    """Fonction principale"""
    print("\n🧪 Test d'extraction de liens internes AVEC statistiques\n")
    
    try:
        await test_links_with_stats()
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
