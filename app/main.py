from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles  # ✅ ADICIONAR
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.db.database import init_db
from app.routes import messages

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
    """
    Gerencia eventos de inicialização e encerramento da aplicação.
    - Startup: Inicializa o banco de dados
    - Shutdown: Limpa recursos (se necessário)
    """
    logger.info("🚀 Iniciando aplicação...")
    logger.info(f"📦 Modelo OpenAI: {settings.OPENAI_MODEL}")
    
    # Inicializa banco de dados
    await init_db()
    logger.info("✅ Banco de dados inicializado")
    
    yield  # Aplicação roda aqui
    
    # Código de shutdown (se necessário no futuro)
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

# Configuração de CORS (permite frontend acessar a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"  # Em produção, especifique os domínios exatos
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de logging de requisições
@app.middleware("http")
async def log_requests(request, call_next):
    """Loga todas as requisições HTTP"""
    logger.info(f"📥 {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 Status: {response.status_code}")
    return response

# ✅ REGISTRA ROTAS DA API PRIMEIRO (importante!)
app.include_router(messages.router)

# Rota raiz
@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Página inicial da API com informações básicas
    """
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
            .info {{ margin: 20px 0; font-size: 1.1em; }}
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
            <div class="badge">v{settings.APP_VERSION}</div>
            
            <div class="info">
                <p>✨ <strong>Bem-vindo ao Agente de IA especializado em contabilidade!</strong></p>
                <p>Este agente pode ajudar com:</p>
                <ul>
                    <li>📋 Obrigações fiscais e prazos</li>
                    <li>💼 Simples Nacional, MEI, Lucro Real e Presumido</li>
                    <li>📊 SPED, NFe, DAS, DARF</li>
                    <li>👥 Questões trabalhistas e folha de pagamento</li>
                </ul>
            </div>
            
            <h2>🔗 Endpoints Disponíveis:</h2>
            
            <div class="endpoint">
                <strong>POST</strong> /api/messages/send
                <br><small>Envia mensagem para o agente</small>
            </div>
            
            <div class="endpoint">
                <strong>POST</strong> /api/messages/send-stream
                <br><small>Envia mensagem com resposta em streaming</small>
            </div>
            
            <div class="endpoint">
                <strong>GET</strong> /api/messages/history/{{session_id}}
                <br><small>Recupera histórico de conversas</small>
            </div>
            
            <div class="endpoint">
                <strong>DELETE</strong> /api/messages/history/{{session_id}}
                <br><small>Limpa histórico de uma sessão</small>
            </div>
            
            <h2>📚 Documentação:</h2>
            <p>
                <a href="/docs" target="_blank">📖 Swagger UI (Interativa)</a><br>
                <a href="/redoc" target="_blank">📘 ReDoc (Alternativa)</a>
            </p>
            
            <h2>💬 Interface de Chat:</h2>
            <p>
                <a href="/chat">🚀 Abrir Chat Interface</a>
            </p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# ✅ NOVA ROTA: Serve o frontend do chat
@app.get("/chat", response_class=HTMLResponse)
async def chat_interface():
    """Serve a interface de chat"""
    return FileResponse("frontend/index.html")

# Rota de health check
@app.get("/health")
async def health_check():
    """
    Verifica se a API está funcionando
    Útil para monitoramento e load balancers
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# Tratamento de erros global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Captura erros não tratados"""
    logger.error(f"❌ Erro não tratado: {str(exc)}")
    return {
        "success": False,
        "error": "Erro interno do servidor",
        "detail": str(exc) if settings.DEBUG else "Entre em contato com o suporte"
    }

# ✅ MONTA ARQUIVOS ESTÁTICOS POR ÚLTIMO (importante!)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
