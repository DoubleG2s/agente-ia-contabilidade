from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# Encontra a raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # API Config
    APP_NAME: str = "Agente IA Contabilidade"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # OpenAI Config
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    MAX_TOKENS: int = 1500
    TEMPERATURE: float = 0.7
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./contabilidade_agent.db"
    
    # ✅ NOVO - Autenticação
    SECRET_KEY: str # Mude em produção!
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 dias
    
    # Sistema Prompt para o agente
    SYSTEM_PROMPT: str = """Você é um assistente especializado em contabilidade brasileira.
    
    Suas responsabilidades incluem:
    - Responder dúvidas sobre prazos de obrigações fiscais
    - Orientar sobre documentação necessária
    - Esclarecer dúvidas sobre Simples Nacional, MEI, Lucro Real e Presumido
    - Ajudar com cálculos de impostos básicos
    - Fornecer informações sobre SPED, NFe, DAS, DARF
    - Auxiliar em questões trabalhistas básicas (folha de pagamento, férias, 13º)
    
    IMPORTANTE:
    - Sempre mantenha um tom profissional e educado
    - Se não souber algo, admita e sugira consultar um contador
    - Cite legislação quando relevante (Lei, IN, Resolução)
    - Use linguagem clara, evite jargões complexos sem explicação
    - Mantenha o contexto da conversa anterior
    """
    
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'
        case_sensitive = True

@lru_cache()
def get_settings():
    """Retorna instância única das configurações"""
    return Settings()
