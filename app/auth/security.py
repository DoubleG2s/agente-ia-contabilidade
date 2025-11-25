"""
Módulo de segurança: hashing de senhas e geração de tokens JWT
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

# ✅ SEMPRE buscar do settings
settings = get_settings()

# Configuração do contexto de senha - ARGON2
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# ✅ Configurações JWT vindas do settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera hash argon2 de uma senha"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT usando a SECRET_KEY do settings
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # ✅ Debug temporário
    print(f"🔐 Gerando token com SECRET_KEY: {SECRET_KEY[:10]}...")
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica e valida um token JWT usando a SECRET_KEY do settings
    """
    # ✅ Debug temporário
    print(f"🔓 Decodificando token com SECRET_KEY: {SECRET_KEY[:10]}...")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"❌ Erro ao decodificar token: {e}")
        return None
