from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging


from app.config import get_settings
from app.db.database import init_db
from app.routes import messages, auth  # ✅ Importar auth
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Lifespan: Gerencia startup e shutdown da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando aplicação...")
    logger.info(f"📦 Modelo OpenAI: {settings.OPENAI_MODEL}")
    
    # Inicializa banco de dados
    await init_db()
    logger.info("✅ Banco de dados inicializado")
    
    yield
    
    logger.info("🛑 Encerrando aplicação...")

# Cria aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Agente de IA especializado em contabilidade brasileira",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de logging
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"📥 {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 Status: {response.status_code}")
    return response

# ✅ REGISTRA ROTAS
app.include_router(auth.router)     # ✅ NOVO - Autenticação
app.include_router(messages.router)

# Rota raiz
@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{settings.APP_NAME}</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .container {{
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }}
            h1 {{ margin-top: 0; font-size: 2.5em; }}
            .endpoint {{
                background: rgba(255, 255, 255, 0.2);
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                font-family: 'Courier New', monospace;
            }}
            a {{
                color: #ffd700;
                text-decoration: none;
                font-weight: bold;
            }}
            a:hover {{ text-decoration: underline; }}
            .badge {{
                background: #4CAF50;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                display: inline-block;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 {settings.APP_NAME}</h1>
            <div class="badge">v{settings.APP_VERSION} ✅ Multi-User</div>
            
            <h2>🔐 Autenticação</h2>
            <div class="endpoint">
                <strong>POST</strong> /api/auth/register<br>
                <small>Registrar novo usuário</small>
            </div>
            <div class="endpoint">
                <strong>POST</strong> /api/auth/login<br>
                <small>Login (retorna token JWT)</small>
            </div>
            <div class="endpoint">
                <strong>GET</strong> /api/auth/me<br>
                <small>Informações do usuário autenticado</small>
            </div>
            
            <h2>💬 Mensagens (requer autenticação)</h2>
            <div class="endpoint">
                <strong>POST</strong> /api/messages/send<br>
                <small>Enviar mensagem para o agente</small>
            </div>
            
            <h2>📚 Documentação:</h2>
            <p>
                <a href="/docs">📖 Swagger UI</a><br>
                <a href="/chat">🚀 Interface de Chat</a>
            </p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/chat", response_class=HTMLResponse)
async def chat_interface():
    return FileResponse("frontend/index.html")

@app.get("/frontend/{file_path:path}")
async def serve_frontend(file_path: str):
    """Serve arquivos estáticos do frontend"""
    file_location = Path("frontend") / file_path
    
    if file_location.exists() and file_location.is_file():
        # ✅ Headers para prevenir cache em páginas HTML
        headers = {}
        if file_path.endswith('.html'):
            headers = {
                'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        
        return FileResponse(
            file_location,
            headers=headers
        )
    
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"❌ Erro não tratado: {str(exc)}")
    return {
        "success": False,
        "error": "Erro interno do servidor",
        "detail": str(exc) if settings.DEBUG else "Entre em contato com o suporte"
    }

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
