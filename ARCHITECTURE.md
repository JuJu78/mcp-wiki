# 🏗️ Architecture MCP-Wiki

## Vue d'ensemble du système

```
┌─────────────────────────────────────────────────────────────┐
│                     UTILISATEUR                              │
│              (Claude Desktop / ChatGPT)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Protocole MCP
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  MCP-WIKI SERVER                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               app.py (Main Entry)                     │  │
│  └─────────────────────┬─────────────────────────────────┘  │
│                        │                                     │
│  ┌─────────────────────▼─────────────────────────────────┐  │
│  │         core/mcp_server.py (Initialisation)           │  │
│  │         core/server_modes.py (STDIO/HTTP/SSE)         │  │
│  └─────────────────────┬─────────────────────────────────┘  │
│                        │                                     │
│  ┌─────────────────────▼─────────────────────────────────┐  │
│  │           tools/wikipedia_tools.py                    │  │
│  │   ┌─────────────────────────────────────────────┐     │  │
│  │   │  • search_wikipedia_keyword                 │     │  │
│  │   │  • get_wikipedia_page_stats                 │     │  │
│  │   └─────────────────────────────────────────────┘     │  │
│  └─────────────────────┬─────────────────────────────────┘  │
│                        │                                     │
│  ┌─────────────────────▼─────────────────────────────────┐  │
│  │       services/wikipedia_api.py                       │  │
│  │   ┌─────────────────────────────────────────────┐     │  │
│  │   │  • search_pages()                           │     │  │
│  │   │  • get_page_info()                          │     │  │
│  │   │  • get_pageviews()                          │     │  │
│  │   │  • get_comprehensive_stats()                │     │  │
│  │   └─────────────────────────────────────────────┘     │  │
│  └─────────────────────┬─────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          │                             │
┌─────────▼──────────┐      ┌──────────▼───────────┐
│  Wikipedia API     │      │ Wikimedia Pageviews  │
│  (Search)          │      │ API (Statistics)     │
│                    │      │                      │
│  • opensearch      │      │  • per-article       │
│  • query           │      │  • daily/monthly     │
└────────────────────┘      └──────────────────────┘
```

## Flux de données

### 1. Recherche de pages Wikipedia

```
Claude Desktop
    │
    │ "Recherche des pages sur 'machine learning'"
    │
    ▼
MCP Server (app.py)
    │
    │ Appel: search_wikipedia_keyword(keyword="machine learning", language="en")
    │
    ▼
wikipedia_tools.py
    │
    │ Validation des paramètres
    │ Création du service Wikipedia
    │
    ▼
wikipedia_api.py
    │
    │ search_pages(keyword, limit=20)
    │
    ▼
Wikipedia API
    │
    │ GET https://en.wikipedia.org/w/api.php?action=opensearch&search=...
    │
    ▼
Réponse JSON
    │
    │ [query, [titles], [descriptions], [urls]]
    │
    ▼
wikipedia_api.py
    │
    │ Pour chaque page:
    │   - get_comprehensive_stats(page_title)
    │       ├─ get_page_info()
    │       └─ get_pageviews() (past_month, past_year, current_month, etc.)
    │
    ▼
Wikimedia Pageviews API
    │
    │ GET https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/...
    │
    ▼
Agrégation des statistiques
    │
    │ {
    │   "past_month_views": 156789,
    │   "past_year_views": 2145678,
    │   "daily_views_current_month": 5123,
    │   "yoy_change_percent": 12.2
    │ }
    │
    ▼
Retour à Claude Desktop
    │
    │ Affichage formaté avec liens et statistiques
    │
    ▼
Utilisateur
```

### 2. Statistiques d'une page spécifique

```
ChatGPT
    │
    │ "Stats de la page 'Python (programming language)'"
    │
    ▼
MCP Server
    │
    │ get_wikipedia_page_stats(page_title="Python (programming language)")
    │
    ▼
wikipedia_api.py
    │
    │ get_comprehensive_stats(page_title)
    │
    ├─► get_page_info()
    │   └─ Wikipedia API (action=query)
    │
    └─► get_pageviews()
        ├─ past_month (30 jours)
        ├─ past_year (365 jours)
        ├─ current_month
        └─ last_year_same_month
            │
            ▼
        Calcul YoY
            │
            ▼
        Retour complet
```

## Structure des modules

### config/

```python
settings.py
├─ load_environment()          # Charge .env
├─ setup_logging()             # Configure les logs
├─ get_server_config()         # Config serveur (mode, host, port)
├─ get_wikipedia_config()      # Config Wikipedia
└─ get_headers()               # Headers HTTP

constants.py
├─ SUPPORTED_LANGUAGES         # 14 langues Wikipedia
├─ SEARCH_TYPES                # Types de recherche
└─ STATS_PERIODS               # Périodes statistiques
```

### core/

```python
mcp_server.py
└─ create_mcp_server()         # Crée instance serveur MCP

server_modes.py
└─ MCPServerMultiMode
   ├─ __init__(name)           # Initialise serveur
   ├─ register_tool()          # Enregistre un outil
   ├─ run_stdio()              # Mode Claude Desktop
   ├─ run_http()               # Mode API REST
   ├─ run_sse()                # Mode Server-Sent Events
   └─ run_chatgpt()            # Mode ChatGPT
```

### services/

```python
wikipedia_api.py
└─ WikipediaAPIService
   ├─ __init__(language)       # Init avec langue
   ├─ search_pages()           # Recherche pages
   ├─ get_page_info()          # Infos page
   ├─ get_pageviews()          # Stats de vues
   └─ get_comprehensive_stats() # Stats complètes
```

