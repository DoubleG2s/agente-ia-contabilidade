# 📚 Documentação Completa - Agente de IA para Contabilidade

**Versão:** 1.0.0  
**Última atualização:** Novembro 2025  
**Autor:** DoubleG2s  
**Repositório:** [agente-ia-contabilidade](https://github.com/DoubleG2s/agente-ia-contabilidade)

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Tecnologias Utilizadas](#tecnologias-utilizadas)
4. [Pré-requisitos e Instalação](#pré-requisitos-e-instalação)
5. [Configuração](#configuração)
6. [Estrutura de Pastas](#estrutura-de-pastas)
7. [API Endpoints](#api-endpoints)
8. [Autenticação](#autenticação)
9. [Módulos Principais](#módulos-principais)
10. [Ferramentas (Function Calling)](#ferramentas-function-calling)
11. [Banco de Dados](#banco-de-dados)
12. [Deployment](#deployment)
13. [Troubleshooting](#troubleshooting)
14. [Contribuindo](#contribuindo)

---

## 🎯 Visão Geral

O **Agente de IA para Contabilidade** é um assistente inteligente especializado em contabilidade brasileira, construído com **FastAPI** e **OpenAI GPT-4**. Ele fornece respostas contextualizadas sobre obrigações fiscais, cálculos tributários, questões trabalhistas e oferece ferramentas integradas (function calling) para cálculos automatizados.

### ✨ Principais Funcionalidades

- 🧠 **IA Conversacional**: Respostas contextualizadas com memória de conversas
- 🛠️ **Function Calling**: Ferramentas integradas para cálculos automatizados
- 📊 **Especialidades**: Simples Nacional, Lucro Real/Presumido, SPED, NFe, Folha de Pagamento
- 🔐 **Autenticação**: Sistema de usuários com JWT e roles
- 💾 **Persistência**: Banco de dados assíncrono com SQLAlchemy
- 🌐 **Interface Web**: Chat moderno com suporte a Markdown e syntax highlighting
- 📈 **Streaming**: Respostas em tempo real

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────┐
│         Frontend (HTML/CSS/JS)          │
│  ├─ chat.html (Interface Principal)     │
│  ├─ login.html (Autenticação)           │
│  └─ index.html (Homepage)               │
└────────────┬────────────────────────────┘
             │
             ↓ HTTP/WebSocket
┌─────────────────────────────────────────┐
│      FastAPI Application                │
│  ├─ routes/auth.py (Autenticação)       │
│  ├─ routes/messages.py (Chat)           │
│  ├─ services/openai_services.py (IA)    │
│  ├─ services/tools.py (Ferramentas)     │
│  └─ auth/ (Segurança)                   │
└────────────┬────────────────────────────┘
             │
      ┌──────┴──────┐
      ↓             ↓
  OpenAI API    SQLite Database
  (GPT-4o-mini) (Histórico)
```

### Fluxo de Requisição

```
1. Usuário envia mensagem (Chat)
   ↓
2. Autenticação JWT validada
   ↓
3. Busca histórico de conversas (opcional)
   ↓
4. Envia para OpenAI com system prompt
   ↓
5. OpenAI retorna resposta ± ferramentas necessárias
   ↓
6. Se ferramentas solicitadas:
   ├─ Executa ferramentas localmente
   └─ Envia resultados novamente para OpenAI
   ↓
7. Salva conversa no banco
   ↓
8. Retorna resposta ao usuário
```

---

## 🛠️ Tecnologias Utilizadas

| Categoria | Tecnologia | Versão | Uso |
|-----------|-----------|--------|-----|
| **Framework Web** | FastAPI | 0.115+ | Server web assíncrono |
| **Server ASGI** | Uvicorn | 0.30+ | Execução da aplicação |
| **IA/LLM** | OpenAI API | 1.54+ | Modelo GPT-4o-mini |
| **ORM** | SQLAlchemy | 2.0+ | Banco de dados assíncrono |
| **Driver DB** | aiosqlite | 0.20+ | SQLite assíncrono |
| **Validação** | Pydantic | 2.12+ | Validação de dados e settings |
| **Autenticação** | python-jose | 3.3+ | JWT tokens |
| **Hash Senha** | Argon2 | 23.1+ | Hashing seguro |
| **Configuração** | python-dotenv | 1.0+ | Variáveis de ambiente |
| **Email** | email-validator | 2.1+ | Validação de emails |
| **HTTP Client** | httpx | 0.28+ | Cliente HTTP async |
| **Markdown** | Marked.js | - | Frontend (renderização) |
| **Code Highlight** | Highlight.js | - | Frontend (syntax highlighting) |
| **Containerização** | Docker | - | Deploy em containers |

---

## 📦 Pré-requisitos e Instalação

### Requisitos do Sistema

- **Python**: 3.13+ (compatível com 3.11+)
- **Git**: Para clonar o repositório
- **Chave OpenAI**: [Obter aqui](https://platform.openai.com/api-keys)
- **Sistemas Operacionais**: Windows, macOS, Linux

### 1️⃣ Clone o Repositório

```bash
git clone https://github.com/DoubleG2s/agente-ia-contabilidade.git
cd agente-ia-contabilidade
```

### 2️⃣ Crie Ambiente Virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Instale Dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Variáveis de Ambiente

Crie um arquivo `.env` na **raiz do projeto**:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-sua-chave-api-aqui
OPENAI_MODEL=gpt-4o-mini
MAX_TOKENS=1500
TEMPERATURE=0.7

# Application Settings
APP_NAME=Agente IA Contabilidade
APP_VERSION=1.0.0
DEBUG=True

# Database
DATABASE_URL=sqlite+aiosqlite:///./contabilidade_agent.db

# Authentication (IMPORTANTE: Mude em produção!)
SECRET_KEY=sua-chave-secreta-super-segura-aqui
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 5️⃣ Crie Admin (Opcional)

```bash
python create_admin.py
```

### 6️⃣ Execute a Aplicação

```bash
uvicorn app.main:app --reload
```

A aplicação estará disponível em: **http://localhost:8000**

---

## ⚙️ Configuração

### Variáveis de Ambiente

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `OPENAI_API_KEY` | string | - | **Obrigatória** - Chave da API OpenAI |
| `OPENAI_MODEL` | string | gpt-4o-mini | Modelo a usar (gpt-4, gpt-4o, gpt-4o-mini) |
| `MAX_TOKENS` | int | 1500 | Máximo de tokens na resposta |
| `TEMPERATURE` | float | 0.7 | Criatividade do modelo (0.0-2.0) |
| `APP_NAME` | string | Agente IA Contabilidade | Nome da aplicação |
| `APP_VERSION` | string | 1.0.0 | Versão da aplicação |
| `DEBUG` | bool | True | Modo debug (False em produção) |
| `DATABASE_URL` | string | sqlite+aiosqlite:///./contabilidade_agent.db | URL do banco de dados |
| `SECRET_KEY` | string | - | **Obrigatória** - Chave para JWT (mude em produção) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | 10080 | Expiração do token (7 dias padrão) |

### Modelos OpenAI Recomendados

- **gpt-4o-mini** ⭐ Recomendado (rápido, barato, poderoso)
- **gpt-4o** (mais caro, melhor qualidade)
- **gpt-4-turbo** (alternativa)

---

## 📁 Estrutura de Pastas

```
agente-ia-contabilidade/
├── app/                          # Código principal da aplicação
│   ├── __init__.py
│   ├── main.py                   # Entrada da aplicação (FastAPI)
│   ├── config.py                 # Configurações (Pydantic Settings)
│   │
│   ├── auth/                     # Sistema de autenticação
│   │   ├── __init__.py
│   │   ├── dependencies.py       # Dependências (get_current_user, etc)
│   │   └── security.py           # Funções de segurança (hash, JWT)
│   │
│   ├── db/                       # Banco de dados
│   │   ├── __init__.py
│   │   └── database.py           # Modelos SQLAlchemy e conexão
│   │
│   ├── routes/                   # Rotas/Endpoints da API
│   │   ├── __init__.py
│   │   ├── auth.py               # Endpoints: registro, login, perfil
│   │   └── messages.py           # Endpoints: envio de mensagens
│   │
│   ├── services/                 # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── openai_services.py    # Integração com OpenAI
│   │   └── tools.py              # Ferramentas (function calling)
│   │
│   └── utils/                    # Utilitários
│       ├── __init__.py
│       └── formatters.py         # Formatação de dados
│
├── frontend/                     # Interface web (HTML/CSS/JS)
│   ├── index.html                # Página inicial
│   ├── login.html                # Página de login
│   └── chat.html                 # Interface do chat
│
├── docs/                         # Documentação
│   └── DOCUMENTACAO.md           # Este arquivo
│
├── .env                          # Variáveis de ambiente (não commitar)
├── .gitignore                    # Arquivos a ignorar no git
├── Dockerfile                    # Configuração Docker
├── docker-compose.yml            # Orquestração Docker (opcional)
├── requirements.txt              # Dependências Python
├── create_admin.py               # Script para criar usuário admin
├── README.md                     # Readme do projeto
└── contabilidade_agent.db        # Banco de dados SQLite (gerado)
```

### Descrição dos Diretórios Principais

#### `app/`
Contém toda a lógica da aplicação FastAPI, dividida em camadas:
- **routes/**: Endpoints HTTP
- **services/**: Lógica de negócio
- **db/**: Modelos e acesso a banco de dados
- **auth/**: Segurança e autenticação
- **utils/**: Funções auxiliares

#### `frontend/`
Arquivos HTML/CSS/JS da interface web. Sem framework (vanilla JS).

#### `docs/`
Documentação do projeto em Markdown.

---

## 🔌 API Endpoints

### 🔐 Autenticação

#### POST `/api/auth/register`
Registra um novo usuário

**Request:**
```json
{
  "email": "usuario@example.com",
  "username": "usuario123",
  "full_name": "João Silva",
  "password": "senha123",
  "role": "user"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "usuario@example.com",
  "username": "usuario123",
  "full_name": "João Silva",
  "role": "user",
  "is_active": true,
  "created_at": "2025-11-25T10:30:00",
  "last_login": null
}
```

**Status Codes:**
- `201 Created`: Usuário registrado com sucesso
- `400 Bad Request`: Email ou username já existem

---

#### POST `/api/auth/login`
Faz login e retorna token JWT

**Request:**
```json
{
  "username": "usuario123",
  "password": "senha123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "usuario123",
    "email": "usuario@example.com",
    "role": "user"
  }
}
```

**Status Codes:**
- `200 OK`: Login bem-sucedido
- `401 Unauthorized`: Credenciais inválidas

---

#### GET `/api/auth/me`
Obtém perfil do usuário autenticado

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "usuario@example.com",
  "username": "usuario123",
  "full_name": "João Silva",
  "role": "user",
  "is_active": true,
  "created_at": "2025-11-25T10:30:00",
  "last_login": "2025-11-25T15:45:00"
}
```

---

#### PUT `/api/auth/me`
Atualiza perfil do usuário

**Headers:**
```
Authorization: Bearer {token}
```

**Request:**
```json
{
  "full_name": "João Silva Santos",
  "email": "novoemail@example.com"
}
```

**Response (200 OK):**
Similar ao endpoint GET `/api/auth/me`

---

#### POST `/api/auth/change-password`
Altera a senha do usuário

**Headers:**
```
Authorization: Bearer {token}
```

**Request:**
```json
{
  "current_password": "senha123",
  "new_password": "nova_senha456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Senha alterada com sucesso"
}
```

---

### 💬 Mensagens

#### POST `/api/messages/send`
Envia mensagem para o agente de IA

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request:**
```json
{
  "message": "Como calcular DAS para MEI?",
  "session_id": "abc123def456",
  "use_history": true,
  "use_tools": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "session_id": "abc123def456",
  "message": "Para um MEI em 2025, o DAS é calculado...",
  "timestamp": "2025-11-25T15:47:30.123456",
  "metadata": {
    "model": "gpt-4o-mini",
    "tokens_used": 245,
    "tools_used": ["calculadora_das"],
    "processing_time": 2.34
  }
}
```

**Status Codes:**
- `200 OK`: Mensagem processada
- `401 Unauthorized`: Não autenticado
- `422 Unprocessable Entity`: Dados inválidos

**Parâmetros:**
- `message` (string, obrigatório): Pergunta ou solicitação (max 2000 chars)
- `session_id` (string, opcional): ID da sessão (UUID gerado se não fornecido)
- `use_history` (bool, default: true): Usar histórico de conversas
- `use_tools` (bool, default: true): Usar ferramentas (calculadoras, etc)

---

#### GET `/api/messages/history`
Obtém histórico de conversas de uma sessão

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
- `session_id` (string, obrigatório): ID da sessão
- `limit` (int, default: 20): Número máximo de mensagens

**Response (200 OK):**
```json
{
  "success": true,
  "session_id": "abc123def456",
  "conversations": [
    {
      "id": 1,
      "user_message": "Como calcular DAS?",
      "assistant_message": "O DAS é...",
      "created_at": "2025-11-25T15:47:30.123456"
    }
  ],
  "total": 1
}
```

---

#### DELETE `/api/messages/history/{session_id}`
Deleta histórico de uma sessão

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Histórico deletado com sucesso"
}
```

---

### 🌐 Páginas Web

#### GET `/`
Página inicial (homepage)

#### GET `/chat`
Interface do chat

#### GET `/login`
Página de login

#### GET `/docs`
Documentação automática da API (Swagger)

#### GET `/redoc`
Documentação alternativa (ReDoc)

---

## 🔐 Autenticação

### Sistema JWT (JSON Web Tokens)

A aplicação usa **OAuth2 com Password Flow** e **JWT** para autenticação.

### Fluxo de Autenticação

```
1. Usuário se registra ou faz login
   ↓
2. Senha é hasheada com Argon2
   ↓
3. Credenciais validadas
   ↓
4. JWT token criado (contém user_id, role, exp)
   ↓
5. Token enviado ao cliente (localStorage)
   ↓
6. Cliente inclui token em Authorization header
   ↓
7. Servidor valida token a cada requisição
```

### Como Usar Autenticação

**1. Registrar usuário:**
```javascript
const response = await fetch('/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'usuario@example.com',
    username: 'usuario123',
    full_name: 'João Silva',
    password: 'senha123'
  })
});
```

**2. Fazer login:**
```javascript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'usuario123',
    password: 'senha123'
  })
});
const data = await response.json();
localStorage.setItem('token', data.access_token);
```

**3. Enviar mensagem com autenticação:**
```javascript
const token = localStorage.getItem('token');
const response = await fetch('/api/messages/send', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    message: 'Como calcular DAS?',
    use_history: true,
    use_tools: true
  })
});
```

### Roles (Papéis)

| Role | Descrição | Permissões |
|------|-----------|-----------|
| `user` | Usuário padrão | Usar chat, ver histórico |
| `contador` | Contador profissional | Tudo + acessar dados fiscais |
| `assistente` | Assistente administrativo | Chat + relatórios |
| `admin` | Administrador | Acesso total |

---

## 📚 Módulos Principais

### 1. `app/main.py` - Entrada da Aplicação

```python
# Inicializa FastAPI com lifespan
app = FastAPI(
    title="Agente IA Contabilidade",
    version="1.0.0",
    lifespan=lifespan
)

