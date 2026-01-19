# MCP Wiki - Wikipedia Internal Links Extractor

Serveur MCP (Model Context Protocol) pour extraire tous les **liens internes** (ancres) d'une page Wikipedia à partir d'un mot-clé.

## 🎯 Fonctionnalités

- **Extraction de liens internes** : Récupère tous les liens (ancres) présents dans le contenu d'une page Wikipedia
- **Recherche par mot-clé** : Trouve automatiquement la page correspondante puis extrait ses liens
- **Multi-langues** : Support de 14 langues Wikipedia (en, fr, de, es, it, pt, nl, pl, ru, ja, zh, ar, ko, hi)
- **Multi-modes** : Compatible avec Claude Desktop, ChatGPT, et API HTTP/SSE
- **Liens avec ancres** : Retourne le texte de l'ancre + l'URL de destination + le titre de la page liée

## 📊 Données extraites

Pour chaque lien interne trouvé dans une page Wikipedia, le serveur retourne :

- **Texte de l'ancre** : Le texte cliquable (ex: "application web", "Google", "PageRank")
- **Titre de la page liée** : Titre de la page Wikipedia de destination
- **URL complète** : Lien direct vers la page Wikipedia (ex: https://fr.wikipedia.org/wiki/Google)
- **Nombre total de liens** : Comptage du nombre de liens internes dans la page

### Exemple pour la page "Optimisation pour les moteurs de recherche"

La page contient **114 liens internes** dont :
- "application web" → https://fr.wikipedia.org/wiki/Application_web (2,135 vues/mois)
- "Google" → https://fr.wikipedia.org/wiki/Google
- "PageRank" → https://fr.wikipedia.org/wiki/PageRank (1,759 vues/mois)
- "référencement" → https://fr.wikipedia.org/wiki/Référencement
- "Page web" → https://fr.wikipedia.org/wiki/Page_web (3,053 vues/mois - la plus populaire !)
- et 109 autres liens...

**NOUVEAU** : Vous pouvez maintenant récupérer les **statistiques de vues** pour chaque lien !

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

Éditer le fichier `.env` selon vos besoins :

```env
# Mode du serveur
MCP_SERVER_MODE=stdio  # stdio, http, sse, chatgpt

# Configuration Wikipedia (optionnel)
WIKIPEDIA_DEFAULT_LANGUAGE=en
WIKIPEDIA_MAX_RESULTS=20
```

## 📝 Utilisation

### Mode STDIO (Claude Desktop)

1. Ajouter dans votre configuration Claude Desktop (`claude_desktop_config.json`) :

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

2. Redémarrer Claude Desktop

3. Utiliser les outils dans Claude :

**Exemple 1 : Liens seuls (rapide - ~2 secondes)**
```
Utilise mcp-wiki pour extraire tous les liens internes de la page Wikipedia 
"Optimisation pour les moteurs de recherche" en français
```

**Exemple 2 : Liens + statistiques (complet - ~20 secondes pour 20 liens)**
```
Utilise mcp-wiki pour extraire les liens internes de la page Wikipedia 
"Optimisation pour les moteurs de recherche" en français, 
avec les statistiques de vues pour les 20 premiers liens
```

### Mode HTTP (API REST)

1. Modifier `.env` :
```env
MCP_SERVER_MODE=http
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8000
```

2. Démarrer le serveur :
```bash
python app.py
```

3. Accéder à l'API :
- Documentation : `http://127.0.0.1:8000/docs`
- Liste des outils : `http://127.0.0.1:8000/tools`

### Installation dans Windsurf

Voir `WINDSURF.md`.

### Mode ChatGPT

1. Modifier `.env` :
```env
MCP_SERVER_MODE=chatgpt
MCP_SERVER_PORT=8000
```

2. Démarrer le serveur :
```bash
python app.py
```

3. Utiliser ngrok pour exposer le serveur :
```bash
ngrok http 8000
```

4. Ajouter le serveur dans ChatGPT (Deep Research) avec l'URL ngrok

## 🛠️ Outils MCP disponibles

### 1. `get_wikipedia_internal_links` ⭐ (Principal)

Extrait tous les liens internes (ancres) d'une page Wikipedia à partir d'un mot-clé.

**✨ NOUVEAU** : Peut maintenant récupérer les **statistiques de vues** pour chaque lien !

**Paramètres :**
- `keyword` (str, requis) : Terme de recherche pour trouver la page Wikipedia
- `language` (str, optionnel) : Code langue (défaut: "fr")
- `include_stats` (bool, optionnel) : Récupérer les statistiques de vues (défaut: false)
- `max_links_with_stats` (int, optionnel) : Nombre max de liens avec stats, 1-100 (défaut: 20)

**Exemples dans Claude :**

*Sans statistiques (rapide ~2s) :*
```
Utilise mcp-wiki pour extraire tous les liens internes de la page Wikipedia 
sur "optimisation pour les moteurs de recherche" en français
```

*Avec statistiques (complet ~20s pour 20 liens) :*
```
Utilise mcp-wiki pour extraire les liens internes de la page "SEO" en français 
avec les statistiques de vues pour les 20 premiers liens. 
Crée ensuite un tableau trié par popularité.
```

**Résultat (sans statistiques) :**
```json
{
  "success": true,
  "page_title": "Optimisation pour les moteurs de recherche",
  "source_page_url": "https://fr.wikipedia.org/wiki/Optimisation_pour_les_moteurs_de_recherche",
  "total_internal_links": 114,
  "stats_included": false,
  "internal_links": [
    {
      "anchor_text": "application web",
      "linked_page_title": "Application web",
      "url": "https://fr.wikipedia.org/wiki/Application_web"
    }
    // ... 113 autres liens
  ]
}
```

**Résultat (avec statistiques) :**
```json
{
  "success": true,
  "page_title": "Optimisation pour les moteurs de recherche",
  "total_internal_links": 114,
  "stats_included": true,
  "stats_count": 20,
  "internal_links": [
    {
      "anchor_text": "Page web",
      "linked_page_title": "Page web",
      "url": "https://fr.wikipedia.org/wiki/Page_web",
      "statistics": {
        "past_month_total_views": 3053,
        "past_year_total_views": 41084,
        "daily_views_current_month": 76,
        "yoy_change_percent": -27.3
      },
      "page_info": {
        "title": "Page web",
        "url": "https://fr.wikipedia.org/wiki/Page_web",
        "created": "2025-11-04T08:08:06Z"
      }
    },
    {
      "anchor_text": "Application web",
      "linked_page_title": "Application web",
      "url": "https://fr.wikipedia.org/wiki/Application_web",
      "statistics": {
        "past_month_total_views": 2135,
        "past_year_total_views": 33876,
        "daily_views_current_month": 49,
        "yoy_change_percent": -33.4
      }
    }
    // ... 18 autres liens avec statistiques + 94 sans statistiques
  ]
}
```

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

## 🌍 Langues supportées

| Code | Langue        | Code | Langue      |
|------|---------------|------|-------------|
| en   | English       | nl   | Nederlands  |
| fr   | Français      | pl   | Polski      |
| de   | Deutsch       | ru   | Русский     |
| es   | Español       | ja   | 日本語       |
| it   | Italiano      | zh   | 中文         |
| pt   | Português     | ar   | العربية     |
| ko   | 한국어         | hi   | हिन्दी       |

## 📁 Structure du projet

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
│   └── wikipedia_api.py  # Client API Wikipedia
│
└── tools/                # Outils MCP
    ├── __init__.py
    └── wikipedia_tools.py # Outils de recherche
```

## 🔧 Développement

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

## 📚 APIs utilisées

- **Wikipedia API** : Recherche de pages
  - Documentation : https://www.mediawiki.org/wiki/API:Main_page
  
- **Wikimedia Pageviews API** : Statistiques de vues
  - Documentation : https://wikimedia.org/api/rest_v1/

## 🐛 Dépannage

### Erreur "Module not found"

```bash
pip install -r requirements.txt
```

### Erreur "Page not found"

Vérifier que le titre de la page est exact. Les titres Wikipedia sont sensibles à la casse.

### Pas de statistiques disponibles

Certaines pages très récentes peuvent ne pas avoir de données dans l'API Pageviews.

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit vos changements (`git commit -am 'Ajout d'une nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

## 🙏 Remerciements

- **Wikipedia** et **Wikimedia Foundation** pour leurs APIs ouvertes
- **Anthropic** pour le protocole MCP et Claude Desktop
- **OpenAI** pour ChatGPT
- **detailed.com** pour l'inspiration

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation MCP : https://modelcontextprotocol.io/

---

**Note** : Ce projet n'est pas affilié à la Wikimedia Foundation. Veuillez respecter les [conditions d'utilisation](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use) de Wikipedia lors de l'utilisation de ce serveur.
