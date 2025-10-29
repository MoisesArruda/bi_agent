import pandas as pd
import psycopg2
import csv
import json
import os
from dotenv import load_dotenv
import sys

load_dotenv()

def map_json_type_to_postgres(json_type):
    """
    Mapeia tipos JSON para tipos PostgreSQL.
    
    Args:
        json_type: Tipo do campo no JSON schema.
        
    Returns:
        Tipo PostgreSQL correspondente.
    """
    type_mapping = {
        'STRING': 'TEXT',
        'INTEGER': 'INTEGER',
        'FLOAT': 'REAL',
        'BOOLEAN': 'BOOLEAN',
        'DATE': 'DATE',
        'TIMESTAMP': 'TIMESTAMP'
    }
    return type_mapping.get(json_type, 'TEXT')

def csv_to_postgres(db_config, table_name, csv_path, schema_path, truncate_table=True):
    """
    Upload CSV data to PostgreSQL with schema validation.

    Args:
        db_config: Dictionary with PostgreSQL connection parameters (host, dbname, user, password, port).
        table_name: PostgreSQL table name.
        csv_path: Path to CSV file.
        schema_path: Path to JSON schema file.
        truncate_table: Whether to truncate the table before inserting data.
    """
    # Load schema from JSON file
    try:
        print(f"Carregando o esquema do arquivo JSON: {schema_path}")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_json = json.load(f)
        print("Esquema JSON carregado com sucesso.")
    except UnicodeDecodeError as e:
        print(f"Erro de codificação ao carregar o arquivo JSON: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Erro de formatação no arquivo JSON: {e}")
        return

    try:
        print("Conectando ao banco de dados PostgreSQL...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        print("Conexão com o banco de dados bem-sucedida.")
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return

    try:
        print(f"Criando a tabela '{table_name}' no banco de dados...")
        create_table_query = generate_create_table_query(table_name, schema_json)
        print(f"Query de criação da tabela: {create_table_query}")
        cursor.execute(create_table_query)
        print(f"Tabela '{table_name}' criada ou já existente.")
    except Exception as e:
        print(f"Erro ao criar a tabela: {e}")
        conn.close()
        return

    if truncate_table:
        try:
            print(f"Truncando a tabela '{table_name}'...")
            cursor.execute(f"TRUNCATE TABLE {table_name};")
            print(f"Tabela '{table_name}' truncada com sucesso.")
        except Exception as e:
            print(f"Erro ao truncar a tabela: {e}")
            conn.close()
            return

    try:
        print(f"Lendo o arquivo CSV: {csv_path}")
        with open(csv_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader)  # Read the header row
            print(f"Headers do CSV: {headers}")
            insert_query = generate_insert_query(table_name, headers)
            print(f"Query de inserção: {insert_query}")

            batch_size = 1000
            batch_count = 0
            total_rows = 0

            for row in reader:
                # Substituir strings vazias por None (equivalente a NULL no PostgreSQL)
                row = [None if value == "" else value for value in row]
                cursor.execute(insert_query, row)
                total_rows += 1
                
                # Commit a cada batch_size registros para melhor performance
                if total_rows % batch_size == 0:
                    conn.commit()
                    batch_count += 1
                    print(f"Processados {total_rows} registros (batch {batch_count})")
                    
        print(f"Dados do arquivo CSV '{csv_path}' inseridos com sucesso na tabela '{table_name}'.")
        print(f"Total de registros inseridos: {total_rows}")
    except Exception as e:
        print(f"Erro ao inserir dados do CSV: {e}")
        conn.close()
        return

    try:
        conn.commit()
        print("Transação confirmada.")
    except Exception as e:
        print(f"Erro ao confirmar a transação: {e}")
    finally:
        cursor.close()
        conn.close()
        print("Conexão com o banco de dados encerrada.")


def generate_create_table_query(table_name, schema_json):
    """
    Generate a CREATE TABLE query based on the schema JSON.

    Args:
        table_name: PostgreSQL table name.
        schema_json: JSON schema defining the table structure.

    Returns:
        CREATE TABLE SQL query as a string.
    """
    columns = []
    for field in schema_json:
        column_name = f'"{field["name"]}"'  # Escapar o nome da coluna com aspas duplas
        column_type = map_json_type_to_postgres(field['type'])
        column_mode = 'NOT NULL' if field.get('mode', 'NULLABLE') == 'REQUIRED' else ''
        columns.append(f"{column_name} {column_type} {column_mode}")

    columns_sql = ', '.join(columns)
    return f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql});"


def generate_insert_query(table_name, headers):
    """
    Generate an INSERT query for the given table and headers.

    Args:
        table_name: PostgreSQL table name.
        headers: List of column names.

    Returns:
        INSERT SQL query as a string.
    """
    columns = ', '.join([f'"{header}"' for header in headers])  # Escapar os nomes das colunas
    placeholders = ', '.join(['%s'] * len(headers))
    return f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"


def insert_netflix_dataset():
    """
    Função específica para inserir o dataset do Netflix no PostgreSQL.
    """
    # Configuração do banco de dados
    db_config = {
        'host': os.getenv("POSTGRES_HOST", "localhost"),
        'dbname': os.getenv("POSTGRES_DBNAME", "postgres"),
        'user': os.getenv("POSTGRES_USER", "postgres"),
        'password': os.getenv("POSTGRES_PASSWORD", "admin"),
        'port': int(os.getenv("POSTGRES_PORT", 5432))
    }
    
    # Caminhos dos arquivos
    csv_path = "data/dataset/netflix_movies_and_tv_shows.csv"
    schema_path = "data/dataset/netflix_schema.json"
    table_name = "netflix_movies_and_tv_shows"
    
    print("=== INSERÇÃO DO DATASET NETFLIX NO POSTGRESQL ===")
    print(f"Arquivo CSV: {csv_path}")
    print(f"Schema JSON: {schema_path}")
    print(f"Tabela: {table_name}")
    print(f"Configuração do banco: {db_config['host']}:{db_config['port']}/{db_config['dbname']}")
    print("=" * 50)
    
    # Executar a inserção
    csv_to_postgres(db_config, table_name, csv_path, schema_path, truncate_table=True)


if __name__ == "__main__":
    try:
        insert_netflix_dataset()
        print("✅ Dataset Netflix inserido com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inserir dataset: {e}")
        sys.exit(1)
    
    sys.exit(0)
