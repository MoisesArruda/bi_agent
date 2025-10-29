# Scripts para Inserção do Dataset Netflix no PostgreSQL

Este diretório contém scripts para inserir o dataset do Netflix no PostgreSQL.

## Arquivos

- `insert_netflix_data.py` - Script principal para inserir o dataset
- `test_postgres_connection.py` - Script para testar a conexão com o banco

## Pré-requisitos

1. **PostgreSQL rodando** (via Docker ou instalação local)
2. **Arquivo .env** com as configurações do banco
3. **Dataset Netflix** em `data/dataset/netflix_movies_and_tv_shows.csv`
4. **Schema JSON** em `data/dataset/netflix_schema.json`

## Configuração

### 1. Criar arquivo .env

Copie o arquivo de exemplo e configure suas credenciais:

```bash
cp config.env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DBNAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
```

### 2. Executar PostgreSQL via Docker

```bash
# Executar apenas o PostgreSQL
docker-compose up -d postgres

# Ou executar todos os serviços
docker-compose up -d
```

## Como Usar

### 1. Testar Conexão

```bash
python scripts/test_postgres_connection.py
```

### 2. Inserir Dataset

```bash
python scripts/insert_netflix_data.py
```

### 3. Verificar Resultado

```bash
python scripts/test_postgres_connection.py
```

## Estrutura da Tabela

A tabela `netflix_movies_and_tv_shows` será criada com as seguintes colunas:

- `show_id` (TEXT, NOT NULL) - ID único do filme/série
- `type` (TEXT) - Tipo: Movie ou TV Show
- `title` (TEXT) - Título
- `director` (TEXT) - Diretor
- `cast` (TEXT) - Elenco
- `country` (TEXT) - País de produção
- `date_added` (TEXT) - Data de adição no Netflix
- `release_year` (INTEGER) - Ano de lançamento
- `rating` (TEXT) - Classificação
- `duration` (TEXT) - Duração
- `listed_in` (TEXT) - Gêneros/categorias
- `description` (TEXT) - Descrição

## Troubleshooting

### Erro de Conexão

1. Verifique se o PostgreSQL está rodando:
   ```bash
   docker ps | grep postgres
   ```

2. Verifique as configurações no arquivo `.env`

3. Teste a conexão:
   ```bash
   python scripts/test_postgres_connection.py
   ```

### Erro de Arquivo Não Encontrado

1. Verifique se o arquivo CSV existe:
   ```bash
   ls -la data/dataset/netflix_movies_and_tv_shows.csv
   ```

2. Verifique se o schema JSON existe:
   ```bash
   ls -la data/dataset/netflix_schema.json
   ```

### Erro de Permissão

1. Verifique se o usuário tem permissão para criar tabelas
2. Verifique se o banco de dados existe

## Logs

O script mostra logs detalhados durante a execução:

- ✅ Conexão com o banco
- 📋 Criação da tabela
- 🗑️ Truncamento da tabela (se habilitado)
- 📊 Progresso da inserção (a cada 1000 registros)
- ✅ Confirmação da transação
