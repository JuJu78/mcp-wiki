"""Wikidata entity discovery tools"""

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional, Set

import requests
from bs4 import BeautifulSoup
from services.wikidata_api import WikidataAPIService

logger = logging.getLogger(__name__)


def _normalize_term(value: str) -> Optional[str]:
    if value is None:
        return None
    v = str(value).strip()
    if not v:
        return None
    v = re.sub(r"\s+", " ", v)
    return v


def _dedupe_terms(values: List[str]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for raw in values or []:
        v = _normalize_term(raw)
        if not v:
            continue
        key = v.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(v)
    return out


def _extract_terms_from_text(text: str, max_terms: int = 50) -> List[str]:
    if not text:
        return []

    candidates: List[str] = []

    # Heuristique: groupes de mots commençant par majuscule (noms propres)
    pattern = re.compile(r"\b([A-Z][\w'\-]+(?:\s+[A-Z][\w'\-]+){0,3})\b")
    for m in pattern.finditer(text):
        candidates.append(m.group(1))
        if len(candidates) >= max_terms * 3:
            break

    return _dedupe_terms(candidates)[:max_terms]


def _extract_terms_from_url_html(html: str, max_terms: int = 50) -> List[str]:
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    candidates: List[str] = []

    title = (soup.title.string if soup.title else None)
    if title:
        candidates.append(title)

    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        candidates.append(h1.get_text(strip=True))

    # Si la page contient déjà des liens Wikipedia, c'est un signal fort.
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        if not href:
            continue
        if "wikipedia.org/wiki/" in href:
            part = href.split("/wiki/", 1)[-1]
            part = part.split("#", 1)[0]
            part = part.split("?", 1)[0]
            part = part.replace("_", " ")
            if part:
                candidates.append(part)
        if len(candidates) >= max_terms * 5:
            break

    return _dedupe_terms(candidates)[:max_terms]


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

    @mcp.tool()
    async def resolve_wikidata_entities(
        entities: List[str],
        language: str = "fr",
        search_limit: int = 5,
        max_concurrency: int = 8,
        ctx=None,
    ):
        """\
        Résout une liste de termes (entités candidates) vers Wikidata en batch.

        Objectif: éviter que le modèle fasse des appels un par un.
        Le tool:
        - dé-duplique les termes
        - parallélise les appels à Wikidata (`wbsearchentities`)
        - retourne une liste unique d'entités (Qid) + URLs cliquables

        Args:
            entities: Liste de termes à résoudre
            language: Langue des labels (ex: fr, en)
            search_limit: Nombre de candidats max par terme (1-50)
            max_concurrency: Nombre max d'appels en parallèle (1-32)
        """
        if not isinstance(entities, list) or not entities:
            return {"success": False, "error": "entities must be a non-empty list of strings"}

        if search_limit < 1 or search_limit > 50:
            search_limit = 5
        if max_concurrency < 1 or max_concurrency > 32:
            max_concurrency = 8

        terms = _dedupe_terms(entities)
        service = WikidataAPIService()
        sem = asyncio.Semaphore(max_concurrency)

        async def resolve_one(term: str) -> Dict[str, Any]:
            async with sem:
                resp = await asyncio.to_thread(
                    service.search_entities,
                    query=term,
                    language=language,
                    limit=search_limit,
                )
                if not resp.get("success"):
                    return {"term": term, "success": False, "error": resp.get("error")}

                results = resp.get("results", []) or []
                if not results:
                    return {"term": term, "success": True, "entity": None, "candidates": []}

                best = results[0]
                qid = best.get("id")
                return {
                    "term": term,
                    "success": True,
                    "entity": {
                        "id": qid,
                        "label": best.get("label"),
                        "description": best.get("description"),
                        "url": best.get("url")
                        or (f"https://www.wikidata.org/wiki/{qid}" if qid else None),
                    },
                    "candidates": results,
                }

        resolved = await asyncio.gather(*(resolve_one(t) for t in terms))

        unique_entities: Dict[str, Any] = {}
        unresolved: List[Dict[str, Any]] = []
        for item in resolved:
            if not item.get("success"):
                unresolved.append(item)
                continue
            ent = item.get("entity")
            if not ent or not ent.get("id"):
                unresolved.append(item)
                continue
            qid = ent["id"]
            if qid not in unique_entities:
                unique_entities[qid] = {**ent, "matched_terms": [item.get("term")]}
            else:
                unique_entities[qid]["matched_terms"].append(item.get("term"))

        entities_list = list(unique_entities.values())
        entities_list.sort(key=lambda x: (x.get("label") or x.get("id") or ""))

        return {
            "success": True,
            "language": language,
            "terms_count": len(terms),
            "entities_count": len(entities_list),
            "entities": entities_list,
            "unresolved": unresolved,
        }

    @mcp.tool()
    async def resolve_wikidata_entities_from_text(
        text: str,
        language: str = "fr",
        max_terms: int = 50,
        search_limit: int = 5,
        max_concurrency: int = 8,
        ctx=None,
    ):
        """\
        Extrait des entités candidates depuis un texte puis les résout vers Wikidata.

        Note: l'extraction est heuristique (noms propres). Pour un NER plus précis,
        laisse le modèle produire une liste de candidats et appelle `resolve_wikidata_entities`.
        """
        if not text or not str(text).strip():
            return {"success": False, "error": "text is required and cannot be empty"}

        if max_terms < 1 or max_terms > 200:
            max_terms = 50

        terms = _extract_terms_from_text(str(text), max_terms=max_terms)
        return await resolve_wikidata_entities(
            entities=terms,
            language=language,
            search_limit=search_limit,
            max_concurrency=max_concurrency,
        )

    @mcp.tool()
    async def resolve_wikidata_entities_from_urls(
        urls: List[str],
        language: str = "fr",
        max_terms_per_url: int = 30,
        search_limit: int = 5,
        max_concurrency: int = 8,
        timeout_seconds: int = 20,
        ctx=None,
    ):
        """\
        Prend une liste d'URLs, extrait des entités candidates (title/h1 + liens Wikipedia présents),
        dé-duplique, puis résout en batch vers Wikidata.
        """
        if not isinstance(urls, list) or not urls:
            return {"success": False, "error": "urls must be a non-empty list"}

        if max_terms_per_url < 1 or max_terms_per_url > 200:
            max_terms_per_url = 30

        fetched: List[Dict[str, Any]] = []
        all_terms: List[str] = []

        for raw in urls:
            url = _normalize_term(raw)
            if not url:
                continue
            try:
                resp = requests.get(url, timeout=timeout_seconds)
                resp.raise_for_status()
                terms = _extract_terms_from_url_html(resp.text, max_terms=max_terms_per_url)
                fetched.append({"url": url, "success": True, "terms": terms, "terms_count": len(terms)})
                all_terms.extend(terms)
            except Exception as e:
                fetched.append({"url": url, "success": False, "error": str(e)})

        deduped_terms = _dedupe_terms(all_terms)
        resolution = await resolve_wikidata_entities(
            entities=deduped_terms,
            language=language,
            search_limit=search_limit,
            max_concurrency=max_concurrency,
        )

        return {
            "success": True,
            "language": language,
            "urls_count": len(urls),
            "sources": fetched,
            "extracted_terms_count": len(deduped_terms),
            "resolution": resolution,
        }
