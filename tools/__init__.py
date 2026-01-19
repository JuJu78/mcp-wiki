"""Tools module for MCP Wiki"""

def register_all_tools(mcp):
    """Enregistre tous les outils MCP avec chargement paresseux"""
    
    # Adaptation pour le serveur multi-mode
    if hasattr(mcp, 'register_tool'):
        # Mode multi-mode (HTTP/SSE)
        register_all_tools_multimode(mcp)
    else:
        # Mode FastMCP traditionnel (STDIO)
        register_all_tools_fastmcp(mcp)

def register_all_tools_multimode(mcp):
    """Enregistre tous les outils pour le serveur multi-mode (HTTP/SSE)"""
    
    # Import de tous les modules d'outils
    from .wikipedia_tools import register_wikipedia_tools
    from .wikidata_tools import register_wikidata_tools
    
    # Adaptation des fonctions d'enregistrement pour le mode multi-mode
    def adapt_tool_registration(register_func):
        """Adapte une fonction d'enregistrement FastMCP pour le mode multi-mode"""
        class MockMCP:
            def __init__(self, real_mcp):
                self.real_mcp = real_mcp
                
            def tool(self, name=None, description=""):
                def decorator(func):
                    tool_name = name or func.__name__
                    self.real_mcp.register_tool(tool_name, func, description)
                    return func
                return decorator
        
        mock_mcp = MockMCP(mcp)
        register_func(mock_mcp)
    
    # Enregistrer tous les outils
    adapt_tool_registration(register_wikipedia_tools)
    adapt_tool_registration(register_wikidata_tools)

def register_all_tools_fastmcp(mcp):
    """Enregistre tous les outils pour FastMCP (mode STDIO)"""
    
    # Import de tous les modules d'outils
    from .wikipedia_tools import register_wikipedia_tools
    from .wikidata_tools import register_wikidata_tools
    
    # Enregistrer tous les outils directement
    register_wikipedia_tools(mcp)
    register_wikidata_tools(mcp)
