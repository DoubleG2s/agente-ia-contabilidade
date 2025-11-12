from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional
import uuid

from app.db.database import get_db, save_conversation, get_conversation_history
from app.services.openai_services import OpenAIService
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
    use_tools: bool = Field(True, description="Se deve usar ferramentas (calculadoras, consultas)")  # ✅ NOVO

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
    db: AsyncSession = Depends(get_db)
):
    """
    Envia mensagem para o agente de IA
    
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
        
        # Busca histórico se solicitado
        conversation_history = None
        if request.use_history:
            conversation_history = await get_conversation_history(db, session_id, limit=5)
        
        # Obtém resposta do GPT (com ou sem tools)
        response = await openai_service.get_completion(
            user_message=user_message,
            conversation_history=conversation_history,
            use_tools=request.use_tools  # ✅ Passa o parâmetro
        )
        
        # Extrai keywords para metadata
        keywords = extract_keywords(user_message)
        
        metadata = {
            "tokens": response["tokens_used"],
            "model": response["model"],
            "keywords": keywords,
            "tools_used": response.get("tools_used", [])  # ✅ Adiciona tools usadas
        }
        
        # Salva conversa em background
        background_tasks.add_task(
            save_conversation,
            db=db,
            session_id=session_id,
            user_msg=user_message,
            assistant_msg=response["message"],
            meta_info=metadata
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
    db: AsyncSession = Depends(get_db)
):
    """
    Envia mensagem e retorna resposta em streaming (tempo real)
    Nota: Streaming não suporta function calling
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        user_message = sanitize_input(request.message)
        
        conversation_history = None
        if request.use_history:
            conversation_history = await get_conversation_history(db, session_id, limit=5)
        
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
                meta_info={"streaming": True}
            )
        
        return StreamingResponse(generate(), media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(
    session_id: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Recupera histórico de conversas de uma sessão
    
    - **session_id**: ID da sessão
    - **limit**: Número máximo de conversas a retornar
    """
    try:
        conversations = await get_conversation_history(db, session_id, limit=limit)
        
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
    db: AsyncSession = Depends(get_db)
):
    """
    Limpa histórico de uma sessão específica
    """
    try:
        from sqlalchemy import delete
        from app.db.database import Conversation
        
        stmt = delete(Conversation).where(Conversation.session_id == session_id)
        await db.execute(stmt)
        await db.commit()
        
        return {
            "success": True,
            "message": f"Histórico da sessão {session_id} limpo com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=format_error(str(e)))
