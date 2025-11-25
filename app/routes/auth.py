"""
Rotas de autenticação: login, registro, perfil
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
from typing import Optional

from app.db.database import get_db, User
from app.auth.security import verify_password, get_password_hash, create_access_token
from app.auth.dependencies import get_current_active_user, require_admin

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


# ========================================
# SCHEMAS PYDANTIC
# ========================================

class UserRegister(BaseModel):
    """Schema para registro de novo usuário"""
    email: EmailStr = Field(..., description="Email do usuário")
    username: str = Field(..., min_length=3, max_length=50, description="Nome de usuário único")
    full_name: str = Field(..., min_length=3, max_length=255, description="Nome completo")
    password: str = Field(..., min_length=6, description="Senha (mínimo 6 caracteres)")
    role: str = Field(default="user", description="Role do usuário (user, contador, assistente, admin)")


class UserLogin(BaseModel):
    """Schema para login"""
    username: str
    password: str


class Token(BaseModel):
    """Schema de resposta do token"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """Schema de resposta do usuário"""
    id: int
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]


class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """Schema para mudança de senha"""
    current_password: str
    new_password: str = Field(..., min_length=6)


# ========================================
# ENDPOINTS
# ========================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Registra um novo usuário no sistema
    
    - **email**: Email único do usuário
    - **username**: Nome de usuário único
    - **full_name**: Nome completo
    - **password**: Senha (será hasheada)
    - **role**: user (padrão), contador, assistente, admin
    """
    
    # Verifica se email já existe
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Verifica se username já existe
    stmt = select(User).where(User.username == user_data.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já existe"
        )
    
    # Valida role
    valid_roles = ["user", "contador", "assistente", "admin"]
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role inválida. Use: {', '.join(valid_roles)}"
        )
    
    # Cria usuário
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
    ):
    """Endpoint de login - retorna token JWT"""
    
    # Busca usuário por username ou email
    stmt = select(User).where(
        (User.username == form_data.username) | (User.email == form_data.username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # Verifica credenciais
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    # Atualiza último login
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    
    # ✅ Cria token JWT com sub como STRING
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}  # ← CONVERTER PARA STRING
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }



@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna informações do usuário autenticado
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza informações do usuário autenticado
    """
    
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    
    if user_update.email:
        # Verifica se email já existe
        stmt = select(User).where(
            (User.email == user_update.email) & (User.id != current_user.id)
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        current_user.email = user_update.email
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Altera a senha do usuário autenticado
    """
    
    # Verifica senha atual
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    # Atualiza senha
    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()
    
    return {"message": "Senha alterada com sucesso"}


# ========================================
# ENDPOINTS ADMINISTRATIVOS
# ========================================

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os usuários (apenas admin)
    """
    stmt = select(User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    return users


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Deleta um usuário (apenas admin)
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Não permite deletar a si mesmo
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode deletar sua própria conta"
        )
    
    await db.delete(user)
    await db.commit()
    
    return {"message": f"Usuário {user.username} deletado com sucesso"}


@router.patch("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Ativa/desativa um usuário (apenas admin)
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    user.is_active = not user.is_active
    await db.commit()
    
    status_text = "ativado" if user.is_active else "desativado"
    return {"message": f"Usuário {user.username} {status_text} com sucesso"}
