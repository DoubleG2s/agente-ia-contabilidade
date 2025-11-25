"""
Dependencies para autenticação e autorização
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db, User
from app.auth.security import decode_access_token

# HTTPBearer ao invés de OAuth2PasswordBearer
http_bearer = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Obtém o usuário atual a partir do token JWT no header Authorization"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # LOG 1: Ver se o token está sendo recebido
    print(f"\n🔍 DEBUG - Token recebido: {credentials.credentials[:50]}...")
    
    # Extrai o token das credenciais
    token = credentials.credentials
    
    # Decodifica token
    payload = decode_access_token(token)
    
    # LOG 2: Ver o payload decodificado
    print(f"🔍 DEBUG - Payload decodificado: {payload}")
    
    if payload is None:
        print("❌ DEBUG - Payload é None, token inválido!")
        raise credentials_exception
    
    # ✅ Converte sub de string para int
    user_id_str: str = payload.get("sub")
    
    if user_id_str is None:
        print("❌ DEBUG - User ID é None!")
        raise credentials_exception
    
    try:
        user_id = int(user_id_str)  # ← CONVERTER PARA INT
    except ValueError:
        print(f"❌ DEBUG - Não foi possível converter user_id: {user_id_str}")
        raise credentials_exception
    
    # LOG 3: Ver o user_id extraído
    print(f"🔍 DEBUG - User ID extraído: {user_id}")
    
    # Busca usuário no banco
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # LOG 4: Ver se encontrou o usuário
    print(f"🔍 DEBUG - Usuário encontrado: {user.username if user else 'None'}")
    
    if user is None:
        print("❌ DEBUG - Usuário não encontrado no banco!")
        raise credentials_exception
    
    if not user.is_active:
        print("❌ DEBUG - Usuário inativo!")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    print(f"✅ DEBUG - Autenticação bem-sucedida para: {user.username}")
    return user



async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Garante que o usuário está ativo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    return current_user


def require_role(required_roles: list[str]):
    """
    Decorator para exigir roles específicas
    
    Usage:
        @router.get("/admin")
        async def admin_route(user: User = Depends(require_role(["admin"]))):
            ...
    
    Args:
        required_roles: Lista de roles permitidas (ex: ["admin", "contador"])
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Requer uma das roles: {', '.join(required_roles)}"
            )
        return current_user
    
    return role_checker


# Atalhos para roles comuns
async def require_admin(current_user: User = Depends(require_role(["admin"]))) -> User:
    """Requer role admin"""
    return current_user


async def require_contador(
    current_user: User = Depends(require_role(["admin", "contador"]))
) -> User:
    """Requer role admin ou contador"""
    return current_user
