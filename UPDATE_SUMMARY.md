# 🎉 Mise à jour MCP-Wiki - Extraction de liens internes

## ✅ Fonctionnalité implémentée

Le serveur MCP-Wiki a été mis à jour pour répondre à votre besoin : **extraire tous les liens internes (ancres) d'une page Wikipedia**.

## 🆕 Nouvel outil principal : `get_wikipedia_internal_links`

Cet outil permet de :
1. Trouver une page Wikipedia à partir d'un mot-clé
2. Extraire **tous les liens internes** (ancres) présents dans le contenu
3. Retourner pour chaque lien :
   - Le **texte de l'ancre** (texte cliquable)
   - Le **titre de la page liée**
   - L'**URL complète** de la page de destination

### Exemple concret

Pour la page **"Optimisation pour les moteurs de recherche"** (votre exemple) :

```json
{
  "success": true,
  "page_title": "Optimisation pour les moteurs de recherche",
  "source_page_url": "https://fr.wikipedia.org/wiki/Optimisation_pour_les_moteurs_de_recherche",
  "total_internal_links": 114,
  "internal_links": [
    {
      "anchor_text": "application web",
      "linked_page_title": "Application web",
      "url": "https://fr.wikipedia.org/wiki/Application_web"
    },
    {
      "anchor_text": "page de résultats d'un moteur de recherche",
      "linked_page_title": "Page de résultats d'un moteur de recherche",
      "url": "https://fr.wikipedia.org/wiki/Page_de_r%C3%A9sultats_d%27un_moteur_de_recherche"
    },
    {
      "anchor_text": "référencement",
      "linked_page_title": "Référencement",
      "url": "https://fr.wikipedia.org/wiki/R%C3%A9f%C3%A9rencement"
    },
    {
      "anchor_text": "Google",
      "linked_page_title": "Google",
      "url": "https://fr.wikipedia.org/wiki/Google"
    },
    {
      "anchor_text": "PageRank",
      "linked_page_title": "PageRank",
      "url": "https://fr.wikipedia.org/wiki/PageRank"
    }
    // ... et 109 autres liens !
  ]
}
```

## ✅ Tests réussis

J'ai testé l'outil avec votre exemple exact :

```bash
python test_internal_links.py
```

**Résultats :**

✅ Page trouvée : "Optimisation pour les moteurs de recherche"  
✅ 114 liens internes extraits  
✅ Tous les liens que vous avez mentionnés sont présents :
- ✅ "application web" → https://fr.wikipedia.org/wiki/Application_web
- ✅ "page de résultats d'un moteur de recherche" → Page SERP
- ✅ "référencement" → https://fr.wikipedia.org/wiki/Référencement
- ✅ "Google" → https://fr.wikipedia.org/wiki/Google
- ✅ "PageRank" → https://fr.wikipedia.org/wiki/PageRank

## 🔧 Modifications techniques

### Fichiers modifiés :

1. **`services/wikipedia_api.py`** 
   - Ajout de la méthode `get_internal_links()`
   - Utilise BeautifulSoup pour parser le HTML
   - Extrait uniquement les liens dans le contenu principal

2. **`tools/wikipedia_tools.py`**
   - Ajout de l'outil MCP `get_wikipedia_internal_links`
   - Recherche automatique de la page via mot-clé
   - Extraction et formatage des liens

3. **`requirements.txt`**
   - Ajout de `beautifulsoup4` (parser HTML)
   - Ajout de `lxml` (parser XML/HTML rapide)

### Nouvelles dépendances installées :

```bash
pip install beautifulsoup4 lxml
```

## 📝 Utilisation dans Claude Desktop

### Exemple 1 : Extraction simple

```
Utilise mcp-wiki pour extraire tous les liens internes de la page 
"Optimisation pour les moteurs de recherche" en français
```

### Exemple 2 : Analyse de maillage interne

```
Extrait les liens internes de la page Wikipedia sur "Python (programming language)"
en anglais et montre-moi les 20 premiers liens
```

### Exemple 3 : Comparaison entre pages

```
Compare le maillage interne entre les pages Wikipedia :
- "SEO" en français
- "Search engine optimization" en anglais

Dis-moi combien de liens chaque page contient et liste les 10 premiers liens de chaque page.
```

## 🎯 Cas d'usage

Cet outil est parfait pour :

1. **Analyse de maillage interne** : Voir comment Wikipedia structure ses liens
2. **Découverte de sujets connexes** : Trouver tous les sujets liés à une page
3. **Recherche de termes** : Identifier les concepts importants via les ancres
4. **Étude de contenu** : Analyser la richesse sémantique d'une page
5. **SEO & Content Marketing** : S'inspirer de la structure de liens de Wikipedia

## 📊 Performance

- **Temps de réponse** : ~2-3 secondes par page
- **API utilisée** : Wikipedia API (action=parse)
- **Limitation** : Extrait uniquement les liens du contenu principal (exclut footer, sidebar, etc.)

## 🔄 Outils conservés

Les 2 autres outils sont toujours disponibles :

1. **`search_wikipedia_keyword`** : Recherche de pages avec statistiques de vues
2. **`get_wikipedia_page_stats`** : Stats de vues d'une page spécifique

Vous pouvez combiner ces outils ! Par exemple :
```
1. Utilise get_wikipedia_internal_links pour extraire les liens de la page "SEO"
2. Ensuite, pour chaque lien, récupère les statistiques de vues avec get_wikipedia_page_stats
3. Crée un tableau triant les pages liées par popularité
```

## 📚 Documentation mise à jour

- ✅ `README.md` : Fonctionnalité principale mise à jour
- ✅ `QUICK_START.md` : Exemples d'utilisation mis à jour
- ✅ `test_internal_links.py` : Nouveau script de test
- ✅ `UPDATE_SUMMARY.md` : Ce fichier (résumé de la mise à jour)

## 🚀 Prochaines étapes

1. **Redémarrer Claude Desktop** si le serveur MCP est déjà configuré
2. **Tester** avec votre exemple : "Optimisation pour les moteurs de recherche"
3. **Explorer** d'autres pages Wikipedia pour analyser leur maillage

## 💡 Suggestions d'amélioration futures

Si vous souhaitez aller plus loin, voici des idées :

1. **Filtrage par type de lien** : Séparer les liens selon leur position (intro, corps, références)
2. **Profondeur de maillage** : Extraire les liens des pages liées (niveau 2, 3, etc.)
3. **Graphe de liens** : Visualiser le réseau de liens entre pages
4. **Export CSV/JSON** : Exporter les liens dans différents formats
5. **Statistiques combinées** : Ajouter automatiquement les stats de vues pour chaque lien

---

**Créé le** : 4 novembre 2025  
**Version** : 2.0 (Extraction de liens internes)  
**Status** : ✅ TESTÉ ET OPÉRATIONNEL
