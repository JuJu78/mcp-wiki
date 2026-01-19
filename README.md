# MCP Wiki - Wikipedia + Wikidata Toolkit (MCP Server)

Serveur MCP (Model Context Protocol) pour explorer **Wikipedia** (pages, liens internes, statistiques de vues) et **Wikidata** (entités, relations, sitelinks, identifiants externes).

## Fonctionnalités

- **Extraction de liens internes** : Récupère tous les liens (ancres) présents dans le contenu d'une page Wikipedia
- **Recherche par mot-clé** : Trouve automatiquement la page correspondante puis extrait ses liens
- **Multi-langues** : Support de 14 langues Wikipedia (en, fr, de, es, it, pt, nl, pl, ru, ja, zh, ar, ko, hi)
- **Multi-modes** : Compatible avec Claude Desktop, ChatGPT, et API HTTP/SSE
- **Liens avec ancres** : Retourne le texte de l'ancre + l'URL de destination + le titre de la page liée
- **Exploration Wikidata** : Recherche d'entités, extraction des relations (claims), enrichissement des entités liées
- **Sitelinks multi-projets** : Liens vers Wikipedia/Wikibooks/Wikinews/etc. directement depuis une entité Wikidata
- **Identifiants externes** : Extraction d'identifiants (IMDb, VIAF, etc.) et construction d'URLs quand possible

## Données extraites

Pour chaque lien interne trouvé dans une page Wikipedia, le serveur retourne :

