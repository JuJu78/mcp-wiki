# Windsurf - Installation du serveur MCP

## Prérequis

- Python 3.10+ recommandé
- Dépendances installées (voir `requirements.txt`)

## Installation

1. Créer un environnement virtuel

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Copier la configuration

Crée un fichier `.env` à partir de `.env.example` :

```bash
copy .env.example .env
```

## Configuration du MCP dans Windsurf

Dans Windsurf, ajoute un serveur MCP en mode **stdio**.

Paramètres recommandés :

- **Command** : `python`
- **Args** : `app.py`
- **Working directory** : le dossier du repo (ex: `d:\mcp-wiki`)
- **Environment** :
  - `PYTHONPATH=d:\mcp-wiki`

### Alternative (si tu veux pointer vers un Python de venv)

- **Command** : `d:\mcp-wiki\venv\Scripts\python.exe`
- **Args** : `app.py`

## Test rapide

Dans Windsurf, demande par exemple :

```
Utilise mcp-wiki pour extraire tous les liens internes de la page Wikipedia "SEO" en français.
```
