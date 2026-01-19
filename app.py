#!/usr/bin/env python3
"""MCP Wiki Server - Point d'entrée principal

Serveur MCP pour rechercher des pages Wikipedia et obtenir leurs statistiques.
Supporte plusieurs modes: STDIO (Claude Desktop), HTTP, SSE, et ChatGPT.
"""

import logging
from config.settings import setup_logging, load_environment
from core.mcp_server import create_mcp_server
from tools import register_all_tools

def main():
    """Point d'entrée principal du serveur MCP Wiki"""
    
    # Configuration de l'environnement et du logging
    load_environment()
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=== Démarrage du serveur MCP Wiki ===")
    
    try:
        # Création du serveur MCP multi-mode
        mcp_server, config = create_mcp_server()
        logger.info("Instance MCP multi-mode créée avec succès")
        
        # Enregistrement de tous les outils
        register_all_tools(mcp_server)
        logger.info("Outils MCP enregistrés avec succès")
        
        # Démarrage du serveur selon le mode configuré
        mode = config.get("mode", "stdio")
        logger.info(f"✅ Serveur MCP Wiki prêt à recevoir des requêtes en mode {mode.upper()}")
        
        if mode == "http":
            mcp_server.run_http(config)
        elif mode == "sse":
            mcp_server.run_sse(config)
        elif mode == "chatgpt":
            mcp_server.run_chatgpt(config)
        else:  # stdio par défaut
            logger.info("🔌 Démarrage en mode STDIO (Claude Desktop / ChatGPT)")
            mcp_server.run_stdio()
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage du serveur : {e}")
        raise

if __name__ == "__main__":
    main()
