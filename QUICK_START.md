# 🚀 Guide de démarrage rapide MCP Wiki - Extraction de liens internes

## Installation en 3 étapes

### Étape 1 : Installer les dépendances

```bash
cd d:\mcp-wiki
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Étape 2 : Configurer Claude Desktop

Copier le contenu de `claude_desktop_config.json` dans votre fichier de configuration Claude Desktop :

**Emplacement du fichier :**
- Windows : `%APPDATA%\Claude\claude_desktop_config.json`
- Mac : `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux : `~/.config/Claude/claude_desktop_config.json`

**Ou ajouter cette section dans votre configuration existante :**

```json
{
  "mcpServers": {
    "mcp-wiki": {
      "command": "python",
      "args": ["{{ path_to_mcp_wiki }}\\app.py"],
      "cwd": "{{ path_to_mcp_wiki }}",
      "env": {
        "PYTHONPATH": "{{ path_to_mcp_wiki }}"
      }
    }
  }
}
```

### Étape 3 : Redémarrer Claude Desktop

Redémarrez complètement l'application Claude Desktop pour qu'elle charge le nouveau serveur MCP.

## Windsurf

Pour installer le serveur MCP dans Windsurf, voir `WINDSURF.md`.

## ✅ Test

Dans Claude Desktop, essayez cette requête :

```
Utilise mcp-wiki pour extraire tous les liens internes de la page Wikipedia 
"Optimisation pour les moteurs de recherche" en français
```

Claude devrait utiliser l'outil `get_wikipedia_internal_links` et vous retourner :
- Le titre de la page trouvée
- L'URL source de la page
- Le nombre total de liens internes (114 pour cette page)
- Liste complète des liens avec :
  - Texte de l'ancre (ex: "application web", "Google", "PageRank")
  - URL de destination
  - Titre de la page liée

## 🎯 Exemples d'utilisation

### Recherche simple en anglais

```
Recherche les pages Wikipedia sur "artificial intelligence" en anglais
```

### Recherche en français

```
Utilise mcp-wiki pour trouver des pages sur "intelligence artificielle" 
en français avec un maximum de 10 résultats
```

### Statistiques d'une page spécifique

```
Donne-moi les statistiques complètes de la page Wikipedia 
"Machine learning" en anglais
```

### Comparaison de popularité

```
Compare la popularité des pages Wikipedia suivantes : 
"Python (programming language)", "JavaScript", et "Java (programming language)"
```

## 🔧 Dépannage

### Claude ne voit pas l'outil mcp-wiki

1. Vérifier que le chemin dans `claude_desktop_config.json` est correct
2. Vérifier que l'environnement virtuel contient toutes les dépendances
3. Redémarrer complètement Claude Desktop

### Erreur "Module not found"

```bash
cd d:\mcp-wiki
venv\Scripts\activate
pip install -r requirements.txt
```

### Voir les logs

Les logs sont enregistrés dans `d:\mcp-wiki\mcp_server.log`

```bash
type mcp_server.log  # Windows
# ou
cat mcp_server.log  # Linux/Mac
```

## 📚 Documentation complète

Consultez [README.md](README.md) pour plus de détails sur :
- Toutes les langues supportées
- Configuration avancée
- Mode HTTP/SSE/ChatGPT
- APIs utilisées

## 💡 Astuce

Vous pouvez créer des raccourcis dans Claude :

```
Crée-moi un tableau comparatif des pages Wikipedia sur ces technologies : 
[liste de technologies]

Pour chaque page, affiche :
- Titre et lien
- Vues du dernier mois
- Changement YoY
- Rang par popularité
```

Claude utilisera automatiquement mcp-wiki pour récupérer toutes les données !
