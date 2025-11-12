from datetime import datetime
from typing import Dict, Any

def format_response(
    message: str,
    session_id: str,
    metadata: Dict = None
) -> Dict[str, Any]:
    """
    Formata resposta padrão da API
    """
    return {
        "success": True,
        "session_id": session_id,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": metadata or {}
    }

def format_error(error_message: str, status_code: int = 500) -> Dict[str, Any]:
    """
    Formata resposta de erro
    """
    return {
        "success": False,
        "error": error_message,
        "status_code": status_code,
        "timestamp": datetime.utcnow().isoformat()
    }

def format_conversation_history(conversations: list) -> list:
    """
    Formata histórico de conversas para resposta da API
    """
    return [
        {
            "user": conv.user_message,
            "assistant": conv.assistant_message,
            "timestamp": conv.created_at.isoformat()
        }
        for conv in conversations
    ]

def sanitize_input(text: str, max_length: int = 2000) -> str:
    """
    Limpa e valida input do usuário
    """
    # Remove espaços extras
    text = " ".join(text.split())
    
    # Limita tamanho
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()

def extract_keywords(text: str) -> list:
    """
    Extrai palavras-chave para categorização (simples)
    """
    keywords_contabilidade = [
        "imposto", "sped", "nfe", "das", "darf", "simples nacional",
        "lucro real", "lucro presumido", "mei", "folha pagamento",
        "férias", "13º", "rescisão", "contrato", "obrigação",
        "prazo", "entrega", "declaração", "irpf", "irpj"
    ]
    
    text_lower = text.lower()
    found = [kw for kw in keywords_contabilidade if kw in text_lower]
    
    return found
