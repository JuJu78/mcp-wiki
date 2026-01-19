"""Serveur MCP multi-mode : STDIO, HTTP et SSE"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

class MCPServerMultiMode:
    """Serveur MCP supportant plusieurs modes de communication"""
    
    def __init__(self, name: str = "mcp-wiki"):
        self.name = name
        self.mcp = FastMCP(name)
        self.app = None
        self.tools = {}
        
    def register_tool(self, name: str, func, description: str = ""):
        """Enregistre un outil MCP"""
        self.mcp.tool(name=name, description=description)(func)
        self.tools[name] = {
            "function": func,
            "description": description
        }
        
    def run_stdio(self):
        """Lance le serveur en mode STDIO (mode par défaut MCP)"""
        logger.info("🔌 Démarrage en mode STDIO")
        self.mcp.run()
        
    def setup_fastapi(self, config: Dict[str, Any]):
        """Configure l'application FastAPI pour HTTP et SSE"""
        self.app = FastAPI(
            title="MCP Wiki",
            description="Serveur MCP pour Wikipedia avec support HTTP et SSE",
            version="1.0.0"
        )
        
        # Configuration CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=config.get("cors_origins", ["*"]),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Routes MCP
        self.setup_mcp_routes()
        
    def setup_mcp_routes(self):
        """Configure les routes MCP pour HTTP"""
        
        @self.app.get("/")
        async def root():
            return {
                "name": self.name,
                "version": "1.0.0",
                "protocol": "mcp",
                "modes": ["stdio", "http", "sse"],
                "tools_count": len(self.tools)
            }
            
        @self.app.get("/tools")
        async def list_tools():
            """Liste tous les outils disponibles"""
            tools_list = []
            for name, info in self.tools.items():
                tools_list.append({
                    "name": name,
                    "description": info["description"]
                })
            return {
                "jsonrpc": "2.0",
                "result": {
                    "tools": tools_list
                }
            }
            
        @self.app.post("/tools/call")
        async def call_tool(request: Request):
            """Appelle un outil MCP via HTTP"""
            try:
                data = await request.json()
                tool_name = data.get("name")
                arguments = data.get("arguments", {})
                
                if tool_name not in self.tools:
                    return {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32601,
                            "message": f"Tool '{tool_name}' not found"
                        },
                        "id": data.get("id")
                    }
                
                # Exécuter l'outil
                tool_func = self.tools[tool_name]["function"]
                result = await self._execute_tool(tool_func, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": str(result)
                            }
                        ]
                    },
                    "id": data.get("id")
                }
                
            except Exception as e:
                logger.error(f"Erreur lors de l'appel d'outil: {e}")
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    },
                    "id": data.get("id", None)
                }
                
        @self.app.get("/sse")
        async def sse_endpoint():
            """Point d'entrée pour Server-Sent Events"""
            return StreamingResponse(
                self.sse_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
            
        @self.app.post("/sse/call")
        async def sse_call_tool(request: Request):
            """Appelle un outil via SSE"""
            try:
                data = await request.json()
                tool_name = data.get("name")
                arguments = data.get("arguments", {})
                
                if tool_name not in self.tools:
                    return {"error": f"Tool '{tool_name}' not found"}
                
                # Exécuter l'outil et streamer le résultat
                return StreamingResponse(
                    self.sse_tool_generator(tool_name, arguments),
                    media_type="text/event-stream"
                )
                
            except Exception as e:
                logger.error(f"Erreur SSE: {e}")
                return {"error": str(e)}
    
    async def _execute_tool(self, tool_func, arguments: Dict[str, Any]):
        """Exécute un outil de manière asynchrone"""
        try:
            if asyncio.iscoroutinefunction(tool_func):
                return await tool_func(**arguments)
            else:
                return tool_func(**arguments)
        except Exception as e:
            logger.error(f"Erreur d'exécution d'outil: {e}")
            raise
    
    async def sse_generator(self):
        """Générateur pour les événements SSE de base"""
        yield f"data: {json.dumps({'type': 'connected', 'message': 'SSE connection established'})}\n\n"
        
        # Envoyer la liste des outils disponibles
        tools_data = {
            "type": "tools_list",
            "tools": [{"name": name, "description": info["description"]} 
                     for name, info in self.tools.items()]
        }
        yield f"data: {json.dumps(tools_data)}\n\n"
        
        # Maintenir la connexion
        while True:
            await asyncio.sleep(30)  # Heartbeat toutes les 30 secondes
            yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': asyncio.get_event_loop().time()})}\n\n"
    
    async def sse_tool_generator(self, tool_name: str, arguments: Dict[str, Any]):
        """Générateur pour l'exécution d'outils via SSE"""
        try:
            # Envoyer le début de l'exécution
            yield f"data: {json.dumps({'type': 'tool_start', 'tool': tool_name})}\n\n"
            
            # Exécuter l'outil
            tool_func = self.tools[tool_name]["function"]
            result = await self._execute_tool(tool_func, arguments)
            
            # Envoyer le résultat
            yield f"data: {json.dumps({'type': 'tool_result', 'result': str(result)})}\n\n"
            yield f"data: {json.dumps({'type': 'tool_complete'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'tool_error', 'error': str(e)})}\n\n"
    
    def run_http(self, config: Dict[str, Any]):
        """Lance le serveur en mode HTTP"""
        host = config.get("host", "127.0.0.1")
        port = config.get("port", 8000)
        
        logger.info(f"🌐 Démarrage en mode HTTP sur http://{host}:{port}")
        logger.info(f"📋 API disponible sur http://{host}:{port}/tools")
        
        self.setup_fastapi(config)
        uvicorn.run(self.app, host=host, port=port, log_level="info")
    
    def run_sse(self, config: Dict[str, Any]):
        """Lance le serveur en mode SSE"""
        host = config.get("host", "127.0.0.1")
        port = config.get("port", 8000)
        
        logger.info(f"📡 Démarrage en mode SSE sur http://{host}:{port}")
        logger.info(f"🔄 SSE endpoint: http://{host}:{port}/sse")
        
        self.setup_fastapi(config)
        uvicorn.run(self.app, host=host, port=port, log_level="info")
    
    def run_chatgpt(self, config: Dict[str, Any]):
        """Lance le serveur en mode ChatGPT (Streamable HTTP avec endpoint /mcp)"""
        host = config.get("host", "127.0.0.1")
        port = config.get("port", 8000)
        
        logger.info(f"🤖 Démarrage en mode ChatGPT sur http://{host}:{port}")
        logger.info(f"🔗 MCP endpoint: http://{host}:{port}/mcp")
        
        self.setup_fastapi_chatgpt(config)
        uvicorn.run(self.app, host=host, port=port, log_level="info")
    
    def setup_fastapi_chatgpt(self, config: Dict[str, Any]):
        """Configure l'application FastAPI pour ChatGPT (protocole MCP Streamable HTTP)"""
        self.app = FastAPI(
            title="MCP Wiki for ChatGPT",
            description="Serveur MCP Wikipedia compatible ChatGPT avec protocole Streamable HTTP",
            version="1.0.0"
        )
        
        # Configuration CORS plus permissive pour ChatGPT
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # ChatGPT nécessite un accès ouvert
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Routes MCP pour ChatGPT
        self.setup_chatgpt_routes()
    
    def setup_chatgpt_routes(self):
        """Configure les routes MCP pour ChatGPT (protocole Streamable HTTP)"""
        
        @self.app.get("/")
        async def root():
            return {
                "name": self.name,
                "version": "1.0.0",
                "protocol": "mcp",
                "transport": "streamable-http",
                "capabilities": {
                    "tools": True,
                    "resources": False,
                    "prompts": False
                },
                "tools_count": len(self.tools),
                "chatgpt_compatible": True
            }
        
        @self.app.post("/mcp")
        async def mcp_endpoint(request: Request):
            """Endpoint MCP principal pour ChatGPT (protocole JSON-RPC 2.0)"""
            try:
                data = await request.json()
                method = data.get("method")
                params = data.get("params", {})
                request_id = data.get("id")
                
                if method == "initialize":
                    return {
                        "jsonrpc": "2.0",
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {}
                            },
                            "serverInfo": {
                                "name": self.name,
                                "version": "1.0.0"
                            }
                        },
                        "id": request_id
                    }
                
                elif method == "tools/list":
                    tools_list = []
                    for name, info in self.tools.items():
                        tools_list.append({
                            "name": name,
                            "description": info["description"],
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "additionalProperties": True
                            }
                        })
                    
                    return {
                        "jsonrpc": "2.0",
                        "result": {
                            "tools": tools_list
                        },
                        "id": request_id
                    }
                
                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    if tool_name not in self.tools:
                        return {
                            "jsonrpc": "2.0",
                            "error": {
                                "code": -32601,
                                "message": f"Tool '{tool_name}' not found"
                            },
                            "id": request_id
                        }
                    
                    # Exécuter l'outil
                    tool_func = self.tools[tool_name]["function"]
                    result = await self._execute_tool(tool_func, arguments)
                    
                    return {
                        "jsonrpc": "2.0",
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": str(result)
                                }
                            ]
                        },
                        "id": request_id
                    }
                
                else:
                    return {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32601,
                            "message": f"Method '{method}' not found"
                        },
                        "id": request_id
                    }
                    
            except Exception as e:
                logger.error(f"Erreur dans l'endpoint MCP: {e}")
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    },
                    "id": data.get("id", None)
                }
        
        @self.app.get("/mcp")
        async def mcp_get():
            """GET sur /mcp pour la découverte du serveur"""
            return {
                "name": self.name,
                "version": "1.0.0",
                "protocol": "mcp",
                "transport": "streamable-http",
                "capabilities": {
                    "tools": True
                },
                "tools_count": len(self.tools)
            }
