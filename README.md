# 🤖 Agente de IA para Contabilidade

Agente de IA especializado em contabilidade brasileira, construído com FastAPI e OpenAI GPT. Oferece respostas inteligentes sobre obrigações fiscais, cálculos tributários e questões trabalhistas, com suporte a ferramentas (function calling) para cálculos automatizados.

![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-green)
![OpenAI](https://img.shields.io/badge/OpenAI-API-orange)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Funcionalidades

### 🧠 IA Conversacional
- Respostas contextualizadas sobre contabilidade brasileira
- Memória de conversas (histórico persistente por sessão)
- Interface de chat moderna com suporte a Markdown
- Streaming de respostas em tempo real

### 🛠️ Ferramentas Integradas (Function Calling)
- **Calculadora de DAS**: Calcula tributos do Simples Nacional (Anexos I a V)
- **Calculadora de Férias**: Calcula férias, 1/3 constitucional e abono pecuniário
- **Calendário Fiscal**: Lista obrigações fiscais mensais com prazos
- **Análise de Regime Tributário**: Sugere melhor regime (Simples, Lucro Presumido, Lucro Real)

### 📊 Especialidades
- Simples Nacional (MEI, ME, EPP)
- Lucro Real e Lucro Presumido
- SPED, NFe, DAS, DARF
- Folha de pagamento e questões trabalhistas
- Obrigações acessórias

## 🚀 Tecnologias

- **FastAPI** - Framework web assíncrono de alta performance
- **OpenAI GPT-4** - Modelo de linguagem com function calling
- **SQLAlchemy** - ORM com suporte assíncrono (SQLite)
- **Pydantic** - Validação de dados e settings
- **Uvicorn** - Servidor ASGI
- **Marked.js** - Renderização de Markdown no frontend
- **Highlight.js** - Syntax highlighting para código

## 📋 Pré-requisitos

- Python 3.13+ (compatível com 3.11+)
- Chave de API da OpenAI ([obter aqui](https://platform.openai.com/api-keys))
- Git

## ⚙️ Instalação

### 1. Clone o repositório

git clone https://github.com/seu-usuario/agente-ia-contabilidade.git
cd agente-ia-contabilidade


### 2. Crie e ative o ambiente virtual

Windows
python -m venv venv
venv\Scripts\activate

Linux/Mac
python3 -m venv venv
source venv/bin/activate


### 3. Instale as dependências

pip install -r requirements.txt


### 4. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:

OpenAI API
OPENAI_API_KEY=sk-sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini
MAX_TOKENS=1500
TEMPERATURE=0.7

Aplicação
APP_NAME=Agente IA Contabilidade
APP_VERSION=1.0.0
DEBUG=True

Database
DATABASE_URL=sqlite+aiosqlite:///./contabilidade_agent.db


### 5. Execute a aplicação

uvicorn app.main:app --reload


A aplicação estará disponível em: [**http://localhost:8000**](http://localhost:8000)

## 📖 Como Usar

### Interface Web (Chat)
Acesse: [**http://localhost:8000/chat**](http://localhost:8000/chat)

Exemplos de perguntas:
- *"Calcule a DAS de uma empresa com receita de R$ 250.000 no anexo 1"*
- *"Quanto vou receber de férias se meu salário é R$ 3.500 e vou vender 10 dias?"*
- *"Quais são as obrigações fiscais deste mês?"*
- *"Qual o melhor regime tributário para uma empresa que fatura R$ 600.000/ano?"*

### API REST

#### Enviar Mensagem

POST /api/messages/send
Content-Type: application/json

{
"message": "Calcule a DAS para receita de R$ 180.000 no anexo 3",
"session_id": "opcional-123",
"use_history": true,
"use_tools": true
}


#### Documentação Interativa
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Estrutura do Projeto

meu-agente-ia/
│
├── app/
│ ├── main.py # Aplicação FastAPI principal
│ ├── config.py # Configurações e settings
│ │
│ ├── routes/
│ │ └── messages.py # Endpoints da API
│ │
│ ├── services/
│ │ ├── openai_service.py # Integração com OpenAI
│ │ └── tools.py # Ferramentas (function calling)
│ │
│ ├── db/
│ │ └── database.py # Modelos e conexão do banco
│ │
│ └── utils/
│ └── formatters.py # Funções utilitárias
│
├── frontend/
│ └── index.html # Interface de chat
│
├── .env # Variáveis de ambiente (não commitado)
├── .gitignore
├── requirements.txt # Dependências Python
├── Dockerfile # Container Docker
└── README.md # Este arquivo


## 🧪 Testes

Teste as ferramentas via chat:

"Calcule a DAS de uma empresa do Simples anexo 1 com R$ 250.000 de receita"
✅ Retorna cálculo detalhado com alíquotas e valor da DAS

"Quanto recebo de férias com salário de R$ 4.000 vendendo 10 dias?"
✅ Retorna cálculo de férias, 1/3 e abono pecuniário

"Quais obrigações fiscais de novembro?"
✅ Lista DAS, DARF, GPS, FGTS, SEFIP com prazos

"Melhor regime para receita anual de R$ 800.000?"
✅ Analisa e sugere Simples vs Lucro Presumido


## 🐳 Docker (Opcional)

Build
docker build -t agente-ia-contabilidade .

Run
docker run -d -p 8000:8000 --env-file .env agente-ia-contabilidade


## 🔮 Roadmap / Próximas Evoluções

- [ ] Upload e análise de documentos (PDFs, NFes)
- [ ] Dashboard de analytics com métricas de uso
- [ ] Integração com WhatsApp (Twilio/Evolution API)
- [ ] Sistema de autenticação multi-usuário
- [ ] RAG com base de conhecimento (legislações, normas)
- [ ] Calculadora de IRPF
- [ ] Geração de relatórios em PDF
- [ ] API de consulta CNPJ (Receita Federal)

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se livre para abrir issues ou pull requests.

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

Desenvolvido com ❤️ para facilitar o trabalho de escritórios de contabilidade.

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web excepcional
- [OpenAI](https://openai.com/) - API de IA poderosa
- Comunidade Python e open source

---

**⚠️ Aviso Legal**: Este agente fornece informações gerais sobre contabilidade. Para decisões financeiras e tributárias importantes, consulte sempre um contador profissional.