# Configurações:
# - CORS habilitado para todos os origins
# - Static files (frontend)
# - Routes de auth e messages
# - Health check em /health
```

**Funcionalidades:**
- Gerencia startup/shutdown
- Inicializa banco de dados
- Configura middlewares CORS
- Serve arquivos estáticos (frontend)
- Inclui rotas de autenticação e mensagens

---

### 2. `app/config.py` - Configurações

```python
class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    MAX_TOKENS: int = 1500
    TEMPERATURE: float = 0.7
    
    # App
    APP_NAME: str = "Agente IA Contabilidade"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    
    # Auth
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
```

**Carrega de:**
- Arquivo `.env`
- Variáveis de ambiente do sistema

---

### 3. `app/services/openai_services.py` - Integração OpenAI

```python
class OpenAIService:
    async def get_completion(
        user_message: str,
        conversation_history: List[Dict] = None,
        use_tools: bool = True
    ) -> Dict:
        """
        1. Monta array de mensagens com histórico
        2. Envia para OpenAI com ferramentas disponíveis
        3. Se OpenAI solicita ferramentas:
           - Executa funções localmente
           - Envia resultados novamente para OpenAI
        4. Retorna resposta final
        """
```

**Processo:**

```
┌──────────────────────────────┐
│ Construir messages array     │
│ (system + history + user)    │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Chamar OpenAI com tools      │
│ (AVAILABLE_TOOLS, auto)      │
└──────────────┬───────────────┘
               ↓
         ┌─────────────┐
         │ Tem tool    │
         │ calls?      │
         └─────┬───────┘
             /   \
           Sim    Não
           /       \
          ↓         ↓
    ┌─────────┐ ┌──────────────┐
    │Executar │ │ Retornar     │
    │funções  │ │ resposta     │
    │locais   │ │ final        │
    └────┬────┘ └──────────────┘
         ↓
    ┌─────────────────────┐
    │ Chamar OpenAI       │
    │ novamente com       │
    │ resultados das      │
    │ ferramentas         │
    └────┬────────────────┘
         ↓
    ┌──────────────────────┐
    │ Retornar resposta    │
    │ final               │
    └──────────────────────┘
