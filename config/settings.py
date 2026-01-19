"""Configuration settings for MCP Wiki"""

import os
import sys
import logging
from dotenv import load_dotenv

def load_environment():
    """Charge les variables d'environnement"""
    load_dotenv()

def setup_logging():
    """Configure le système de logging"""
    # Log vers stderr ET vers un fichier pour debugging
    log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mcp_server.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),  # Pour Claude Desktop / ChatGPT
            logging.FileHandler(log_file, mode='a', encoding='utf-8')  # Pour debugging
        ]
    )

def get_server_config():
    """Retourne la configuration du serveur MCP"""
    return {
        "mode": os.getenv("MCP_SERVER_MODE", "stdio").lower(),  # stdio, http, sse, chatgpt
        "host": os.getenv("MCP_SERVER_HOST", "127.0.0.1"),
        "port": int(os.getenv("MCP_SERVER_PORT", "8000")),
        "cors_origins": os.getenv("MCP_CORS_ORIGINS", "*").split(",")
    }

def get_wikipedia_config():
    """Retourne la configuration Wikipedia"""
    return {
        "api_url": "https://en.wikipedia.org/w/api.php",
        "pageviews_api_url": "https://wikimedia.org/api/rest_v1",
        "user_agent": os.getenv("WIKIPEDIA_USER_AGENT", "MCP-Wiki/1.0 (https://github.com/yourrepo/mcp-wiki)"),
        "default_language": os.getenv("WIKIPEDIA_DEFAULT_LANGUAGE", "en"),
        "max_results": int(os.getenv("WIKIPEDIA_MAX_RESULTS", "20"))
    }

def get_headers():
    """Retourne les headers HTTP pour les requêtes Wikipedia"""
    config = get_wikipedia_config()
    return {
        "User-Agent": config["user_agent"],
        "Accept": "application/json"
    }
