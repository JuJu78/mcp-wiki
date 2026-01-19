"""MCP Server initialization and configuration"""

import logging
import sys
from config.settings import get_server_config
from core.server_modes import MCPServerMultiMode

logger = logging.getLogger(__name__)

def create_mcp_server():
    """Crée et configure l'instance du serveur MCP multi-mode"""
    config = get_server_config()
    mode = config.get("mode", "stdio")
    
    logger.info(f"Configuration du serveur MCP en mode: {mode.upper()}")
    
    # Créer le serveur multi-mode
    server = MCPServerMultiMode("mcp-wiki")
    
    return server, config
