from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey
from datetime import datetime, timezone
from typing import AsyncGenerator
from app.config import get_settings

settings = get_settings()

# Engine assíncrono
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# ✅ NOVO - Modelo de Usuário
class User(Base):
    """Usuários do sistema"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user", nullable=False)  # admin, contador, assistente, user
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)

# Modelo de Conversa (atualizado com user_id)
class Conversation(Base):
    """Armazena histórico de conversas"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # ✅ NOVO - Relacionamento
    user_message = Column(Text, nullable=False)
    assistant_message = Column(Text, nullable=False)
    meta_info = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Modelo de Cliente (para contexto)
class Client(Base):
    """Dados de clientes do escritório"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    cnpj_cpf = Column(String(20), unique=True, index=True)
    regime_tributario = Column(String(50))
    email = Column(String(200))
    telefone = Column(String(20))
    observacoes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

async def init_db():
    """Inicializa o banco de dados"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency para obter sessão do banco"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Funções auxiliares de CRUD
async def save_conversation(
    db: AsyncSession, 
    session_id: str, 
    user_msg: str, 
    assistant_msg: str,
    meta_info: dict = None,
    user_id: int = None  # ✅ NOVO
):
    """Salva uma interação no histórico"""
    conversation = Conversation(
        session_id=session_id,
        user_id=user_id,  # ✅ NOVO
        user_message=user_msg,
        assistant_message=assistant_msg,
        meta_info=meta_info
    )
    db.add(conversation)
    await db.flush()
    return conversation

async def get_conversation_history(
    db: AsyncSession, 
    session_id: str, 
    limit: int = 10,
    user_id: int = None  # ✅ NOVO - Filtrar por usuário
):
    """Recupera histórico de conversas de uma sessão"""
    from sqlalchemy import select
    
    stmt = select(Conversation).where(
        Conversation.session_id == session_id
    )
    
    # Filtrar por usuário se fornecido
    if user_id:
        stmt = stmt.where(Conversation.user_id == user_id)
    
    stmt = stmt.order_by(
        Conversation.created_at.desc()
    ).limit(limit)
    
    result = await db.execute(stmt)
    conversations = result.scalars().all()
    return list(reversed(conversations))
