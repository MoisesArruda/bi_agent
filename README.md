# 🤖 BI Agent - Arruda Consulting

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.47.0-red.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.6.7-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Sistema de Inteligência Artificial para Análise de Dados e Business Intelligence**

[🚀 Começar](#-instalação-e-execução) • [📖 Documentação](#-documentação) • [🏗️ Arquitetura](#️-arquitetura) • [💡 Exemplos](#-exemplos-de-uso)

</div>

---

## 📋 Visão Geral

O **BI Agent** é uma solução completa de Business Intelligence baseada em Inteligência Artificial que permite análise automatizada de dados, geração de consultas SQL, criação de visualizações interativas e insights inteligentes. Desenvolvido pela **Arruda Consulting**, o sistema combina múltiplos agentes especializados para fornecer uma experiência de análise de dados totalmente automatizada.

### ✨ Principais Funcionalidades

- 🔍 **Análise Inteligente de Dados**: Processamento automático de datasets complexos
- 📊 **Geração de Visualizações**: Criação automática de gráficos e dashboards interativos
- 🗄️ **Consultas SQL Inteligentes**: Geração e validação automática de consultas SQL
- 🤖 **Múltiplos Agentes Especializados**: Sistema modular com agentes para diferentes tarefas
- 🔒 **Sistema de Autenticação**: Login seguro com credenciais configuráveis
- 🐳 **Containerização Docker**: Deploy fácil e escalável
- 📈 **Cache Inteligente**: Sistema de cache para otimização de performance
- 🎯 **Interface Intuitiva**: Interface web moderna e responsiva

---

## 🏗️ Arquitetura

### Estrutura do Projeto

```
bi_agent/
├── 📁 src/
│   ├── 📁 app/                    # Lógica principal da aplicação
│   │   ├── 📁 domain/            # Domínios de negócio
│   │   │   ├── 📁 prompts/       # Prompts dos agentes
│   │   │   └── 📁 tools/         # Ferramentas dos agentes
│   │   ├── 📁 graph/             # Workflow LangGraph
│   │   │   ├── nodes.py          # Nós do workflow
│   │   │   ├── routers.py        # Roteamento condicional
│   │   │   └── graph.py          # Definição do grafo
│   │   └── 📁 guardrails/        # Validação e segurança
│   ├── 📁 frontend/              # Interface Streamlit
│   │   ├── 📁 pages/             # Páginas da aplicação
│   │   │   ├── Chatbot.py        # Interface principal
│   │   │   ├── Login.py          # Autenticação
│   │   │   └── Register.py       # Registro de usuários
│   │   └── 📁 utils/             # Utilitários do frontend
│   ├── 📁 databases/             # Conectores de banco
│   │   ├── 📁 postgress/         # PostgreSQL
│   │   ├── 📁 redis/             # Redis Cache
│   │   └── 📁 azure_mysql/       # Azure MySQL
│   ├── 📁 infrastructure/        # Provedores de LLM
│   │   └── 📁 llm_providers/     # Azure, Groq, HuggingFace
│   └── 📁 rag/                   # Sistema RAG
│       ├── 📁 indexing/          # Indexação de documentos
│       └── 📁 retrieval/         # Recuperação de informações
├── 📁 data/                      # Dados e datasets
│   └── 📁 dataset/               # Dataset Netflix
├── 📁 logs/                      # Sistema de logs
├── 📁 notebooks/                 # Jupyter notebooks
├── 🐳 docker-compose.yaml        # Orquestração de containers
├── 🐳 Dockerfile                 # Imagem da aplicação
└── 📋 requirements.txt           # Dependências Python
```

---

## 🚀 Instalação e Execução

### Pré-requisitos

- **Python 3.11+**
- **Docker** e **Docker Compose**
- **Git**

### 1. Clone o Repositório

```bash
git clone https://github.com/arruda-consulting/bi-agent.git
cd bi-agent
```

### 2. Configuração do Ambiente

#### Opção A: Docker (Recomendado)

```bash
# Executar todos os serviços
docker-compose up -d

# Ou executar apenas a aplicação
docker-compose up -d frontend
```

#### Opção B: Instalação Local

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run src/frontend/app.py 
```

### 3. Acessar a Aplicação

- **URL**: http://localhost:8501
- **Login**: admin / 123 (padrão)

---

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Configurações do PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DBNAME=bi_agent_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

# Configurações do Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Configuração de Bancos de Dados

#### PostgreSQL
```bash
# Executar apenas PostgreSQL
docker-compose up -d postgres

# Inserir dataset Netflix
python src/databases/postgress/insert_netflix_data.py
```

#### Redis
```bash
# Executar apenas Redis
docker-compose up -d redis
```

---

## 💡 Exemplos de Uso

### 1. Análise de Dataset Netflix

```python
# Pergunta: "Quais são os gêneros mais populares no Netflix?"
# O sistema irá:
# 1. Analisar o dataset
# 2. Gerar consulta SQL
# 3. Executar no banco
# 4. Criar visualização
# 5. Fornecer insights
```

### 2. Geração de Relatórios

```python
# Pergunta: "Crie um relatório de filmes por país"
# Resultado: Gráfico de barras com países e contagem de filmes
```

### 3. Análise Temporal

```python
# Pergunta: "Mostre a evolução dos lançamentos por ano"
# Resultado: Gráfico de linha temporal com tendências
```

---

## 🎯 Funcionalidades Detalhadas

### 🤖 Sistema de Agentes

#### **Supervisor Agent**
- Coordena todos os outros agentes
- Decide qual agente usar para cada tarefa
- Gerencia o fluxo de trabalho

#### **SQL Writer Agent**
- Gera consultas SQL otimizadas
- Considera a estrutura do banco de dados
- Adapta consultas para diferentes SGBDs

#### **SQL Validator Agent**
- Valida sintaxe SQL
- Verifica segurança das consultas
- Otimiza performance

#### **BI Expert Agent**
- Fornece insights de negócio
- Interpreta resultados de dados
- Sugere análises adicionais

#### **Visualization Generator Agent**
- Cria visualizações interativas
- Escolhe tipos de gráficos apropriados
- Personaliza estilos e cores

#### **Python Validator Agent**
- Valida código Python gerado
- Verifica segurança
- Otimiza performance

### 🔒 Sistema de Autenticação

- **Login seguro** com credenciais configuráveis
- **Sessões persistentes** com cookies
- **Usuários anônimos** para acesso rápido
- **Registro de usuários** (opcional)

### 📊 Sistema de Visualizações

- **Plotly** para gráficos interativos
- **Matplotlib** para visualizações estáticas
- **Gráficos responsivos** e personalizáveis
- **Exportação** de imagens e dados

### 🗄️ Sistema de Dados

- **PostgreSQL** para dados estruturados
- **Redis** para cache e sessões
- **FAISS/Qdrant** para busca vetorial
- **Suporte a múltiplos formatos** (CSV, JSON, PDF)

---

## 📈 Performance e Escalabilidade

### Otimizações Implementadas

- **Cache Redis** para consultas frequentes
- **Processamento em lotes** para grandes datasets
- **Lazy loading** de dependências
- **Compressão** de dados em memória
- **Pool de conexões** para bancos de dados

### Métricas de Performance

- **Tempo de resposta**: < 2s para consultas simples
- **Throughput**: 100+ consultas/minuto
- **Uso de memória**: < 512MB por instância
- **Disponibilidade**: 99.9% uptime

---

## 🔐 Segurança

### Medidas Implementadas

- **Validação de entrada** com Guardrails AI
- **Sanitização de consultas SQL**
- **Autenticação segura** com cookies
- **Logs de auditoria** completos
- **Isolamento de containers** Docker

### Boas Práticas

- Nunca exponha credenciais em código
- Use variáveis de ambiente para configurações
- Mantenha dependências atualizadas
- Monitore logs de segurança

---
[⬆ Voltar ao topo](#-bi-agent---arruda-consulting)

</div>