```

---

### 4. `app/services/tools.py` - Ferramentas (Function Calling)

Define todas as ferramentas disponíveis para o agente usar:

#### ✅ Ferramentas Implementadas

##### 1. **Calculadora de DAS**
```python
def calcular_das(
    receita_bruta_anual: float,
    aliquota_percentual: float,
    incluir_1_3: bool = True
) -> dict
```
Calcula DAS (Documento de Arrecadação do Simples Nacional) para MEI, ME, EPP.

**Parâmetros:**
- `receita_bruta_anual`: Faturamento anual em reais
- `aliquota_percentual`: Alíquota conforme anexo (ex: 6%, 7.3%)
- `incluir_1_3`: Se deve incluir 1/3 do INSS

**Retorna:**
```json
{
  "receita_bruta_anual": 60000,
  "aliquota": 6.0,
  "das_mensal": 360,
  "das_anual": 4320,
  "incluir_inss_1_3": true,
  "inss_1_3": 180,
  "total_mensal_com_inss": 540
}
```

##### 2. **Calculadora de Férias**
```python
def calcular_ferias(
    salario_mensal: float,
    dias_ferias: int = 30,
    incluir_1_3: bool = True,
    abono_pecuniario: bool = False
) -> dict
```
Calcula férias, 1/3 constitucional e abono pecuniário.

**Parâmetros:**
- `salario_mensal`: Salário em reais
- `dias_ferias`: Dias de férias (padrão 30)
- `incluir_1_3`: Se deve incluir 1/3 (padrão sim)
- `abono_pecuniario`: Se usa abono pecuniário

**Retorna:**
```json
{
  "salario_mensal": 3000,
  "dias_ferias": 30,
  "valor_ferias": 3000,
  "um_terco_constitucional": 1000,
  "total_com_um_terco": 4000,
  "abono_pecuniario": false,
  "valor_abono": 0,
  "total_final": 4000
}
```

##### 3. **Calendário Fiscal**
```python
def obter_calendario_fiscal(
    mes: int,
    ano: int = 2025
) -> dict
```
Lista obrigações fiscais mensais com prazos.

**Parâmetros:**
- `mes`: Mês (1-12)
- `ano`: Ano (padrão 2025)

**Retorna:**
```json
{
  "mes": 11,
  "ano": 2025,
  "obrigacoes": [
    {
      "obrigacao": "SPED Fiscal",
      "prazo": "25/11/2025",
      "para_quem": "Empresas do Lucro Real",
      "observacao": "Prazo até o 25º dia do mês seguinte"
    }
  ]
}
```

##### 4. **Análise de Regime Tributário**
```python
def analisar_regime_tributario(
    receita_anual: float,
    tipo_atividade: str,
    quantidade_funcionarios: int = 0
) -> dict
```
Sugere melhor regime tributário baseado em critérios.

**Parâmetros:**
- `receita_anual`: Faturamento anual
- `tipo_atividade`: Ex: "comércio", "prestação de serviços", "indústria"
- `quantidade_funcionarios`: Número de funcionários

**Retorna:**
```json
{
  "receita_anual": 500000,
  "tipo_atividade": "comércio",
  "regimes_possiveis": [
    {
      "regime": "Simples Nacional",
      "limite_receita": "4800000",
      "aliquota_minima": "4%",
      "aliquota_maxima": "11.2%",
      "recomendacao": "Ideal para pequenas empresas",
      "vantagens": ["Menos obrigações acessórias", "Processo simplificado"],
      "desvantagens": ["Limite de faturamento", "Não pode ter filiais"]
    }
  ],
  "regime_recomendado": "Simples Nacional"
}
```

---

### 5. `app/db/database.py` - Banco de Dados

```python
# Modelos SQLAlchemy
class User(Base):
    id: int
    email: str (unique)
    username: str (unique)
    full_name: str
    hashed_password: str
    role: str (enum)
    is_active: bool
    created_at: datetime
    last_login: datetime (nullable)

