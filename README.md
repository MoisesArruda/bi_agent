# BI Agent

TAVILLI APY KEY - https://app.tavily.com/home

## Estrutura do Projeto

```
BI_Agent/
├── data/                           # Diretório para armazenamento de dados
├── docker-compose.yaml            # Configuração do Docker Compose
├── Dockerfile                     # Configuração do Docker
├── notebooks/                     # Jupyter notebooks para análise e experimentação
├── README.md                      # Documentação do projeto
├── requirements.txt               # Dependências Python do projeto
├── src/                          # Código fonte principal
│   ├── bi_agent/                 # Módulo principal do agente BI
│   │   ├── aplication/           # Camada de aplicação
│   │   │   └── chat_service/     # Serviços de chat
│   │   └── domain/               # Camada de domínio
│   │       ├── memory/           # Gerenciamento de memória
│   │       ├── prompts/          # Templates de prompts
│   │       ├── tools/            # Ferramentas do agente
│   │       └── utils.py          # Utilitários do domínio
│   └── infrastructure/           # Camada de infraestrutura
│       ├── db/                   # Configurações de banco de dados
│       ├── llm_providers/        # Provedores de LLM
│       ├── mcp_clients/          # Clientes MCP (Model Context Protocol)
│       └── monitoring/           # Monitoramento e observabilidade
└── tests/                        # Testes automatizados
```

## Descrição das Pastas

### `/src/bi_agent/`
Módulo principal que contém a lógica de negócio do agente de Business Intelligence.

### `/src/bi_agent/aplication/`
Camada de aplicação responsável por orquestrar os casos de uso e serviços.

### `/src/bi_agent/domain/`
Camada de domínio contendo as regras de negócio, entidades e interfaces.

### `/src/infrastructure/`
Camada de infraestrutura que implementa as interfaces definidas no domínio.

### `/data/`
Diretório para armazenamento de dados, datasets e arquivos de configuração.

### `/notebooks/`
Jupyter notebooks para análise exploratória, prototipagem e experimentação.

### `/tests/`
Testes automatizados para garantir a qualidade e funcionamento do código.


src/app/
├── core/                    # �� Lógica central
│   ├── config/             # Configurações (settings.py, database.py)
│   ├── exceptions/         # Exceções customizadas
│   └── middleware/         # Middlewares (auth, logging, etc.)
├── services/               # 🆕 Serviços de negócio
│   ├── chat_service.py     # Orquestração do chat
│   ├── sql_service.py      # Processamento SQL
│   └── validation_service.py # Validações
└── api/                    # ✅ Manter como está


src/shared/
├── utils/                  # 🆕 Utilitários gerais
│   ├── file_utils.py      # Manipulação de arquivos
│   ├── text_utils.py      # Processamento de texto
│   └── date_utils.py      # Manipulação de datas
├── constants/             # 🆕 Constantes centralizadas
│   ├── api_constants.py   # Constantes da API
│   └── db_constants.py    # Constantes de banco
└── types/                 # 🆕 Tipos e schemas
    ├── schemas.py         # Pydantic schemas
    └── types.py           # Type hints


docs/
├── api/                   # �� Documentação da API
│   ├── endpoints.md      # Documentação dos endpoints
│   └── examples.md       # Exemplos de uso
├── architecture/         # 🆕 Documentação arquitetural
│   ├── overview.md      # Visão geral
│   └── components.md    # Componentes do sistema
└── deployment/          # �� Guias de deploy
    ├── docker.md        # Deploy com Docker
    └── production.md    # Deploy em produção

scripts/
├── setup/               # �� Scripts de configuração
│   ├── install.sh      # Instalação do projeto
│   └── setup_env.py    # Configuração do ambiente
├── migration/          # 🆕 Scripts de migração
│   └── migrate_data.py # Migração de dados
└── maintenance/        # 🆕 Scripts de manutenção
    ├── cleanup.py      # Limpeza de logs/cache
    └── backup.py       # Backup de dados