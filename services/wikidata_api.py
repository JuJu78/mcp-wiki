"""Wikidata API service for entity lookup and relations"""

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests

from config.settings import get_headers

logger = logging.getLogger(__name__)


class WikidataAPIService:
    """Service pour interagir avec l'API Wikidata (MediaWiki)."""

    def __init__(self):
        self.api_url = "https://www.wikidata.org/w/api.php"
        self.headers = get_headers()

    def search_entities(
        self,
        query: str,
        language: str = "fr",
        limit: int = 5,
    ) -> Dict[str, Any]:
        """Recherche des entités Wikidata via wbsearchentities."""
        try:
            params = {
                "action": "wbsearchentities",
                "search": query,
                "language": language,
                "uselang": language,
                "format": "json",
                "limit": limit,
            }

            response = requests.get(
                self.api_url,
                params=params,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("search", []) or []:
                entity_id = item.get("id")
                if not entity_id:
                    continue

                results.append(
                    {
                        "id": entity_id,
                        "label": item.get("label"),
                        "description": item.get("description"),
                        "url": item.get("concepturi")
                        or f"https://www.wikidata.org/wiki/{entity_id}",
                        "match": item.get("match"),
                    }
                )

            return {
                "success": True,
                "query": query,
                "language": language,
                "total_results": len(results),
                "results": results,
            }
        except Exception as e:
            logger.error(f"Error searching Wikidata entities: {e}")
            return {"success": False, "error": str(e)}

    def get_properties_metadata(
        self,
        property_ids: List[str],
        language: str = "fr",
        batch_size: int = 50,
    ) -> Dict[str, Any]:
        """Récupère les métadonnées des propriétés (labels + formatter URL P1630)."""
        try:
            if not property_ids:
                return {"success": True, "properties": {}}

            properties_out: Dict[str, Any] = {}
            for i in range(0, len(property_ids), batch_size):
                chunk = property_ids[i : i + batch_size]
                params = {
                    "action": "wbgetentities",
                    "ids": "|".join(chunk),
                    "props": "labels|claims|datatype",
                    "languages": language,
                    "format": "json",
                }

                response = requests.get(
                    self.api_url,
                    params=params,
                    headers=self.headers,
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                for pid, prop in (data.get("entities", {}) or {}).items():
                    label = (
                        (prop.get("labels", {}) or {}).get(language, {}) or {}
                    ).get("value")

                    formatter_url = None
                    claims = prop.get("claims", {}) or {}
                    p1630 = claims.get("P1630")
                    if isinstance(p1630, list) and p1630:
                        mainsnak = (p1630[0] or {}).get("mainsnak", {}) or {}
                        datavalue = (mainsnak.get("datavalue") or {})
                        value = datavalue.get("value")
                        if isinstance(value, str) and value.strip():
                            formatter_url = value.strip()

                    properties_out[pid] = {
                        "id": pid,
                        "label": label,
                        "datatype": prop.get("datatype"),
                        "formatter_url": formatter_url,
                        "url": f"https://www.wikidata.org/wiki/Property:{pid}",
                    }

            return {"success": True, "properties": properties_out}
        except Exception as e:
            logger.error(f"Error getting Wikidata properties metadata: {e}")
            return {"success": False, "error": str(e)}

    def extract_sitelinks(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les sitelinks (Wikipedia, Wikibooks, etc.) en URLs cliquables."""
        try:
            sitelinks = entity.get("sitelinks", {}) or {}
            out: Dict[str, Any] = {}
            for key, info in sitelinks.items():
                title = (info or {}).get("title")
                if not title:
                    continue

                # key examples: enwiki, frwiki, enwikibooks, frwikinews...
                lang = key[:2]
                if key.endswith("wiki"):
                    domain = f"{lang}.wikipedia.org"
                elif key.endswith("wikibooks"):
                    domain = f"{lang}.wikibooks.org"
                elif key.endswith("wikinews"):
                    domain = f"{lang}.wikinews.org"
                elif key.endswith("wikiquote"):
                    domain = f"{lang}.wikiquote.org"
                elif key.endswith("wikisource"):
                    domain = f"{lang}.wikisource.org"
                elif key.endswith("wikiversity"):
                    domain = f"{lang}.wikiversity.org"
                elif key.endswith("wikivoyage"):
                    domain = f"{lang}.wikivoyage.org"
                else:
                    # Unknown sitelink type, keep raw
                    out[key] = {"site": key, "title": title, "url": None}
                    continue

                out[key] = {
                    "site": key,
                    "title": title,
                    "url": f"https://{domain}/wiki/{quote(title.replace(' ', '_'))}",
                }

            return {"success": True, "sitelinks": out, "count": len(out)}
        except Exception as e:
            logger.error(f"Error extracting sitelinks: {e}")
            return {"success": False, "error": str(e)}

    def extract_external_identifiers(
        self,
        entity: Dict[str, Any],
        language: str = "fr",
        max_properties: int = 200,
        max_values_per_property: int = 5,
    ) -> Dict[str, Any]:
        """Extrait des identifiants externes et construit des URLs via formatter URL (P1630).

        Notes:
        - Beaucoup d'identifiants sont des strings: on construit des liens actionnables.
        - Cas spécial: P646 (Freebase ID) => lien Google Knowledge Graph kgmid.
        """
        try:
            claims = entity.get("claims", {}) or {}
            property_ids = list(claims.keys())[:max_properties]

            prop_meta_resp = self.get_properties_metadata(property_ids, language=language)
            if not prop_meta_resp.get("success"):
                return prop_meta_resp
            prop_meta = prop_meta_resp.get("properties", {})

            identifiers: Dict[str, Any] = {}
            for pid in property_ids:
                statements = claims.get(pid)
                if not isinstance(statements, list) or not statements:
                    continue

                meta = prop_meta.get(pid, {})
                formatter_url = meta.get("formatter_url")
                values: List[Dict[str, Any]] = []

                for st in statements:
                    mainsnak = (st or {}).get("mainsnak", {}) or {}
                    datavalue = (mainsnak.get("datavalue") or {})
                    if not datavalue:
                        continue

                    raw_value = datavalue.get("value")
                    if not isinstance(raw_value, str):
                        continue

                    raw_value = raw_value.strip()
                    if not raw_value:
                        continue

                    url = None

                    # Special-case: Freebase ID -> Google KG mid
                    if pid == "P646":
                        url = f"https://www.google.com/search?kgmid={quote(raw_value, safe='') }"
                    elif formatter_url and "$1" in formatter_url:
                        url = formatter_url.replace("$1", quote(raw_value, safe=""))

                    values.append({"value": raw_value, "url": url})
                    if len(values) >= max_values_per_property:
                        break

                # Ne garder que les propriétés qui ont des valeurs string
                if values:
                    identifiers[pid] = {
                        "property": pid,
                        "property_label": meta.get("label"),
                        "property_url": meta.get("url"),
                        "formatter_url": formatter_url,
                        "values": values,
                        "count": len(values),
                    }

            return {
                "success": True,
                "identifiers": identifiers,
                "identifiers_count": len(identifiers),
            }
        except Exception as e:
            logger.error(f"Error extracting external identifiers: {e}")
            return {"success": False, "error": str(e)}

    def get_entity_data(self, entity_id: str) -> Dict[str, Any]:
        """Récupère les données d'une entité via Special:EntityData/{id}.json."""
        try:
            if not entity_id or not str(entity_id).strip():
                return {"success": False, "error": "entity_id is required"}

            entity_id = str(entity_id).strip()
            url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            entities = data.get("entities", {}) or {}
            entity = entities.get(entity_id)
            if not entity:
                return {"success": False, "error": f"Entity '{entity_id}' not found"}

            return {"success": True, "entity": entity}
        except Exception as e:
            logger.error(f"Error getting Wikidata entity data for {entity_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_entities_labels(
        self,
        entity_ids: List[str],
        language: str = "fr",
        batch_size: int = 50,
    ) -> Dict[str, Any]:
        """Récupère les labels/descriptions pour une liste d'entités (wbgetentities)."""
        try:
            if not entity_ids:
                return {"success": True, "entities": {}}

            entities_out: Dict[str, Any] = {}
            for i in range(0, len(entity_ids), batch_size):
                chunk = entity_ids[i : i + batch_size]
                params = {
                    "action": "wbgetentities",
                    "ids": "|".join(chunk),
                    "props": "labels|descriptions",
                    "languages": language,
                    "format": "json",
                }

                response = requests.get(
                    self.api_url,
                    params=params,
                    headers=self.headers,
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                for ent_id, ent in (data.get("entities", {}) or {}).items():
                    label = (
                        (ent.get("labels", {}) or {}).get(language, {}) or {}
                    ).get("value")
                    description = (
                        (ent.get("descriptions", {}) or {}).get(language, {}) or {}
                    ).get("value")

                    entities_out[ent_id] = {
                        "id": ent_id,
                        "label": label,
                        "description": description,
                        "url": f"https://www.wikidata.org/wiki/{ent_id}",
                    }

            return {"success": True, "entities": entities_out}
        except Exception as e:
            logger.error(f"Error getting Wikidata labels: {e}")
            return {"success": False, "error": str(e)}

    def extract_linked_entities(
        self,
        entity: Dict[str, Any],
        max_entities: int = 200,
    ) -> Dict[str, Any]:
        """Extrait les entités Qxxx référencées dans les claims d'une entité."""
        try:
            claims = entity.get("claims", {}) or {}

            linked: List[str] = []
            relations: Dict[str, Any] = {}

            for prop, statements in claims.items():
                if not isinstance(statements, list):
                    continue

                prop_entities: List[str] = []
                for st in statements:
                    mainsnak = (st or {}).get("mainsnak", {}) or {}
                    datavalue = (mainsnak.get("datavalue") or {})
                    if not datavalue:
                        continue

                    value = datavalue.get("value")
                    if isinstance(value, dict) and value.get("entity-type") == "item":
                        qid = value.get("id")
                        if qid and qid.startswith("Q"):
                            prop_entities.append(qid)

                if prop_entities:
                    # Dé-doublonnage tout en gardant un ordre stable
                    seen = set()
                    unique_prop_entities = []
                    for qid in prop_entities:
                        if qid in seen:
                            continue
                        seen.add(qid)
                        unique_prop_entities.append(qid)

                    relations[prop] = {
                        "property": prop,
                        "linked_entities": unique_prop_entities,
                        "count": len(unique_prop_entities),
                    }

                    for qid in unique_prop_entities:
                        if qid not in linked:
                            linked.append(qid)
                            if len(linked) >= max_entities:
                                break

                if len(linked) >= max_entities:
                    break

            return {
                "success": True,
                "relations": relations,
                "linked_entity_ids": linked,
            }
        except Exception as e:
            logger.error(f"Error extracting linked entities: {e}")
            return {"success": False, "error": str(e)}
