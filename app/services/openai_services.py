from openai import AsyncOpenAI
from typing import List, Dict, Optional
import json

from app.config import get_settings
from app.services.tools import AVAILABLE_TOOLS, FUNCTION_MAP

settings = get_settings()

class OpenAIService:
    """Serviço para comunicação com OpenAI API com suporte a Function Calling"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
    
    def _build_messages(
        self, 
        user_message: str, 
        conversation_history: List[Dict] = None
    ) -> List[Dict[str, str]]:
        """Constrói array de mensagens incluindo histórico"""
        messages = [
            {"role": "system", "content": settings.SYSTEM_PROMPT}
        ]
        
        # Adiciona histórico de conversas anteriores
        if conversation_history:
            for conv in conversation_history:
                messages.append({"role": "user", "content": conv.user_message})
                messages.append({"role": "assistant", "content": conv.assistant_message})
        
        # Adiciona mensagem atual do usuário
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    async def get_completion(
        self, 
        user_message: str,
        conversation_history: List[Dict] = None,
        use_tools: bool = True
    ) -> Dict:
        """
        Obtém resposta do GPT com suporte a Function Calling
        
        Args:
            user_message: Mensagem do usuário
            conversation_history: Histórico de conversas anteriores
            use_tools: Se deve usar ferramentas (function calling)
        
        Returns:
            Dict com resposta e metadata
        """
        messages = self._build_messages(user_message, conversation_history)
        
        try:
            # Primeira chamada à API (pode gerar tool calls)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                tools=AVAILABLE_TOOLS if use_tools else None,
                tool_choice="auto" if use_tools else None
            )
            
            assistant_message = response.choices[0].message
            
            # Verifica se o modelo quer chamar funções
            if assistant_message.tool_calls:
                # Adiciona a resposta do assistente (com tool calls) ao histórico
                messages.append(assistant_message)
                
                # Executa cada tool call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Executa a função
                    if function_name in FUNCTION_MAP:
                        function_response = FUNCTION_MAP[function_name](**function_args)
                        
                        # Adiciona o resultado ao histórico
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": json.dumps(function_response, ensure_ascii=False)
                        })
                
                # Segunda chamada à API com os resultados das funções
                second_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                
                final_message = second_response.choices[0].message.content
                
                return {
                    "message": final_message,
                    "model": second_response.model,
                    "tokens_used": {
                        "prompt": response.usage.prompt_tokens + second_response.usage.prompt_tokens,
                        "completion": response.usage.completion_tokens + second_response.usage.completion_tokens,
                        "total": response.usage.total_tokens + second_response.usage.total_tokens
                    },
                    "finish_reason": second_response.choices[0].finish_reason,
                    "tools_used": [tc.function.name for tc in assistant_message.tool_calls]
                }
            
            # Se não houve tool calls, retorna resposta normal
            return {
                "message": assistant_message.content,
                "model": response.model,
                "tokens_used": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason,
                "tools_used": []
            }
            
        except Exception as e:
            raise Exception(f"Erro ao comunicar com OpenAI: {str(e)}")
    
    async def get_streaming_completion(
        self,
        user_message: str,
        conversation_history: List[Dict] = None
    ):
        """
        Retorna resposta em streaming (para respostas longas em tempo real)
        Nota: Function calling não é suportado em streaming
        """
        messages = self._build_messages(user_message, conversation_history)
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"[ERRO]: {str(e)}"