class Conversation(Base):
    id: int
    user_id: int (FK)
    session_id: str
    user_message: str
    assistant_message: str
    created_at: datetime
```

**Funções principais:**
- `init_db()`: Inicializa banco de dados
- `get_db()`: Dependency injection para AsyncSession
- `save_conversation()`: Salva uma conversa
- `get_conversation_history()`: Busca histórico

---

### 6. `app/auth/security.py` - Segurança

```python
def get_password_hash(password: str) -> str:
    """Hasheia senha com Argon2"""

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica senha contra hash"""

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """Cria JWT token"""

def decode_token(token: str) -> dict:
    """Decodifica e valida JWT token"""
```

---

### 7. `app/auth/dependencies.py` - Dependências

```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Valida token e retorna usuário"""

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Valida se usuário está ativo"""

async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Valida se usuário é admin"""
```

---

### 8. `app/routes/auth.py` - Rotas de Autenticação

Endpoints para:
- `/register` - Novo usuário
- `/login` - Autenticação
- `/me` - Perfil
- `/me` (PUT) - Atualizar perfil
- `/change-password` - Trocar senha
- `/logout` - Logout

---

### 9. `app/routes/messages.py` - Rotas de Mensagens

Endpoints para:
- `/send` - Enviar mensagem
- `/history` - Ver histórico
- `/history/{session_id}` - Deletar histórico

---

### 10. `app/utils/formatters.py` - Formatação

```python
def format_response(response: str) -> str:
    """Formata resposta para exibição"""

