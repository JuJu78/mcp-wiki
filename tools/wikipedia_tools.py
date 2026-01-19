"""Wikipedia search and statistics tools"""

import logging
from services.wikipedia_api import WikipediaAPIService

logger = logging.getLogger(__name__)

def register_wikipedia_tools(mcp):
    """Enregistre les outils de recherche et statistiques Wikipedia"""
    
    @mcp.tool()
    async def search_wikipedia_keyword(
        keyword: str,
        language: str = "en",
        max_results: int = 20,
        include_stats: bool = True,
        ctx=None
    ):
        """
        Recherche des pages Wikipedia liées à un mot-clé et récupère leurs statistiques.
        
        Cette fonction retourne une liste de pages Wikipedia pertinentes avec:
        - Le titre de la page (avec lien cliquable)
        - La date de création
        - Les vues totales du dernier mois
        - Les vues totales de l'année passée
        - Les vues quotidiennes moyennes du mois en cours
        - Les vues quotidiennes moyennes du même mois l'année dernière
        - Le changement année sur année (YoY) en pourcentage
        
        Args:
            keyword: Le terme de recherche (ex: "google", "python programming", etc.)
            language: Code de langue Wikipedia (en, fr, de, es, etc.). Défaut: "en"
            max_results: Nombre maximum de pages à retourner (1-50). Défaut: 20
            include_stats: Inclure les statistiques détaillées pour chaque page. Défaut: True
        
        Returns:
            Un dictionnaire JSON contenant:
            - success: True/False
            - keyword: Le terme recherché
            - language: La langue utilisée
            - total_results: Nombre de résultats trouvés
            - pages: Liste des pages avec liens et statistiques
        
        Exemple d'utilisation:
            Pour rechercher des pages sur "artificial intelligence" en anglais:
            search_wikipedia_keyword(keyword="artificial intelligence", language="en", max_results=10)
            
            Pour rechercher en français:
            search_wikipedia_keyword(keyword="intelligence artificielle", language="fr")
        """
        if not keyword or not str(keyword).strip():
            return {"error": "keyword is required and cannot be empty"}
        
        # Validation de la langue
        supported_languages = ["en", "fr", "de", "es", "it", "pt", "nl", "pl", "ru", "ja", "zh", "ar", "ko", "hi"]
        if language not in supported_languages:
            return {
                "error": f"Language '{language}' not supported. Supported languages: {', '.join(supported_languages)}"
            }
        
        # Validation du nombre de résultats
        if max_results < 1 or max_results > 50:
            return {"error": "max_results must be between 1 and 50"}
        
        try:
            # Créer le service Wikipedia pour la langue spécifiée
            wiki_service = WikipediaAPIService(language=language)
            
            # Rechercher les pages
            logger.info(f"Searching Wikipedia for '{keyword}' in {language}")
            search_results = wiki_service.search_pages(keyword, limit=max_results)
            
            if not search_results.get("success"):
                return search_results
            
            pages = search_results.get("results", [])
            
            if not pages:
                return {
                    "success": True,
                    "keyword": keyword,
                    "language": language,
                    "total_results": 0,
                    "pages": [],
                    "message": "No Wikipedia pages found for this keyword"
                }
            
            # Si include_stats=True, récupérer les statistiques pour chaque page
            if include_stats:
                logger.info(f"Fetching statistics for {len(pages)} pages")
                enriched_pages = []
                
                for page in pages:
                    page_title = page["title"]
                    
                    # Récupérer les statistiques complètes
                    stats = wiki_service.get_comprehensive_stats(page_title)
                    
                    if stats.get("success"):
                        page_info = stats.get("page_info", {})
                        statistics = stats.get("statistics", {})
                        
                        enriched_page = {
                            "title": page_title,
                            "url": page["url"],
                            "description": page.get("description", ""),
                            "page_created": page_info.get("created_formatted", "Unknown"),
                            "statistics": {
                                "past_month_views": statistics.get("past_month_total_views", 0),
                                "past_year_views": statistics.get("past_year_total_views", 0),
                                "daily_views_current_month": statistics.get("daily_views_current_month", 0),
                                "daily_views_last_year_month": statistics.get("daily_views_last_year_same_month", 0),
                                "yoy_change_percent": statistics.get("yoy_change_percent", 0)
                            }
                        }
                    else:
                        # Si les stats ne sont pas disponibles, retourner la page sans stats
                        enriched_page = {
                            "title": page_title,
                            "url": page["url"],
                            "description": page.get("description", ""),
                            "page_created": "Unknown",
                            "statistics": None,
                            "error": "Statistics not available for this page"
                        }
                    
                    enriched_pages.append(enriched_page)
                
                return {
                    "success": True,
                    "keyword": keyword,
                    "language": language,
                    "total_results": len(enriched_pages),
                    "pages": enriched_pages
                }
            else:
                # Retourner uniquement les résultats de recherche sans statistiques
                return {
                    "success": True,
                    "keyword": keyword,
                    "language": language,
                    "total_results": len(pages),
                    "pages": pages
                }
            
        except Exception as e:
            logger.error(f"search_wikipedia_keyword error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def get_wikipedia_page_stats(
        page_title: str,
        language: str = "en",
        ctx=None
    ):
        """
        Récupère les statistiques détaillées pour une page Wikipedia spécifique.
        
        Args:
            page_title: Titre exact de la page Wikipedia
            language: Code de langue Wikipedia (en, fr, de, es, etc.). Défaut: "en"
        
        Returns:
            Statistiques complètes de la page incluant:
            - Informations de base (titre, URL, date de création)
            - Vues du dernier mois
            - Vues de l'année passée
            - Vues quotidiennes moyennes
            - Changement YoY
        """
        if not page_title or not str(page_title).strip():
            return {"error": "page_title is required and cannot be empty"}
        
        try:
            wiki_service = WikipediaAPIService(language=language)
            stats = wiki_service.get_comprehensive_stats(page_title)
            
            return stats
            
        except Exception as e:
            logger.error(f"get_wikipedia_page_stats error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def get_wikipedia_internal_links(
        keyword: str,
        language: str = "fr",
        include_stats: bool = False,
        max_links_with_stats: int = 20,
        max_internal_links: int = 200,
        ctx=None
    ):
        """
        Récupère tous les liens internes (ancres) d'une page Wikipedia à partir d'un mot-clé.
        
        Cette fonction trouve d'abord la page Wikipedia correspondant au mot-clé,
        puis extrait tous les liens internes (ancres) présents dans le contenu principal
        de la page. Ces liens pointent vers d'autres pages Wikipedia.
        
        NOUVEAU : Peut également récupérer les statistiques de vues pour chaque page liée !
        
        Args:
            keyword: Le terme de recherche pour trouver la page Wikipedia
            language: Code de langue Wikipedia (en, fr, de, es, etc.). Défaut: "fr"
            include_stats: Si True, récupère les statistiques de vues pour chaque lien. Défaut: False
            max_links_with_stats: Nombre maximum de liens pour lesquels récupérer les stats (1-100). Défaut: 20
        
        Returns:
            Un dictionnaire JSON contenant:
            - success: True/False
            - page_title: Titre de la page trouvée
            - page_url: URL de la page
            - total_internal_links: Nombre total de liens internes
            - internal_links: Liste des liens avec:
              - anchor_text: Texte de l'ancre (le texte cliquable)
              - linked_page_title: Titre de la page liée
              - url: URL complète vers la page liée
              - statistics: (si include_stats=True) Statistiques de vues de la page liée:
                  - past_month_views: Vues du dernier mois
                  - past_year_views: Vues de l'année passée
                  - daily_views_current_month: Vues quotidiennes moyennes (mois actuel)
                  - yoy_change_percent: Changement année sur année (%)
        
        Exemple d'utilisation:
            # Sans statistiques (rapide)
            get_wikipedia_internal_links(keyword="SEO", language="fr")
            
            # Avec statistiques pour les 20 premiers liens (prend ~20 secondes)
            get_wikipedia_internal_links(keyword="SEO", language="fr", include_stats=True, max_links_with_stats=20)
            
            # Avec statistiques pour les 50 premiers liens (prend ~50 secondes)
            get_wikipedia_internal_links(keyword="SEO", language="fr", include_stats=True, max_links_with_stats=50)
        """
        if not keyword or not str(keyword).strip():
            return {"error": "keyword is required and cannot be empty"}
        
        # Valider max_links_with_stats
        if max_links_with_stats < 1 or max_links_with_stats > 100:
            max_links_with_stats = 20

        # Valider max_internal_links
        if max_internal_links < 1 or max_internal_links > 2000:
            max_internal_links = 200
        
        try:
            # Créer le service Wikipedia pour la langue spécifiée
            wiki_service = WikipediaAPIService(language=language)
            
            # D'abord, rechercher la page correspondant au mot-clé
            logger.info(f"Searching Wikipedia for '{keyword}' in {language}")
            search_results = wiki_service.search_pages(keyword, limit=1)
            
            if not search_results.get("success") or not search_results.get("results"):
                return {
                    "success": False,
                    "error": f"No Wikipedia page found for keyword '{keyword}'"
                }
            
            # Prendre la première page trouvée
            first_page = search_results["results"][0]
            page_title = first_page["title"]
            page_url = first_page["url"]
            
            logger.info(f"Found page: {page_title}")
            logger.info(f"Extracting internal links...")
            
            # Extraire les liens internes de cette page
            links_data = wiki_service.get_internal_links(page_title, max_links=max_internal_links)
            
            if not links_data.get("success"):
                return links_data
            
            # Si include_stats est activé, récupérer les statistiques pour chaque lien
            if include_stats and links_data.get("internal_links"):
                logger.info(f"Fetching statistics for up to {max_links_with_stats} linked pages...")
                
                # Limiter le nombre de liens pour lesquels on récupère les stats
                links_to_process = links_data["internal_links"][:max_links_with_stats]
                
                # Récupérer les stats pour chaque lien de manière séquentielle
                # (pour éviter de surcharger les APIs Wikipedia)
                for idx, link in enumerate(links_to_process, 1):
                    try:
                        logger.info(f"Fetching stats for link {idx}/{len(links_to_process)}: {link['linked_page_title']}")
                        stats = wiki_service.get_comprehensive_stats(link["linked_page_title"])
                        
                        if stats.get("success"):
                            link["statistics"] = stats.get("statistics", {})
                            link["page_info"] = stats.get("page_info", {})
                        else:
                            link["statistics"] = None
                            link["stats_error"] = stats.get("error", "Unknown error")
                    except Exception as e:
                        logger.error(f"Error getting stats for {link['linked_page_title']}: {e}")
                        link["statistics"] = None
                        link["stats_error"] = str(e)
                
                logger.info(f"Statistics fetched for {len(links_to_process)} pages")
                links_data["stats_included"] = True
                links_data["stats_count"] = len(links_to_process)
            else:
                links_data["stats_included"] = False
            
            # Ajouter l'URL de la page source
            links_data["source_page_url"] = page_url
            links_data["source_page_title"] = page_title
            links_data["keyword_searched"] = keyword
            links_data["language"] = language
            
            return links_data
            
        except Exception as e:
            logger.error(f"get_wikipedia_internal_links error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
