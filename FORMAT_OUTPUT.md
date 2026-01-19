# 📋 Format de sortie des outils MCP Wiki

Ce document décrit le format JSON retourné par chaque outil du serveur MCP Wiki.

## 🔍 `search_wikipedia_keyword`

Recherche des pages Wikipedia liées à un mot-clé et récupère leurs statistiques.

### Paramètres d'entrée

```json
{
  "keyword": "machine learning",
  "language": "en",
  "max_results": 10,
  "include_stats": true
}
```

### Format de sortie (succès)

```json
{
  "success": true,
  "keyword": "machine learning",
  "language": "en",
  "total_results": 10,
  "pages": [
    {
      "title": "Machine Learning",
      "url": "https://en.wikipedia.org/wiki/Machine_Learning",
      "description": "Machine learning is a field of study in artificial intelligence...",
      "page_created": "March 15, 2003",
      "statistics": {
        "past_month_views": 156789,
        "past_year_views": 2145678,
        "daily_views_current_month": 5123,
        "daily_views_last_year_month": 4567,
        "yoy_change_percent": 12.2
      }
    },
    {
      "title": "Deep Learning",
      "url": "https://en.wikipedia.org/wiki/Deep_Learning",
      "description": "Deep learning is a subset of machine learning...",
      "page_created": "June 22, 2012",
      "statistics": {
        "past_month_views": 98456,
        "past_year_views": 1345678,
        "daily_views_current_month": 3215,
        "daily_views_last_year_month": 2890,
        "yoy_change_percent": 11.2
      }
    }
    // ... autres pages
  ]
}
```

### Format de sortie (sans statistiques)

Si `include_stats=false` :

```json
{
  "success": true,
  "keyword": "machine learning",
  "language": "en",
  "total_results": 10,
  "pages": [
    {
      "title": "Machine Learning",
      "url": "https://en.wikipedia.org/wiki/Machine_Learning",
      "description": "Machine learning is a field of study...",
      "page_name": "Machine_Learning"
    }
    // ... autres pages
  ]
}
```

### Format de sortie (erreur)

```json
{
  "success": false,
  "error": "Language 'xx' not supported. Supported languages: en, fr, de, es..."
}
```

### Format de sortie (aucun résultat)

```json
{
  "success": true,
  "keyword": "nonexistent topic xyz",
  "language": "en",
  "total_results": 0,
  "pages": [],
  "message": "No Wikipedia pages found for this keyword"
}
```

## 📊 `get_wikipedia_page_stats`

Récupère les statistiques détaillées pour une page Wikipedia spécifique.

### Paramètres d'entrée

```json
{
  "page_title": "Python (programming language)",
  "language": "en"
}
```

### Format de sortie (succès)

```json
{
  "success": true,
  "page_info": {
    "page_id": 23862,
    "title": "Python (programming language)",
    "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "created": "2025-11-03T12:34:56Z",
    "created_formatted": "November 03, 2025"
  },
  "statistics": {
    "past_month_total_views": 236456,
    "past_year_total_views": 3857311,
    "daily_views_current_month": 5607,
    "daily_views_last_year_same_month": 10618,
    "yoy_change_percent": -47.2
  }
}
```

### Format de sortie (erreur)

```json
{
  "success": false,
  "error": "Page 'Nonexistent Page' not found"
}
```

## 📈 Interprétation des statistiques

### Champs de statistiques

| Champ | Description | Unité | Exemple |
|-------|-------------|-------|---------|
| `past_month_total_views` | Nombre total de vues sur les 30 derniers jours | Entier | 236456 |
| `past_year_total_views` | Nombre total de vues sur les 365 derniers jours | Entier | 3857311 |
| `daily_views_current_month` | Moyenne quotidienne du mois en cours | Entier | 5607 |
| `daily_views_last_year_month` | Moyenne quotidienne du même mois l'an dernier | Entier | 10618 |
| `yoy_change_percent` | Changement année sur année (%) | Float | -47.2 |

### Calcul du YoY (Year-over-Year)