def format_error(error: str) -> str:
    """Formata mensagens de erro"""

def sanitize_input(user_input: str) -> str:
    """Remove caracteres perigosos da entrada"""

def extract_keywords(text: str) -> list:
    """Extrai palavras-chave para busca"""

def format_conversation_history(conversations: list) -> str:
    """Formata histórico para contexto"""
```

---

## 🔨 Ferramentas (Function Calling)

### O que é Function Calling?

Function Calling permite que o modelo GPT:
1. Identifique quando precisa de uma ferramenta
2. Solicite ao servidor para executar
3. Receba o resultado
4. Use o resultado na resposta final

### Como Funciona

```
Usuário: "Qual é o DAS para um MEI com faturamento de R$60mil?"
   ↓
GPT analisa mensagem e diz:
"Preciso usar a ferramenta 'calcular_das' com receita_bruta_anual=60000"
   ↓
Servidor executa calcular_das(60000, ...)
   ↓
Resultado: { das_mensal: 360, das_anual: 4320, ... }
   ↓
GPT recebe resultado e responde:
"Para seu MEI, o DAS será R$360/mês ou R$4.320/ano..."
```

### Ferramentas Disponíveis

Definidasem `app/services/tools.py`:

1. **calcular_das** - DAS para Simples Nacional
2. **calcular_ferias** - Férias e 13º
3. **obter_calendario_fiscal** - Obrigações fiscais
4. **analisar_regime_tributario** - Comparação de regimes

Cada ferramenta tem:
- Nome e descrição
- Parâmetros com tipos e descrições
- Exemplo de uso

---

## 💾 Banco de Dados

### Tecnologia

- **SQLite** com **aiosqlite** para operações assíncronas
- **SQLAlchemy 2.0** como ORM

### Modelos

#### Tabela `user`
```sql
CREATE TABLE "user" (
  id INTEGER PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(50) UNIQUE NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'user',
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP
);
```

#### Tabela `conversation`
```sql
CREATE TABLE conversation (
  id INTEGER PRIMARY KEY,
  user_id INTEGER FOREIGN KEY,
  session_id VARCHAR(36) NOT NULL,
  user_message TEXT NOT NULL,
  assistant_message TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Operações Comuns

**Inicializar banco:**
```python
await init_db()  # Cria tabelas se não existirem
```

**Salvar conversa:**
```python
await save_conversation(
    db=session,
    user_id=user.id,
    session_id="abc123",
    user_message="Olá",
    assistant_message="Olá! Como posso ajudar?"
)
```

**Buscar histórico:**
```python
history = await get_conversation_history(
    db=session,
    session_id="abc123",
    limit=20,
    user_id=user.id
)
```

---

## 🐳 Deployment

### Deploy Local (Desenvolvimento)

```bash
# 1. Ative ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 2. Execute
uvicorn app.main:app --reload
```

Acesse: **http://localhost:8000**

### Deploy com Docker

#### 1. Build da imagem

```bash
docker build -t agente-ia-contabilidade:latest .
```

#### 2. Executar container

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e SECRET_KEY=sua-chave \
  agente-ia-contabilidade:latest
```

#### 3. Docker Compose (Opcional)

Crie `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SECRET_KEY: ${SECRET_KEY}
      DATABASE_URL: sqlite+aiosqlite:///./data/contabilidade_agent.db
    volumes:
      - ./data:/code/data
    restart: unless-stopped
```

Execute:
```bash
docker-compose up -d
```

### Deploy em Produção

**Não use `--reload` em produção!**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Ou com Docker:

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Variáveis de Ambiente em Produção

```env
DEBUG=False
OPENAI_MODEL=gpt-4o-mini
TEMPERATURE=0.5
SECRET_KEY=gerar-chave-segura-aleatorio-aqui
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
```

---

## 🆘 Troubleshooting

### ❌ Erro: "OPENAI_API_KEY not found"

**Solução:**
1. Verifique se `.env` existe na raiz do projeto
2. Confirme que `OPENAI_API_KEY` está definida
3. Reinicie a aplicação

```bash
# Verificar
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows
```

### ❌ Erro: "Could not connect to database"

**Solução:**
1. Verifique permissões da pasta (escrita)
2. Confirme caminho do banco em `.env`
3. Tente deletar `contabilidade_agent.db` (será recriado)

```bash
rm contabilidade_agent.db  # Linux/Mac
del contabilidade_agent.db  # Windows
```

### ❌ Erro: "Secret key not found"

**Solução:**
Gere uma chave segura:

```python
import secrets
print(secrets.token_urlsafe(32))
```

Adicione ao `.env`:
```env
SECRET_KEY=sua-chave-gerada-acima
```

### ❌ Erro: "Module 'app' not found"

**Solução:**
1. Verifique se está na pasta raiz do projeto
2. Confirme que `__init__.py` existe em `app/`
3. Reinstale em modo editable:

```bash
pip install -e .
```

### ❌ Erro: "Port 8000 already in use"

**Solução:**
Use porta diferente:

```bash
uvicorn app.main:app --reload --port 8001
```

Ou matar processo na porta:

```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### ❌ Erro de CORS

**Solução:**
O CORS já está configurado para aceitar todos os origins em `app/main.py`. Se ainda tiver problema, verifique:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✓ Permite todos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### ⚠️ Resposta Lenta

**Otimizações:**
1. Use modelo mais rápido: `gpt-4o-mini` (padrão)
2. Reduza `MAX_TOKENS`: de 1500 para 800
3. Aumente `temperature`: 0.3-0.5 (mais consistente)
4. Use menos histórico: `limit=3` em vez de 20

```env
OPENAI_MODEL=gpt-4o-mini
MAX_TOKENS=800
TEMPERATURE=0.5
```

### 🔄 Reiniciar Aplicação

```bash
# Parar (Ctrl+C)
# Depois:
uvicorn app.main:app --reload
```

---

## 🤝 Contribuindo

### Passos para Contribuir

1. **Fork** o repositório
2. **Clone** seu fork: `git clone ...seu-fork...`
3. **Crie branch** de feature: `git checkout -b feature/sua-feature`
4. **Commit** mudanças: `git commit -m "Add: descrição da feature"`
5. **Push** para seu fork: `git push origin feature/sua-feature`
6. **Abra Pull Request** no repositório principal

### Diretrizes de Código

- Use **Type Hints** em Python
- Siga **PEP 8**
- Adicione **docstrings** em funções
- Escreva **testes** para novas features
- Atualize **documentação** se necessário

### Reportar Bugs

Abra uma **Issue** com:
- Descrição clara do bug
- Passos para reproduzir
- Comportamento esperado
- Comportamento atual
- Screenshots (se aplicável)

---

## 📖 Recursos Adicionais

### Documentação Oficial

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [Pydantic](https://docs.pydantic.dev/)

### Livros e Guias

- "Clean Code" - Robert C. Martin
- "FastAPI Best Practices" - Blog oficial
- [Guia de Contabilidade Brasileira](https://receita.economia.gov.br/)

### Comunidades

- [FastAPI Discord](https://discord.gg/VQjSZaeJmf)
- [Python Brasil](https://python.org.br/)
- [Stack Overflow - fastapi](https://stackoverflow.com/questions/tagged/fastapi)

---

## 📄 Licença

Este projeto está sob licença **MIT**. Veja [LICENSE](../LICENSE) para detalhes.

---

## 👨‍💻 Autor

**DoubleG2s**

- GitHub: [@DoubleG2s](https://github.com/DoubleG2s)
- Email: gui.mail1@proton.me

---

## 📞 Suporte

Para dúvidas ou sugestões:

- 📧 Abra uma [Issue](https://github.com/DoubleG2s/agente-ia-contabilidade/issues)
- 💬 Envie email para: gui.mail1@proton.me

---

**Última atualização:** 25 de Novembro de 2025  
**Versão da Documentação:** 1.0.0

