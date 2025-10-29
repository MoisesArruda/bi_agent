#!/usr/bin/env python3
"""
Script para testar a conexão com o PostgreSQL e verificar se a tabela foi criada.
"""

import sys
import os
import psycopg2
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

load_dotenv()

def test_postgres_connection():
    """
    Testa a conexão com o PostgreSQL.
    """
    try:
        db_config = {
            'host': os.getenv("POSTGRES_HOST", "localhost"),
            'dbname': os.getenv("POSTGRES_DBNAME", "postgres"),
            'user': os.getenv("POSTGRES_USER", "postgres"),
            'password': os.getenv("POSTGRES_PASSWORD", "admin"),
            'port': int(os.getenv("POSTGRES_PORT", 5432))
        }
        
        print("🔌 Testando conexão com PostgreSQL...")
        print(f"Host: {db_config['host']}:{db_config['port']}")
        print(f"Database: {db_config['dbname']}")
        print(f"User: {db_config['user']}")
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Testar consulta simples
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Conexão bem-sucedida!")
        print(f"Versão do PostgreSQL: {version[0]}")
        
        # Verificar se a tabela existe
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'netflix_movies_and_tv_shows';
        """)
        
        table_exists = cursor.fetchone()
        if table_exists:
            print("✅ Tabela 'netflix_movies_and_tv_shows' encontrada!")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM netflix_movies_and_tv_shows;")
            count = cursor.fetchone()[0]
            print(f"📊 Total de registros na tabela: {count}")
            
            # Mostrar algumas amostras
            cursor.execute("SELECT show_id, title, type FROM netflix_movies_and_tv_shows LIMIT 5;")
            samples = cursor.fetchall()
            print("\n📋 Primeiros 5 registros:")
            for sample in samples:
                print(f"  - {sample[0]}: {sample[1]} ({sample[2]})")
        else:
            print("❌ Tabela 'netflix_movies_and_tv_shows' não encontrada!")
            print("💡 Execute o script de inserção primeiro.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False
    
    return True

def main():
    """
    Função principal.
    """
    print("=== TESTE DE CONEXÃO POSTGRESQL ===")
    success = test_postgres_connection()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
        return 0
    else:
        print("\n❌ Teste falhou!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
