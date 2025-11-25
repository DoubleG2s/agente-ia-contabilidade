"""
Script para criar usuário admin inicial
Execute: python create_admin.py
"""

import asyncio
from sqlalchemy import select
from app.db.database import AsyncSessionLocal, User, init_db
from app.auth.security import get_password_hash

async def create_admin_user():
    """Cria usuário admin se não existir"""
    
    # Inicializa banco
    await init_db()
    print("✅ Banco de dados inicializado")
    
    async with AsyncSessionLocal() as db:
        # Verifica se admin já existe
        stmt = select(User).where(User.username == "admin")
        result = await db.execute(stmt)
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("⚠️  Usuário admin já existe!")
            print(f"   Email: {existing_admin.email}")
            print(f"   Username: {existing_admin.username}")
            return
        
        # Dados do admin
        admin_email = input("Email do admin: ").strip()
        admin_username = input("Username do admin (padrão: admin): ").strip() or "admin"
        admin_name = input("Nome completo do admin: ").strip()
        admin_password = input("Senha do admin (mínimo 6 caracteres): ").strip()
        
        if len(admin_password) < 6:
            print("❌ Senha deve ter no mínimo 6 caracteres!")
            return
        
        # Cria admin
        admin_user = User(
            email=admin_email,
            username=admin_username,
            full_name=admin_name,
            hashed_password=get_password_hash(admin_password),
            role="admin",
            is_active=True
        )
        
        db.add(admin_user)
        await db.commit()
        
        print("\n✅ Usuário admin criado com sucesso!")
        print(f"   Email: {admin_email}")
        print(f"   Username: {admin_username}")
        print(f"   Role: admin")
        print("\n🔐 Faça login em: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(create_admin_user())
