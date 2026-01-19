"""Wikipedia API service for fetching pages and statistics"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from config.settings import get_wikipedia_config, get_headers

logger = logging.getLogger(__name__)

class WikipediaAPIService:
    """Service pour interagir avec les APIs Wikipedia et Pageviews"""
    
    def __init__(self, language: str = "en"):
        self.config = get_wikipedia_config()
        self.language = language
        self.api_url = f"https://{language}.wikipedia.org/w/api.php"
        self.pageviews_api_url = self.config["pageviews_api_url"]
        self.headers = get_headers()
    
    def search_pages(self, keyword: str, limit: int = 20) -> Dict[str, Any]:
        """
        Recherche des pages Wikipedia liées à un mot-clé
        
        Args:
            keyword: Le terme de recherche
            limit: Nombre maximum de résultats
            
        Returns:
            Dictionnaire avec les résultats de recherche
        """
        try:
            params = {
                "action": "opensearch",
                "search": keyword,
                "limit": limit,
                "namespace": 0,  # Articles principaux uniquement
                "format": "json"
            }
            
            response = requests.get(
                self.api_url,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Format OpenSearch: [query, [titles], [descriptions], [urls]]
            if len(data) >= 4:
                titles = data[1]
                descriptions = data[2]
                urls = data[3]
                
                results = []
                for i in range(len(titles)):
                    results.append({
                        "title": titles[i],
                        "description": descriptions[i] if i < len(descriptions) else "",
                        "url": urls[i] if i < len(urls) else "",
                        "page_name": titles[i].replace(" ", "_")
                    })
                
                return {
                    "success": True,
                    "keyword": keyword,
                    "language": self.language,
                    "total_results": len(results),
                    "results": results
                }
            
            return {
                "success": False,
                "error": "Invalid response format from Wikipedia API"
            }
            
        except Exception as e:
            logger.error(f"Error searching Wikipedia pages: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_page_info(self, page_title: str) -> Dict[str, Any]:
        """
        Récupère les informations détaillées d'une page Wikipedia
        
        Args:
            page_title: Titre de la page
            
        Returns:
            Informations sur la page
        """
        try:
            params = {
                "action": "query",
                "titles": page_title,
                "prop": "info|pageprops",
                "inprop": "url|created",
                "format": "json"
            }
            
            response = requests.get(
                self.api_url,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            
            if pages:
                page = list(pages.values())[0]
                
                # Extraire les informations
                page_info = {
                    "page_id": page.get("pageid"),
                    "title": page.get("title"),
                    "url": page.get("fullurl"),
                    "created": page.get("touched", "Unknown")
                }
                
                # Parser la date de création si disponible
                if "touched" in page:
                    try:
                        touched = page["touched"]
                        created_date = datetime.strptime(touched, "%Y-%m-%dT%H:%M:%SZ")
                        page_info["created_formatted"] = created_date.strftime("%B %d, %Y")
                    except:
                        page_info["created_formatted"] = "Unknown"
                
                return page_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting page info: {e}")
            return None
    
    def get_pageviews(
        self,
        page_title: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        granularity: str = "daily"
    ) -> Dict[str, Any]:
        """
        Récupère les statistiques de vues pour une page
        
        Args:
            page_title: Titre de la page
            start_date: Date de début (YYYYMMDD)
            end_date: Date de fin (YYYYMMDD)
            granularity: daily ou monthly
            
        Returns:
            Statistiques de vues
        """
        try:
            # Dates par défaut: 1 an
            if not end_date:
                end_date = datetime.now().strftime("%Y%m%d")
            if not start_date:
                start = datetime.now() - timedelta(days=365)
                start_date = start.strftime("%Y%m%d")
            
            # Nettoyer le titre pour l'URL
            page_title_encoded = page_title.replace(" ", "_")
            
            url = f"{self.pageviews_api_url}/metrics/pageviews/per-article/{self.language}.wikipedia/all-access/all-agents/{page_title_encoded}/{granularity}/{start_date}/{end_date}"
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 404:
                return {
                    "success": False,
                    "error": "Page not found in pageviews data"
                }
            
            response.raise_for_status()
            data = response.json()
            
            items = data.get("items", [])
            
            if not items:
                return {
                    "success": True,
                    "page_title": page_title,
                    "total_views": 0,
                    "data_points": 0,
                    "views": []
                }
            
            # Calculer les statistiques
            total_views = sum(item.get("views", 0) for item in items)
            
            return {
                "success": True,
                "page_title": page_title,
                "total_views": total_views,
                "data_points": len(items),
                "start_date": start_date,
                "end_date": end_date,
                "granularity": granularity,
                "views": items
            }
            
        except Exception as e:
            logger.error(f"Error getting pageviews for {page_title}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_comprehensive_stats(self, page_title: str) -> Dict[str, Any]:
        """
        Récupère toutes les statistiques pour une page (comme detailed.com)
        
        Args:
            page_title: Titre de la page
            
        Returns:
            Statistiques complètes
        """
        try:
            # Obtenir les infos de base
            page_info = self.get_page_info(page_title)
            
            if not page_info:
                return {
                    "success": False,
                    "error": f"Page '{page_title}' not found"
                }
            
            # Dates pour les différentes périodes
            now = datetime.now()
            
            # Dernier mois (30 jours)
            past_month_start = (now - timedelta(days=30)).strftime("%Y%m%d")
            past_month_end = now.strftime("%Y%m%d")
            
            # Année dernière (365 jours)
            past_year_start = (now - timedelta(days=365)).strftime("%Y%m%d")
            past_year_end = now.strftime("%Y%m%d")
            
            # Mois en cours
            current_month_start = now.replace(day=1).strftime("%Y%m%d")
            current_month_end = now.strftime("%Y%m%d")
            
            # Même mois année dernière
            last_year_same_month_start = (now.replace(day=1) - timedelta(days=365)).strftime("%Y%m%d")
            last_year_same_month_end = (now - timedelta(days=365)).strftime("%Y%m%d")
            
            # Récupérer les stats
            past_month_views = self.get_pageviews(page_title, past_month_start, past_month_end)
            past_year_views = self.get_pageviews(page_title, past_year_start, past_year_end)
            current_month_views = self.get_pageviews(page_title, current_month_start, current_month_end)
            last_year_month_views = self.get_pageviews(page_title, last_year_same_month_start, last_year_same_month_end)
            
            # Calculer les moyennes quotidiennes
            days_in_current_month = (now - now.replace(day=1)).days + 1
            daily_views_current = (
                current_month_views.get("total_views", 0) / days_in_current_month
                if days_in_current_month > 0 else 0
            )
            
            days_in_last_year_month = (
                datetime.strptime(last_year_same_month_end, "%Y%m%d") -
                datetime.strptime(last_year_same_month_start, "%Y%m%d")
            ).days + 1
            daily_views_last_year = (
                last_year_month_views.get("total_views", 0) / days_in_last_year_month
                if days_in_last_year_month > 0 else 0
            )
            
            # Calculer le changement YoY
            if daily_views_last_year > 0:
                yoy_change = ((daily_views_current - daily_views_last_year) / daily_views_last_year) * 100
            else:
                yoy_change = 0 if daily_views_current == 0 else 100
            
            return {
                "success": True,
                "page_info": page_info,
                "statistics": {
                    "past_month_total_views": past_month_views.get("total_views", 0),
                    "past_year_total_views": past_year_views.get("total_views", 0),
                    "daily_views_current_month": round(daily_views_current),
                    "daily_views_last_year_same_month": round(daily_views_last_year),
                    "yoy_change_percent": round(yoy_change, 1)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_internal_links(self, page_title: str, max_links: int = 200) -> Dict[str, Any]:
        """
        Récupère tous les liens internes (ancres) d'une page Wikipedia
        
        Args:
            page_title: Titre de la page Wikipedia
            
        Returns:
            Dictionnaire avec la liste des liens internes
        """
        try:
            if max_links < 1:
                max_links = 200

            internal_links = []
            seen_titles = set()

            plcontinue = None
            page_id = None
            title = page_title

            partial = False

            while True:
                params = {
                    "action": "query",
                    "titles": page_title,
                    "prop": "links",
                    "plnamespace": 0,
                    "pllimit": "max",
                    "format": "json",
                }
                if plcontinue:
                    params["plcontinue"] = plcontinue

                try:
                    response = requests.get(
                        self.api_url,
                        params=params,
                        headers=self.headers,
                        timeout=20,
                    )
                    response.raise_for_status()
                    data = response.json()
                except requests.exceptions.Timeout:
                    partial = True
                    break

                pages = data.get("query", {}).get("pages", {}) or {}
                if not pages:
                    return {
                        "success": False,
                        "error": f"Page '{page_title}' not found"
                    }

                page = list(pages.values())[0]
                if page.get("missing") is not None:
                    return {
                        "success": False,
                        "error": f"Page '{page_title}' not found"
                    }

                page_id = page.get("pageid")
                title = page.get("title") or title

                links = page.get("links", []) or []
                for l in links:
                    linked_title = (l or {}).get("title")
                    if not linked_title:
                        continue
                    if linked_title in seen_titles:
                        continue
                    seen_titles.add(linked_title)
                    internal_links.append({
                        "anchor_text": linked_title,
                        "linked_page_title": linked_title,
                        "url": f"https://{self.language}.wikipedia.org/wiki/{linked_title.replace(' ', '_')}"
                    })

                    if len(internal_links) >= max_links:
                        partial = True
                        break

                if len(internal_links) >= max_links:
                    break

                cont = data.get("continue", {}) or {}
                plcontinue = cont.get("plcontinue")
                if not plcontinue:
                    break

            return {
                "success": True,
                "page_title": title,
                "page_id": page_id,
                "total_internal_links": len(internal_links),
                "internal_links": internal_links,
                "partial": partial,
                "max_links": max_links,
            }
            
        except Exception as e:
            logger.error(f"Error getting internal links: {e}")
            return {
                "success": False,
                "error": str(e)
            }