### tools/

```python
wikipedia_tools.py
├─ search_wikipedia_keyword()  # Outil MCP recherche
└─ get_wikipedia_page_stats()  # Outil MCP stats page
```

## Modes de communication

### Mode STDIO (Claude Desktop)

```
Claude Desktop Process
    │
    │ lance subprocess: python app.py
    │
    ▼
MCP Server (STDIO)
    │
    │ stdin/stdout communication
    │ JSON-RPC 2.0 protocol
    │
    ▼
FastMCP
    │
    │ Gère les messages MCP
    │ - initialize
    │ - tools/list
    │ - tools/call
    │
    ▼
Outils MCP exécutés
```

### Mode HTTP (API REST)

```
Client HTTP
    │
    │ GET http://127.0.0.1:8000/tools
    │
    ▼
FastAPI Server
    │
    │ Endpoints:
    │ - GET /
    │ - GET /tools
    │ - POST /tools/call
    │
    ▼
Outils MCP exécutés
```

### Mode ChatGPT

```
ChatGPT
    │
    │ POST http://ngrok-url/mcp
    │ { "method": "tools/list", ... }
    │
    ▼
ngrok tunnel
    │
    ▼
FastAPI Server (/mcp endpoint)
    │
    │ JSON-RPC 2.0 protocol
    │ Streamable HTTP transport
    │
    ▼
Outils MCP exécutés
```

## Format des données

### Requête MCP (tools/call)

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "search_wikipedia_keyword",
    "arguments": {
      "keyword": "artificial intelligence",
      "language": "en",
      "max_results": 10,
      "include_stats": true
    }
  }
}
```

### Réponse MCP

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\": true, \"pages\": [...]}"
      }
    ]
  }
}
```

### Données Wikipedia API (opensearch)

```json
[
  "machine learning",
  [
    "Machine Learning",
    "Machine learning in bioinformatics"
  ],
  [
    "Field of study in artificial intelligence",
    "Application of machine learning methods"
  ],
  [
    "https://en.wikipedia.org/wiki/Machine_Learning",
    "https://en.wikipedia.org/wiki/Machine_learning_in_bioinformatics"
  ]
]
```

### Données Pageviews API

```json
{
  "items": [
    {
      "project": "en.wikipedia",
      "article": "Machine_Learning",
      "granularity": "daily",
      "timestamp": "2025110100",
      "access": "all-access",
      "agent": "all-agents",
      "views": 5123
    }
  ]
}
```

## Gestion des erreurs

```
Outil MCP appelé
    │
    ▼
Validation des paramètres
    │
    ├─ OK ─────────► Exécution
    │
    └─ ERREUR ────► {"success": false, "error": "..."}
                         │
                         ▼
                    Retour à l'utilisateur
```

## Performance

### Temps de réponse typiques

- **search_pages()** : ~500ms (recherche seule)
- **get_pageviews()** : ~200ms par page
- **get_comprehensive_stats()** : ~800ms (4 appels API)
- **search_wikipedia_keyword(10 pages)** : ~8s total

### Optimisations possibles

1. **Cache** : Mettre en cache les résultats de recherche
2. **Async parallel** : Récupérer les stats en parallèle
3. **Rate limiting** : Respecter les limites des APIs
4. **Pagination** : Implémenter la pagination pour les gros résultats

## Sécurité

### Headers HTTP

```python
{
  "User-Agent": "MCP-Wiki/1.0 (...)",
  "Accept": "application/json"
}
```

### CORS (modes HTTP/SSE/ChatGPT)

```python
allow_origins=["*"]  # Permissif pour le développement
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

### Validation des entrées

- Vérification des paramètres requis
- Validation des codes de langue
- Limitation du nombre de résultats (1-50)
- Sanitisation des titres de pages

## Extensibilité

### Ajouter un nouvel outil MCP

1. Créer une fonction dans `tools/wikipedia_tools.py`
2. Décorer avec `@mcp.tool()`
3. L'outil sera automatiquement enregistré

```python
@mcp.tool()
async def new_wikipedia_tool(param: str, ctx=None):
    """Description de l'outil"""
    # Implémentation
    return {"success": True, "data": ...}
```

### Ajouter une nouvelle API externe

1. Créer un nouveau fichier dans `services/`
2. Implémenter la classe de service
3. Utiliser dans les outils

```python
# services/new_api.py
class NewAPIService:
    def __init__(self):
        self.api_url = "https://..."
    
    def fetch_data(self, param):
        # Implémentation
        pass
```

## Dépendances

### Principales bibliothèques

```
fastmcp       # Framework MCP
mcp[cli]      # SDK officiel MCP
fastapi       # API web
uvicorn       # Serveur ASGI
requests      # Client HTTP
httpx         # Client HTTP async
python-dotenv # Variables d'environnement
```

### Architecture logicielle

```
Python 3.8+
    │
    ├─ fastmcp (MCP protocol)
    │   └─ FastMCP class
    │
    ├─ fastapi (Web framework)
    │   └─ FastAPI + Uvicorn
    │
    └─ requests/httpx (HTTP clients)
        └─ Wikipedia/Wikimedia APIs
```

---

Cette architecture assure :
- ✅ Modularité
- ✅ Extensibilité
- ✅ Maintenabilité
- ✅ Performance
- ✅ Multi-modes (STDIO/HTTP/SSE/ChatGPT)
