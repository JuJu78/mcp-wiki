"""Wikidata entity discovery tools"""

import logging
from services.wikidata_api import WikidataAPIService

logger = logging.getLogger(__name__)


def register_wikidata_tools(mcp):
    """Enregistre les outils Wikidata."""

    @mcp.tool()
    async def explore_wikidata_entity(
        query: str,
        language: str = "fr",
        search_limit: int = 5,
        max_linked_entities: int = 200,
        ctx=None,
    ):
        """\
        Recherche une entité Wikidata à partir d'un terme et retourne l'entité + ses relations.

        Le tool:
        - cherche les entités Wikidata correspondant à `query`
        - sélectionne le 1er résultat
        - récupère l'URL Wikidata exacte
        - extrait les entités liées depuis les claims (relations)
        - récupère les labels/descriptions des entités liées

        Args:
            query: Terme à rechercher (ex: "SEO")
            language: Langue des labels (ex: fr, en)
            search_limit: Nombre de résultats max lors de la recherche (1-50)
            max_linked_entities: Limite d'entités liées à retourner (1-500)
        """
        if not query or not str(query).strip():
            return {"success": False, "error": "query is required and cannot be empty"}

        if search_limit < 1 or search_limit > 50:
            search_limit = 5

        if max_linked_entities < 1 or max_linked_entities > 500:
            max_linked_entities = 200

        try:
            service = WikidataAPIService()

            search = service.search_entities(query=query, language=language, limit=search_limit)
            if not search.get("success"):
                return search

            results = search.get("results", [])
            if not results:
                return {
                    "success": True,
                    "query": query,
                    "language": language,
                    "message": "No Wikidata entity found for this query",
                    "entity": None,
                    "candidates": [],
                }

            selected = results[0]
            entity_id = selected.get("id")

            entity_data = service.get_entity_data(entity_id)
            if not entity_data.get("success"):
                return {
                    "success": False,
                    "query": query,
                    "language": language,
                    "candidates": results,
                    "error": entity_data.get("error"),
                }

            entity = entity_data.get("entity", {})

            # Label/description de l'entité
            label = (((entity.get("labels", {}) or {}).get(language, {}) or {}).get("value"))
            description = (((entity.get("descriptions", {}) or {}).get(language, {}) or {}).get("value"))

            extracted = service.extract_linked_entities(entity, max_entities=max_linked_entities)
            if not extracted.get("success"):
                return extracted

            linked_ids = extracted.get("linked_entity_ids", [])
            labels_resp = service.get_entities_labels(linked_ids, language=language)
            if not labels_resp.get("success"):
                # On renvoie quand même l'entity et les ids si l'enrichissement échoue
                linked_entities = {qid: {"id": qid, "url": f"https://www.wikidata.org/wiki/{qid}"} for qid in linked_ids}
            else:
                linked_entities = labels_resp.get("entities", {})

            return {
                "success": True,
                "query": query,
                "language": language,
                "entity": {
                    "id": entity_id,
                    "label": label or selected.get("label"),
                    "description": description or selected.get("description"),
                    "url": selected.get("url") or f"https://www.wikidata.org/wiki/{entity_id}",
                },
                "candidates": results,
                "relations": extracted.get("relations", {}),
                "linked_entities": linked_entities,
                "linked_entities_count": len(linked_entities),
            }

        except Exception as e:
            logger.error(f"explore_wikidata_entity error: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def deep_dive_wikidata_topic(
        query: str,
        language: str = "fr",
        search_limit: int = 5,
        max_linked_entities: int = 200,
        max_identifier_properties: int = 200,
        max_values_per_identifier: int = 5,
        ctx=None,
    ):
        """\
        Deep dive sur un sujet via Wikidata.

        Retourne :
        - entité sélectionnée (id/label/description/url)
        - candidats de recherche
        - relations (claims -> entités liées)
        - entités liées enrichies (labels/descriptions)
        - sitelinks (Wikipedia/Wikibooks/Wikinews/etc.) en URLs cliquables
        - identifiers externes (external identifiers) en URLs cliquables quand possible

        Args:
            query: Sujet à creuser (ex: "SEO")
            language: Langue des labels (ex: fr, en)
            search_limit: Nombre de candidats à retourner (1-50)
            max_linked_entities: Limite d'entités liées à retourner (1-500)
            max_identifier_properties: Limite de propriétés inspectées pour identifiers
            max_values_per_identifier: Nb max de valeurs par propriété d'identifier
        """
        if not query or not str(query).strip():
            return {"success": False, "error": "query is required and cannot be empty"}

        if search_limit < 1 or search_limit > 50:
            search_limit = 5

        if max_linked_entities < 1 or max_linked_entities > 500:
            max_linked_entities = 200

        if max_identifier_properties < 1 or max_identifier_properties > 500:
            max_identifier_properties = 200

        if max_values_per_identifier < 1 or max_values_per_identifier > 25:
            max_values_per_identifier = 5

        try:
            service = WikidataAPIService()

            search = service.search_entities(query=query, language=language, limit=search_limit)
            if not search.get("success"):
                return search

            results = search.get("results", [])
            if not results:
                return {
                    "success": True,
                    "query": query,
                    "language": language,
                    "message": "No Wikidata entity found for this query",
                    "entity": None,
                    "candidates": [],
                }

            selected = results[0]
            entity_id = selected.get("id")
            entity_data = service.get_entity_data(entity_id)
            if not entity_data.get("success"):
                return {
                    "success": False,
                    "query": query,
                    "language": language,
                    "candidates": results,
                    "error": entity_data.get("error"),
                }

            entity = entity_data.get("entity", {})

            label = (((entity.get("labels", {}) or {}).get(language, {}) or {}).get("value"))
            description = (((entity.get("descriptions", {}) or {}).get(language, {}) or {}).get("value"))

            extracted = service.extract_linked_entities(entity, max_entities=max_linked_entities)
            if not extracted.get("success"):
                return extracted

            linked_ids = extracted.get("linked_entity_ids", [])
            labels_resp = service.get_entities_labels(linked_ids, language=language)
            if not labels_resp.get("success"):
                linked_entities = {
                    qid: {"id": qid, "url": f"https://www.wikidata.org/wiki/{qid}"}
                    for qid in linked_ids
                }
            else:
                linked_entities = labels_resp.get("entities", {})

            sitelinks_resp = service.extract_sitelinks(entity)
            identifiers_resp = service.extract_external_identifiers(
                entity,
                language=language,
                max_properties=max_identifier_properties,
                max_values_per_property=max_values_per_identifier,
            )

            return {
                "success": True,
                "query": query,
                "language": language,
                "entity": {
                    "id": entity_id,
                    "label": label or selected.get("label"),
                    "description": description or selected.get("description"),
                    "url": selected.get("url") or f"https://www.wikidata.org/wiki/{entity_id}",
                },
                "candidates": results,
                "relations": extracted.get("relations", {}),
                "linked_entities": linked_entities,
                "linked_entities_count": len(linked_entities),
                "sitelinks": sitelinks_resp.get("sitelinks", {}) if sitelinks_resp.get("success") else {},
                "sitelinks_count": sitelinks_resp.get("count", 0) if sitelinks_resp.get("success") else 0,
                "identifiers": identifiers_resp.get("identifiers", {}) if identifiers_resp.get("success") else {},
                "identifiers_count": identifiers_resp.get("identifiers_count", 0) if identifiers_resp.get("success") else 0,
            }
        except Exception as e:
            logger.error(f"deep_dive_wikidata_topic error: {e}")
            return {"success": False, "error": str(e)}
