from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # API Config
    APP_NAME: str = "Agente IA Contabilidade"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # OpenAI Config
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    MAX_TOKENS: int = 1500
    TEMPERATURE: float = 0.7
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./contabilidade_agent.db"
    
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
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    """Retorna instância única das configurações"""
    return Settings()
