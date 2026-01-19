# 🆕 Nouvelle fonctionnalité : Statistiques pour les liens internes

## ✅ Implémentée avec succès !

L'outil `get_wikipedia_internal_links` peut maintenant récupérer les **statistiques de vues** pour chaque lien interne trouvé.

## 📊 Ce que ça permet

Vous pouvez maintenant :
1. **Extraire tous les liens** d'une page Wikipedia
2. **Récupérer les statistiques** pour chaque lien (vues, croissance, etc.)
3. **Analyser la popularité** des pages liées
4. **Créer des tableaux** triés par popularité

## 🎯 Cas d'usage

### 1. Identifier les pages liées les plus populaires

```
Utilise mcp-wiki pour extraire les liens internes de "SEO" en français 
avec les statistiques pour les 20 premiers liens.
Crée un tableau trié par nombre de vues (30 jours).
```

**Résultat pour la page "Optimisation pour les moteurs de recherche"** :

| Rang | Page liée | Vues (30j) | Évolution YoY |
|------|-----------|------------|---------------|
| 1 | Page web | 3,053 | -27.3% |
| 2 | Application web | 2,135 | -33.4% |
| 3 | PageRank | 1,759 | -12.9% |
| 4 | Page SERP | 787 | -87.1% |
| 5 | SEO (homonymie) | 31 | -87.5% |

### 2. Analyse de maillage interne par popularité

```
Extrait les liens de "Python (programming language)" en anglais 
avec les stats pour 50 liens, puis montre-moi :
- Le top 10 par popularité
- Les pages en forte croissance (YoY > 50%)
- Les pages en déclin (YoY < -50%)
```

### 3. Comparaison entre langues

```
Compare le maillage de la page "Artificial Intelligence" :
1. Version anglaise avec stats pour 30 liens
2. Version française avec stats pour 30 liens

Identifie les pages communes et leurs différences de popularité.
```

## 🛠️ Paramètres

### `include_stats` (bool, défaut: false)

Active la récupération des statistiques pour les liens.

- `false` : Rapide (~2 secondes), liens seuls
- `true` : Plus lent (~1 seconde par lien), liens + statistiques complètes

### `max_links_with_stats` (int, défaut: 20)

Nombre maximum de liens pour lesquels récupérer les statistiques (1-100).

**Temps estimés** :
- 10 liens : ~10 secondes
- 20 liens : ~20 secondes
- 50 liens : ~50 secondes
- 100 liens : ~100 secondes (1min 40s)

## 📈 Données retournées

Pour chaque lien avec statistiques, vous obtenez :

```json
{
  "anchor_text": "Page web",
  "linked_page_title": "Page web",
  "url": "https://fr.wikipedia.org/wiki/Page_web",
  "statistics": {
    "past_month_total_views": 3053,
    "past_year_total_views": 41084,
    "daily_views_current_month": 76,
    "daily_views_last_year_same_month": 104,
    "yoy_change_percent": -27.3
  },
  "page_info": {
    "title": "Page web",
    "url": "https://fr.wikipedia.org/wiki/Page_web",
    "created": "2025-11-04T08:08:06Z"
  }
}
```

### Statistiques disponibles

- **`past_month_total_views`** : Total des vues sur les 30 derniers jours
- **`past_year_total_views`** : Total des vues sur l'année passée (365 jours)
- **`daily_views_current_month`** : Moyenne quotidienne du mois en cours
- **`daily_views_last_year_same_month`** : Moyenne quotidienne du même mois l'année dernière
- **`yoy_change_percent`** : Changement année sur année (Year over Year) en %

### Informations de page

- **`title`** : Titre de la page
- **`url`** : URL complète
- **`created`** : Date de création de la page (format ISO)

## 🚀 Exemples d'utilisation

### Exemple 1 : Top 10 des liens populaires

```
Prompt:
Utilise mcp-wiki pour extraire les liens de "Machine learning" en anglais 
avec les stats pour 30 liens. Montre-moi le top 10 par popularité.

Résultat attendu:
Claude va créer un tableau avec les 10 pages liées les plus populaires.
```

### Exemple 2 : Analyse de croissance

```
Prompt:
Extrait les liens de "ChatGPT" en anglais avec stats pour 50 liens.
Identifie les pages en forte croissance (YoY > 100%) et celles en déclin (YoY < -50%).

Résultat attendu:
Claude va segmenter les liens selon leur évolution.
```

### Exemple 3 : Audit de maillage

```
Prompt:
Analyse le maillage de "Search engine optimization" en anglais.
Récupère les stats pour 40 liens et crée un rapport avec :
1. Nombre total de liens
2. Top 5 pages liées les plus populaires
3. Moyenne de vues des pages liées
4. Pages avec moins de 100 vues/mois (opportunités d'amélioration)

Résultat attendu:
Claude va créer un rapport d'audit complet.
```

### Exemple 4 : Export pour analyse

```
Prompt:
Extrait tous les liens de "Python (programming language)" en anglais 
avec stats pour 100 liens. Présente les données au format tableau CSV 
que je pourrais copier dans Excel.

Résultat attendu:
Claude va formater les données en CSV.
```

## ⚡ Performance

### Optimisations implémentées

✅ Traitement séquentiel pour éviter de surcharger les APIs  
✅ Limitation configurable du nombre de liens  
✅ Gestion d'erreurs pour chaque lien (continue même si un lien échoue)  
✅ Logs détaillés du progrès  

### Recommandations

- **Pour exploration rapide** : 10-20 liens (~20 secondes)
- **Pour analyse approfondie** : 30-50 liens (~45 secondes)
- **Pour audit complet** : 100 liens (~100 secondes)

## 🔍 Gestion des erreurs

Si une page liée n'a pas de statistiques disponibles :

```json
{
  "anchor_text": "Page inexistante",
  "linked_page_title": "Page inexistante",
  "url": "https://fr.wikipedia.org/wiki/Page_inexistante",
  "statistics": null,
  "stats_error": "Page not found or no data available"
}
```

Le processus continue pour les autres liens.

## 💡 Idées d'utilisation avancées

### Content Strategy

Identifiez les sujets populaires liés à votre thématique pour créer du contenu pertinent.

### SEO Research

Analysez le maillage interne de pages Wikipedia de votre secteur pour identifier :
- Les termes importants (pages très liées)
- Les tendances (pages en croissance)
- Les opportunités (pages peu connues mais pertinentes)

### Competitive Analysis

Comparez le maillage de pages similaires dans différentes langues pour identifier des variations culturelles.

### Data Analysis

Exportez les données pour des analyses plus poussées dans Excel, Python, R, etc.

## 📝 Notes techniques

- Les statistiques sont récupérées via l'API Wikimedia Pageviews
- Les données de vues sont mises à jour quotidiennement par Wikimedia
- Le calcul YoY compare le mois en cours avec le même mois l'année dernière
- Les pages très récentes peuvent avoir des données incomplètes

---

**Créé le** : 4 novembre 2025  
**Version** : 2.1 (Statistiques pour liens internes)  
**Status** : ✅ TESTÉ ET OPÉRATIONNEL
