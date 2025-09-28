import psycopg2
import csv
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
import os

load_dotenv()

def get_postgres_table_info(table_name: str):
    """
    Busca informações específicas de uma tabela no PostgreSQL.
    
    Args:
        table_name: Nome da tabela para buscar informações
        
    Returns:
        Uma string formatada com as informações da tabela específica.
    """
    try:
        db_config = {
            'host': os.getenv("POSTGRES_HOST", "localhost"),
            'dbname': os.getenv("POSTGRES_DBNAME", "postgres"),
            'user': os.getenv("POSTGRES_USER", "postgres"),
            'password': os.getenv("POSTGRES_PASSWORD", "admin"),
            'port': int(os.getenv("POSTGRES_PORT", 5432))
        }
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        query = """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_name = %s AND table_type = 'BASE TABLE' 
        AND table_schema NOT IN ('pg_catalog', 'information_schema');
        """
        
        cursor.execute(query, (table_name,))
        table_info = cursor.fetchone()
        
        if not table_info:
            return f"Tabela '{table_name}' não encontrada."
        
        schema, table = table_info
        
        query_columns = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position;
        """
        
        cursor.execute(query_columns, (schema, table))
        columns = cursor.fetchall()
        
        if not columns:
            return f"Nenhuma coluna encontrada para a tabela '{table_name}'."
        
        column_details = []
        for col in columns:
            col_name, data_type, is_nullable, default_value = col
            # nullable_info = "NULL" if is_nullable == "YES" else "NOT NULL"
            default_info = f" DEFAULT {default_value}" if default_value else ""
            column_details.append(f"{col_name} ({data_type}) {default_info}")
        
        result = f"{schema}.{table}"
        # result += "Colunas:\n"
        # result += "\n".join([f"  - {col}" for col in column_details])
        
        return result, column_details

    except Exception as e:
        print(f"Erro ao buscar informações da tabela: {e}")
        return ""
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def execute_query_postgress(query: str):
    try:
        db_config = {
            'host': os.getenv("POSTGRES_HOST", "localhost"),
            'dbname': os.getenv("POSTGRES_DBNAME", "postgres"),
            'user': os.getenv("POSTGRES_USER", "postgres"),
            'password': os.getenv("POSTGRES_PASSWORD", "admin"),
            'port': int(os.getenv("POSTGRES_PORT", 5432))
        }
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute(query)
        result = cursor.fetchall()

        return result

    except Exception as e:
        print(f"Erro ao executar consulta: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    print(get_postgres_table_info("netflix_movies_and_tv_shows"))