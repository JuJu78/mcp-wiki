# 📚 Exemples d'utilisation MCP Wiki

Ce document présente des exemples concrets d'utilisation du serveur MCP Wiki avec Claude Desktop ou ChatGPT.

## 🔍 Recherche de pages Wikipedia

### Exemple 1 : Recherche simple

**Prompt Claude/ChatGPT :**
```
Utilise mcp-wiki pour rechercher des pages Wikipedia sur "machine learning" 
en anglais. Montre-moi les 5 premières pages avec leurs statistiques.
```

**Résultat attendu :**
Le chatbot utilisera l'outil `search_wikipedia_keyword` et retournera une liste de 5 pages avec :
- Titre et lien cliquable
- Date de création
- Vues du dernier mois
- Vues de l'année passée
- Vues quotidiennes moyennes
- Changement YoY

### Exemple 2 : Recherche dans une autre langue

**Prompt :**
```
Recherche des pages Wikipedia en français sur "programmation python" 
et affiche les 10 résultats avec leurs statistiques.
```

**Appel MCP :**
```json
{
  "tool": "search_wikipedia_keyword",
  "arguments": {
    "keyword": "programmation python",
    "language": "fr",
    "max_results": 10,
    "include_stats": true
  }
}
```

## 📊 Analyse de popularité

### Exemple 3 : Comparer plusieurs pages

**Prompt :**
```
Compare la popularité des pages Wikipedia suivantes :
- "Python (programming language)"
- "JavaScript"
- "Java (programming language)"
- "C++ (programming language)"

Crée un tableau comparatif avec :
- Titre et lien
- Vues mensuelles
- Vues annuelles
- Changement YoY
- Rang par popularité
```

Le chatbot utilisera plusieurs appels à `get_wikipedia_page_stats` et créera un tableau comparatif.

### Exemple 4 : Tendances d'un sujet

**Prompt :**
```
Analyse les tendances de "artificial intelligence" sur Wikipedia :
1. Recherche toutes les pages liées à ce sujet
2. Identifie les 10 pages les plus populaires
3. Montre le changement YoY pour chacune
4. Fais une synthèse des tendances
```

## 🎯 Cas d'usage avancés

### Exemple 5 : Recherche multi-lingue

**Prompt :**
```
Trouve les pages Wikipedia sur "quantum computing" dans les langues suivantes :
- Anglais
- Français
- Allemand
- Espagnol

Pour chaque langue, montre la page principale et ses statistiques.
```

### Exemple 6 : Détection de sujets émergents

**Prompt :**
```
Recherche des pages Wikipedia sur "generative AI" et identifie celles 
qui ont un changement YoY supérieur à +50%. Ce sont probablement 
des sujets émergents.
```

### Exemple 7 : Analyse de niche

**Prompt :**
```
Trouve toutes les pages Wikipedia liées à "natural language processing" 
et identifie :
1. Les sous-domaines (tokenization, sentiment analysis, etc.)
2. Leur popularité relative
3. Les sujets les plus en croissance
```

## 📈 Visualisation des données

### Exemple 8 : Création de graphiques

**Prompt :**
```
Recherche les 10 pages les plus populaires sur "web development".
Crée un graphique (texte ASCII ou description) montrant :
- Les vues mensuelles de chaque page (en milliers)
- Le changement YoY (en pourcentage)
```

### Exemple 9 : Tableau récapitulatif

**Prompt :**
```
Recherche des pages sur "data science" et crée un tableau Markdown avec :

| Titre | Vues/mois | Vues/an | Quotidien | YoY |
|-------|-----------|---------|-----------|-----|
| ...   | ...       | ...     | ...       | ... |

Trie par vues mensuelles décroissantes.
```

## 🌍 Recherches multilingues

### Exemple 10 : Comparaison entre langues

**Prompt :**
```
Compare la popularité de la page "Artificial Intelligence" entre :
- Wikipedia anglais
- Wikipedia français  
- Wikipedia allemand
- Wikipedia espagnol

Quelle version est la plus consultée ?
```

## 🔬 Analyse de contenu

### Exemple 11 : Découverte de contenus connexes

**Prompt :**
```
Je veux écrire un article sur "deep learning". 
Utilise mcp-wiki pour :
1. Trouver les pages Wikipedia les plus consultées sur ce sujet
2. Identifier les sous-thèmes populaires
3. Suggérer des angles d'article basés sur les tendances
```

### Exemple 12 : Veille technologique

**Prompt :**
```
Fais une veille sur "blockchain technology" :
1. Liste les 15 pages les plus pertinentes
2. Identifie celles avec le plus fort taux de croissance (YoY)
3. Donne-moi un résumé des tendances émergentes
```

## 🎓 Recherche académique

### Exemple 13 : Identification de sujets de recherche

**Prompt :**
```
Trouve des sujets de recherche potentiels dans le domaine de "computer vision" :
- Recherche toutes les pages pertinentes
- Filtre celles avec des vues stables ou en croissance
- Suggère 5 sujets basés sur leur popularité
```

### Exemple 14 : Analyse de citations

**Prompt :**
```
Analyse la popularité des pages Wikipedia suivantes (théories informatiques) :
- "P versus NP problem"
- "Turing machine"
- "Lambda calculus"
- "Halting problem"

Compare leur popularité et suggère laquelle pourrait être la plus 
pertinente pour un article de vulgarisation.
```

## 💡 Astuces

### Utilisation efficace

1. **Soyez spécifique** : Plus votre recherche est précise, meilleurs seront les résultats
2. **Utilisez les bonnes langues** : Certains sujets sont mieux couverts dans certaines langues
3. **Combinez les outils** : Utilisez `search_wikipedia_keyword` pour découvrir, puis `get_wikipedia_page_stats` pour approfondir
4. **Interprétez le YoY** : Un changement YoY élevé indique un sujet en tendance

### Limitations

- Les statistiques sont basées sur les 365 derniers jours maximum
- Certaines pages très récentes peuvent ne pas avoir de données complètes
- Les titres de pages doivent être exacts pour `get_wikipedia_page_stats`

## 🚀 Cas d'usage professionnels

### SEO & Marketing de contenu

```
Identifie les sujets tendances dans [votre niche] pour orienter 
votre stratégie de contenu.
```

### Recherche de marché

```
Compare la popularité de différentes technologies/produits pour 
évaluer l'intérêt du marché.
```

### Veille concurrentielle

```
Surveille l'évolution de la popularité des sujets liés à votre secteur.
```

### Formation & Éducation

```
Identifie les sujets les plus populaires pour créer du contenu éducatif pertinent.
```

---

**Note** : Tous ces exemples sont des suggestions. Claude/ChatGPT interprétera vos prompts et utilisera les outils MCP de manière autonome pour répondre à vos besoins.