- **Texte de l'ancre** : Le texte cliquable (ex: "application web", "Google", "PageRank")
- **Titre de la page liée** : Titre de la page Wikipedia de destination
- **URL complète** : Lien direct vers la page Wikipedia (ex: https://fr.wikipedia.org/wiki/Google)
- **Nombre total de liens** : Comptage du nombre de liens internes dans la page

## Outils MCP disponibles

### 1. `get_wikipedia_internal_links` (Principal)

Extrait tous les liens internes (ancres) d'une page Wikipedia à partir d'un mot-clé.

**Paramètres :**
- `keyword` (str, requis) : Terme de recherche pour trouver la page Wikipedia
- `language` (str, optionnel) : Code langue (défaut: "fr")
- `include_stats` (bool, optionnel) : Récupérer les statistiques de vues (défaut: false)
- `max_links_with_stats` (int, optionnel) : Nombre max de liens avec stats, 1-100 (défaut: 20)

### 2. `search_wikipedia_keyword`

Recherche des pages Wikipedia liées à un mot-clé avec statistiques de vues.

**Paramètres :**
- `keyword` (str, requis) : Terme de recherche
- `language` (str, optionnel) : Code langue (défaut: "en")
- `max_results` (int, optionnel) : Nombre de résultats (1-50, défaut: 20)
- `include_stats` (bool, optionnel) : Inclure les statistiques (défaut: true)

### 3. `get_wikipedia_page_stats`

Récupère les statistiques de vues pour une page Wikipedia spécifique.

**Paramètres :**
- `page_title` (str, requis) : Titre exact de la page
- `language` (str, optionnel) : Code langue (défaut: "en")

### 4. `explore_wikidata_entity`

Recherche une entité Wikidata à partir d'un terme et retourne l'entité + ses relations.

**Cas d'usage :**
- Trouver l'entité Wikidata la plus probable pour un concept (ex: "SEO", "Google", "Python")
- Obtenir les entités liées (Qxxx) via les claims, avec labels/descriptions

**Paramètres :**
- `query` (str, requis)
- `language` (str, optionnel, défaut: "fr")
- `search_limit` (int, optionnel, 1-50, défaut: 5)
- `max_linked_entities` (int, optionnel, 1-500, défaut: 200)

### 5. `deep_dive_wikidata_topic`

Deep dive sur un sujet via Wikidata.

Retourne :
- l'entité sélectionnée + candidats de recherche
- relations (claims -> entités liées) + enrichissement des entités liées
- sitelinks (Wikipedia/Wikibooks/Wikinews/etc.) en URLs cliquables
- identifiants externes (external identifiers) en URLs cliquables quand possible

**Paramètres :**
- `query` (str, requis)
- `language` (str, optionnel, défaut: "fr")
- `search_limit` (int, optionnel, 1-50, défaut: 5)
- `max_linked_entities` (int, optionnel, 1-500, défaut: 200)
- `max_identifier_properties` (int, optionnel, 1-500, défaut: 200)
- `max_values_per_identifier` (int, optionnel, 1-25, défaut: 5)

 ## 🚀 Installation

 ### 1. Cloner le projet

 ```bash
 git clone https://github.com/JuJu78/mcp-wiki.git
 cd mcp-wiki
 ```

 ### 2. Créer un environnement virtuel

 ```bash
 python -m venv venv
 venv\Scripts\activate  # Windows
 # ou
 source venv/bin/activate  # Linux/Mac
 ```

 ### 3. Installer les dépendances

 ```bash
 pip install -r requirements.txt
 ```

 ### 4. Configuration

 Copier le fichier `.env.example` en `.env` :

 ```bash
 copy .env.example .env  # Windows
 # ou
 cp .env.example .env  # Linux/Mac
 ```

 ## 📝 Utilisation

 ### Mode STDIO (Claude Desktop)

 Ajouter une configuration de serveur MCP (Windows) :

 ```json
 {
   "mcpServers": {
     "mcp-wiki": {
       "command": "python",
       "args": ["C:\\path\\to\\mcp-wiki\\app.py"],
       "cwd": "C:\\path\\to\\mcp-wiki",
       "env": {
         "PYTHONPATH": "C:\\path\\to\\mcp-wiki"
       }
     }
   }
 }
 ```

 Redémarre Claude Desktop et teste :

 ```
 Utilise mcp-wiki pour faire un deep dive Wikidata sur "Google" en français.
 ```

 ### Mode HTTP (API REST)

 Modifier `.env` :

 ```env
 MCP_SERVER_MODE=http
 MCP_SERVER_HOST=127.0.0.1
 MCP_SERVER_PORT=8000
 ```

 Démarrer :

 ```bash
 python app.py
 ```

 API :
 - Documentation : `http://127.0.0.1:8000/docs`
 - Liste des outils : `http://127.0.0.1:8000/tools`

 ### Mode ChatGPT

 Modifier `.env` :

 ```env
 MCP_SERVER_MODE=chatgpt
 MCP_SERVER_PORT=8000
 ```

 Démarrer :

 ```bash
 python app.py
 ```

 Puis exposer le serveur (ex: ngrok) et configurer ChatGPT avec l'URL publique.

 ### Installation dans Windsurf

 Voir `WINDSURF.md`.

 ## 🔎 Ce que tu peux faire avec Wikidata

 Cas d'usage typiques :
 - Trouver l'entité Wikidata la plus plausible d'un sujet
 - Explorer le graphe via les relations (claims)
 - Récupérer les sitelinks (liens Wikipedia/Wikibooks/...) depuis une entité
 - Extraire des identifiants externes (IMDb, VIAF, etc.) et obtenir des URLs cliquables

 Exemples de prompts :

 ```
 Explore l'entité Wikidata "Python" en français et donne-moi :
 1) 15 relations importantes
 2) une liste d'entités liées avec leur description
 3) les sitelinks Wikipedia utiles.
 ```

 ```
 Fais un deep dive Wikidata sur "Elon Musk" et liste les identifiants externes disponibles (avec URLs) ainsi que les liens Wikipedia par langue.
 ```

## Langues supportées

| Code | Langue        | Code | Langue      |
|------|---------------|------|-------------|
| en   | English       | nl   | Nederlands  |
| fr   | Français      | pl   | Polski      |
| de   | Deutsch       | ru   | Русский     |
| es   | Español       | ja   | 日本語       |
| it   | Italiano      | zh   | 中文         |
| pt   | Português     | ar   | العربية     |
| ko   | 한국어         | hi   | हिन्दी       |

## Structure du projet

```
mcp-wiki/
├── app.py                 # Point d'entrée principal
├── requirements.txt       # Dépendances Python
├── .env.example          # Configuration exemple
├── .gitignore            # Fichiers à ignorer
├── README.md             # Documentation
│
├── config/               # Configuration
│   ├── __init__.py
│   ├── settings.py       # Paramètres du serveur
│   └── constants.py      # Constantes
│
├── core/                 # Modules principaux
│   ├── __init__.py
│   ├── mcp_server.py     # Serveur MCP
│   └── server_modes.py   # Modes STDIO/HTTP/SSE/ChatGPT
│
├── services/             # Services externes
│   ├── __init__.py
│   ├── wikipedia_api.py  # Client API Wikipedia
│   └── wikidata_api.py   # Client API Wikidata
│
└── tools/                # Outils MCP
    ├── __init__.py
    ├── wikipedia_tools.py # Outils Wikipedia
    └── wikidata_tools.py  # Outils Wikidata
```

## Développement

### Tester le serveur localement

```bash
# Activer l'environnement virtuel
venv\Scripts\activate

# Lancer le serveur en mode STDIO
python app.py
```

### Ajouter un nouvel outil

1. Créer un nouveau fichier dans `tools/` (ex: `custom_tools.py`)
2. Définir les outils avec le décorateur `@mcp.tool()`
3. Ajouter l'import dans `tools/__init__.py`

## APIs utilisées

- **Wikipedia API** : Recherche de pages
  - Documentation : https://www.mediawiki.org/wiki/API:Main_page
  - **Wikimedia Pageviews API** : Statistiques de vues
   - Documentation : https://wikimedia.org/api/rest_v1/

 - **Wikidata API (MediaWiki)** : Recherche d'entités et récupération de données
   - Documentation : https://www.wikidata.org/w/api.php
   - EntityData JSON : https://www.wikidata.org/wiki/Special:EntityData/Q42.json

## Dépannage

### Erreur "Module not found"

```bash
pip install -r requirements.txt
```

### Erreur "Page not found"

Vérifier que le titre de la page est exact. Les titres Wikipedia sont sensibles à la casse.

### Pas de statistiques disponibles

Certaines pages très récentes peuvent ne pas avoir de données dans l'API Pageviews.

## Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

## Remerciements

- **Wikipedia**, **Wikidata** et la **Wikimedia Foundation** pour leurs APIs ouvertes
- **Anthropic** pour le protocole MCP et Claude Desktop
- **OpenAI** pour ChatGPT
- **detailed.com** pour l'inspiration

## Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation MCP : https://modelcontextprotocol.io/

---

**Note** : Ce projet n'est pas affilié à la Wikimedia Foundation. Veuillez respecter les [conditions d'utilisation](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use) de Wikipedia lors de l'utilisation de ce serveur.
