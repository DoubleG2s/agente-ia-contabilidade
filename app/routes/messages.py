from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional
import uuid

from app.db.database import get_db, save_conversation, get_conversation_history, User
from app.services.openai_services import OpenAIService
from app.auth.dependencies import get_current_active_user  # ✅ NOVO
from app.utils.formatters import (
    format_response, 
    format_error, 
    sanitize_input,
    extract_keywords,
    format_conversation_history
)

router = APIRouter(prefix="/api/messages", tags=["Mensagens"])

# Schemas Pydantic
class MessageRequest(BaseModel):
    """Schema para requisição de mensagem"""
    message: str = Field(..., min_length=1, max_length=2000, description="Mensagem do usuário")
    session_id: Optional[str] = Field(None, description="ID da sessão (gerado automaticamente se não fornecido)")
    use_history: bool = Field(True, description="Se deve usar histórico de conversas")
    use_tools: bool = Field(True, description="Se deve usar ferramentas (calculadoras, consultas)")

class MessageResponse(BaseModel):
    """Schema para resposta de mensagem"""
    success: bool
    session_id: str
    message: str
    timestamp: str
    metadata: dict

class HistoryResponse(BaseModel):
    """Schema para resposta de histórico"""
    success: bool
    session_id: str
    conversations: list
    total: int

# Inicializa serviço OpenAI
openai_service = OpenAIService()

@router.post("/send", response_model=MessageResponse)
async def send_message(
    request: MessageRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),  # ✅ NOVO - Requer autenticação
    db: AsyncSession = Depends(get_db)
):
    """
    Envia mensagem para o agente de IA
    
    **Requer autenticação** (Bearer token no header)
    
    - **message**: Pergunta ou solicitação do usuário
    - **session_id**: ID da sessão (opcional, será gerado se não fornecido)
    - **use_history**: Se deve considerar conversas anteriores da mesma sessão
    - **use_tools**: Se deve usar ferramentas (calculadoras, calendário fiscal)
    """
    try:
        # Gera session_id se não fornecido
        session_id = request.session_id or str(uuid.uuid4())
        
        # Limpa input
        user_message = sanitize_input(request.message)
        
        # Busca histórico se solicitado (filtra por usuário)
        conversation_history = None
        if request.use_history:
            conversation_history = await get_conversation_history(
                db, 
                session_id, 
                limit=5,
                user_id=current_user.id  # ✅ NOVO - Filtra por usuário
            )
        
        # Obtém resposta do GPT
        response = await openai_service.get_completion(
            user_message=user_message,
            conversation_history=conversation_history,
            use_tools=request.use_tools
        )
        
        # Extrai keywords para metadata
        keywords = extract_keywords(user_message)
        
        metadata = {
            "tokens": response["tokens_used"],
            "model": response["model"],
            "keywords": keywords,
            "tools_used": response.get("tools_used", []),
            "user_id": current_user.id,  # ✅ NOVO
            "username": current_user.username  # ✅ NOVO
        }
        
        # Salva conversa em background
        background_tasks.add_task(
            save_conversation,
            db=db,
            session_id=session_id,
            user_msg=user_message,
            assistant_msg=response["message"],
            meta_info=metadata,
            user_id=current_user.id  # ✅ NOVO
        )
        
        return format_response(
            message=response["message"],
            session_id=session_id,
            metadata=metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=format_error(str(e)))

@router.post("/send-stream")
async def send_message_stream(
    request: MessageRequest,
    current_user: User = Depends(get_current_active_user),  # ✅ NOVO
    db: AsyncSession = Depends(get_db)
):
    """
    Envia mensagem e retorna resposta em streaming (tempo real)
    
    **Requer autenticação**
    
    Nota: Streaming não suporta function calling
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        user_message = sanitize_input(request.message)
        
        conversation_history = None
        if request.use_history:
            conversation_history = await get_conversation_history(
                db, 
                session_id, 
                limit=5,
                user_id=current_user.id  # ✅ NOVO
            )
        
        async def generate():
            full_response = ""
            async for chunk in openai_service.get_streaming_completion(
                user_message=user_message,
                conversation_history=conversation_history
            ):
                full_response += chunk
                yield chunk
            
            # Salva após completar streaming
            await save_conversation(
                db=db,
                session_id=session_id,
                user_msg=user_message,
                assistant_msg=full_response,
                meta_info={"streaming": True, "user_id": current_user.id},
                user_id=current_user.id  # ✅ NOVO
            )
        
        return StreamingResponse(generate(), media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(
    session_id: str,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),  # ✅ NOVO
    db: AsyncSession = Depends(get_db)
):
    """
    Recupera histórico de conversas de uma sessão
    
    **Requer autenticação** - Usuários só veem seu próprio histórico
    
    - **session_id**: ID da sessão
    - **limit**: Número máximo de conversas a retornar
    """
    try:
        # Busca histórico (filtra por usuário automaticamente)
        conversations = await get_conversation_history(
            db, 
            session_id, 
            limit=limit,
            user_id=current_user.id  # ✅ NOVO - Usuários só veem seu histórico
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "conversations": format_conversation_history(conversations),
            "total": len(conversations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=format_error(str(e)))

@router.delete("/history/{session_id}")
async def clear_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),  # ✅ NOVO
    db: AsyncSession = Depends(get_db)
):
    """
    Limpa histórico de uma sessão específica
    
    **Requer autenticação** - Usuários só podem limpar seu próprio histórico
    """
    try:
        from sqlalchemy import delete
        from app.db.database import Conversation
        
        # Deleta apenas conversas do usuário atual
        stmt = delete(Conversation).where(
            (Conversation.session_id == session_id) & 
            (Conversation.user_id == current_user.id)  # ✅ NOVO - Segurança
        )
        await db.execute(stmt)
        await db.commit()
        
        return {
            "success": True,
            "message": f"Histórico da sessão {session_id} limpo com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=format_error(str(e)))

# ✅ Endpoint para ver todas as conversas do usuário
@router.get("/my-conversations")
async def get_my_conversations(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todas as conversas do usuário autenticado
    """
    from sqlalchemy import select, func
    from app.db.database import Conversation
    
    # Busca sessões únicas
    stmt = select(
        Conversation.session_id,
        func.count(Conversation.id).label("message_count"),
        func.max(Conversation.created_at).label("last_message")
    ).where(
        Conversation.user_id == current_user.id
    ).group_by(
        Conversation.session_id
    ).order_by(
        func.max(Conversation.created_at).desc()
    ).limit(limit)
    
    result = await db.execute(stmt)
    sessions = result.all()
    
    return {
        "success": True,
        "total_sessions": len(sessions),
        "sessions": [
            {
                "session_id": s.session_id,
                "message_count": s.message_count,
                "last_message": s.last_message.isoformat()
            }
            for s in sessions
        ]
    }