Le changement YoY est calculé comme suit :

```
YoY = ((daily_views_current_month - daily_views_last_year_month) / daily_views_last_year_month) * 100
```

**Interprétation :**
- **YoY > 0** : La page est plus populaire qu'il y a un an (croissance)
- **YoY < 0** : La page est moins populaire qu'il y a un an (déclin)
- **YoY ≈ 0** : La popularité est stable

**Exemples :**
- `+50%` : La page a 50% de vues en plus qu'il y a un an (sujet en forte croissance)
- `-20%` : La page a 20% de vues en moins qu'il y a un an
- `+200%` : La page a triplé en popularité (sujet viral ou émergent)

## 🎨 Formatage pour l'affichage

### Exemple de tableau Markdown

```markdown
| Page | Vues/mois | Vues/an | Quotidien | YoY |
|------|-----------|---------|-----------|-----|
| [Machine Learning](https://...) | 156,789 | 2,145,678 | 5,123 | +12.2% |
| [Deep Learning](https://...) | 98,456 | 1,345,678 | 3,215 | +11.2% |
```

### Exemple de liste

```
📄 Résultats pour "machine learning" :

1. Machine Learning
   🔗 https://en.wikipedia.org/wiki/Machine_Learning
   📅 Créée le: March 15, 2003
   📊 Statistiques:
      - Vues mensuelles: 156,789
      - Vues annuelles: 2,145,678
      - Vues quotidiennes (actuel): 5,123
      - Changement YoY: +12.2% ↗️

2. Deep Learning
   🔗 https://en.wikipedia.org/wiki/Deep_Learning
   ...
```

## 🔢 Valeurs numériques

### Formatage des nombres

Les nombres de vues peuvent être très grands. Il est recommandé de les formatter :

```javascript
// Format avec séparateurs de milliers
156789 → "156,789"
2145678 → "2,145,678"

// Format abrégé
156789 → "156.8K"
2145678 → "2.1M"
```

### Formatage des pourcentages

```javascript
12.2 → "+12.2%"
-47.2 → "-47.2%"
0.0 → "0.0%"
```

### Indicateurs visuels

```
+50% ↗️ (forte croissance)
+10% ↗️ (croissance)
0% → (stable)
-10% ↘️ (déclin)
-50% ↘️ (fort déclin)
```

## 🌐 Codes de langue

Liste des codes ISO 639-1 supportés :

| Code | Langue | Code | Langue |
|------|--------|------|--------|
| `en` | English | `nl` | Nederlands |
| `fr` | Français | `pl` | Polski |
| `de` | Deutsch | `ru` | Русский |
| `es` | Español | `ja` | 日本語 |
| `it` | Italiano | `zh` | 中文 |
| `pt` | Português | `ar` | العربية |
| `ko` | 한국어 | `hi` | हिन्दी |

## ⚠️ Gestion des erreurs

### Types d'erreurs communes

1. **Page non trouvée**
```json
{
  "success": false,
  "error": "Page 'Xyz' not found"
}
```

2. **Langue non supportée**
```json
{
  "success": false,
  "error": "Language 'xx' not supported. Supported languages: ..."
}
```

3. **Paramètre invalide**
```json
{
  "success": false,
  "error": "max_results must be between 1 and 50"
}
```

4. **Statistiques indisponibles**
```json
{
  "title": "Very New Page",
  "statistics": null,
  "error": "Statistics not available for this page"
}
```

5. **Erreur API**
```json
{
  "success": false,
  "error": "Wikipedia API error: [détails]"
}
```

## 📝 Bonnes pratiques

1. **Toujours vérifier `success`** avant de traiter les données
2. **Gérer les cas `null`** pour les statistiques indisponibles
3. **Formatter les nombres** pour améliorer la lisibilité
4. **Ajouter des indicateurs visuels** (émojis, couleurs) pour le YoY
5. **Trier les résultats** selon vos besoins (popularité, changement YoY, etc.)

---

Pour plus d'informations, consultez le [README.md](README.md) et [EXAMPLES.md](EXAMPLES.md).
