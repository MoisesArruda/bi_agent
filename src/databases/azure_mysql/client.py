import os
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv(override=True)

class AzureSQLManager:
    def __init__(self):

        self._hostname = os.getenv("HOST")
        self._username = os.getenv("USERNAME")
        self._password = os.getenv("PASSWORD")
        self._database = os.getenv("DATABASE")
        # assert os.path.exists(ssl_cert_path), f"Certificado não encontrado em: {ssl_cert_path}"
        # self._ssl_ca = ssl_cert_path
        self._port = int(os.getenv("PORT", 3306))
        self.conn = None

    def connect(self):
        """Estabelece conexão com o banco Azure SQL."""
        try:
            if not self.conn:
                self.conn = mysql.connector.connect(
                    host=self._hostname,
                    user=self._username,
                    password=self._password,
                    database=self._database,
                    port=self._port,
                    # ssl_ca=self._ssl_ca,
                    ssl_disabled=False
                )
            print("Conexão Azure SQL estabelecida com sucesso!")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Erro na conexão Azure SQL: Usuário ou senha incorretos.")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"Erro na conexão Azure SQL: O banco de dados '{self._database}' não existe.")
            else:
                print(f"Erro na conexão Azure SQL: {err}")
            raise

    def disconnect(self):
        """Fecha a conexão."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            print("Conexão Azure SQL encerrada.")

    def test_connection(self) -> bool:
        """Testa a conexão."""
        try:
            self.connect()
            # Testa se consegue listar tabelas
            tables = self._get_database_tables()
            self.disconnect()
            print("Conexão Azure SQL testada com sucesso!")
            return True
        except Exception as e:
            print(f"Falha no teste de conexão Azure SQL: {e}")
            return False

    def dataframe_to_sql(self, df: pd.DataFrame, table_name: str, if_exists: str = 'replace', index: bool = False):
      """
      Armazena um DataFrame do Pandas em uma tabela no banco de dados usando SQLAlchemy para melhor performance.

      Args:
          df: O DataFrame a ser armazenado.
          table_name: O nome da tabela no banco de dados.
          if_exists: O que fazer se a tabela já existir ('fail', 'replace', 'append').
          index: Se True, escreve o índice do DataFrame como uma coluna.
      """
      print(f"Iniciando a inserção de {len(df)} linhas na tabela '{table_name}'...")
      if not self._username or not self._password or not self._hostname:
          print("❌ Erro: As credenciais do banco (HOST, USERNAME, PASSWORD) não foram carregadas. Verifique seu arquivo .env.")
          return
        
      try:
            # URL-encode o usuário e a senha para lidar com caracteres especiais (como @, :, /) de forma segura.
            safe_username = quote_plus(self._username)
            safe_password = quote_plus(self._password)

            # Formato da string de conexão para SQLAlchemy com mysql-connector
            connection_string = (
                f"mysql+mysqlconnector://{safe_username}:{safe_password}@"
                f"{self._hostname}:{self._port}/{self._database}"
            )
            
            engine = create_engine(connection_string,
                                   connect_args={'ssl_ca': self._ssl_ca} if self._ssl_ca else {})
            
            # Usar o método to_sql do pandas
            df.to_sql(
                name=table_name,
                con=engine,
                if_exists=if_exists,
                index=index,
                chunksize=1000,  # Insere em lotes de 1000 linhas
                method='multi'   # Usa inserções multi-valor para maior velocidade
            )
            print(f"✅ Sucesso! Os dados foram inseridos na tabela '{table_name}'.")

      except SQLAlchemyError as e:
          print(f"❌ Falha ao criar a engine SQLAlchemy ou ao inserir dados: {e}")
          raise
      except Exception as e:
          print(f"❌ Falha ao inserir DataFrame no banco de dados: {e}")
          raise

    # To usando no Graph
    def get_table_info(self, table_name: str ):
        """
        Busca informações de colunas para uma tabela específica no MySQL, 
        adaptado da função do PostgreSQL.
        
        Returns:
            Uma tupla contendo (nome_da_tabela_com_schema, lista_de_detalhes_das_colunas)
            ou (mensagem_de_erro, None)
        """
        try:
            self.connect()  # Garante que a conexão está ativa

            # Usar um cursor de dicionário torna o código mais legível
            cursor = self.conn.cursor(dictionary=True)

            # A query para encontrar a tabela é quase idêntica.
            # Apenas ajustamos o filtro de schemas do sistema.
            query_table_check = """
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
            """
            cursor.execute(query_table_check, (self._database, table_name))

            if not cursor.fetchone():
                return f"Tabela '{table_name}' não encontrada no banco '{self._database}'.", None

            # A query para obter as colunas é praticamente a mesma!
            query_columns = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position;
            """
            cursor.execute(query_columns, (self._database, table_name))
            columns = cursor.fetchall()

            if not columns:
                return f"Nenhuma coluna encontrada para a tabela '{table_name}'.", None
          

            column_details = []
            for col in columns:
                # nullable_info = "NULL" if col['is_nullable'] == "YES" else "NOT NULL"
                default_value = col.get('COLUMN_DEFAULT')
                default_info = f" DEFAULT {default_value}" if default_value else ""
                
                column_name = col.get('COLUMN_NAME', 'N/A')
                data_type = col.get('DATA_TYPE', 'N/A')

                column_details.append(f"{column_name} ({data_type}){default_info}")
            
            result_table_name = f"{self._database}.{table_name}"
            
            return result_table_name, column_details

        except mysql.connector.Error as e:
            print(f"Erro ao buscar informações da tabela no MySQL: {e}")
            return f"Erro ao buscar informações da tabela: {e}", None
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def _connect(self):
      """Método interno para conexão (mantido para compatibilidade)."""
      # Corrigido para usar mysql.connector consistentemente
      if not self.conn or not self.conn.is_connected():
          self.connect()
      return self.conn
    
    def _querying(self, query: str, force_use_db=True):
        """Executa query e retorna resultados."""
        if self.conn is None:
            self._connect()
        cursor = self.conn.cursor()
        if force_use_db:
          cursor.execute(f"USE {self._database};")
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
        
    def _execute_query(self, query: str):
        """Executa query sem retorno."""
        if self.conn is None:
            self._connect()
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
        cursor.close()

    def _get_database_tables(self):
        """Lista tabelas do banco."""
        tables = self._querying('SHOW TABLES')
        print(f"Lista de tabelas no banco {self._database}:\n")
        for table in tables:
            print(f"- {table[0]}")
        return [table[0] for table in tables]
    
    def get_lines_from_table(self, table, limit=False, number_of_lines=None):
        """Obtém linhas de uma tabela."""
        query = f"SELECT * FROM `{table}`"
        if limit and number_of_lines is not None:
            query += f" LIMIT {number_of_lines}"
        result = self._querying(query)
        return result
    
    def closing(self):
        """Fecha conexão (método legado)."""
        self.disconnect()

    def _is_on_database(self, table_name: str):
        """Verifica se tabela existe."""
        try:
            tables = self._get_database_tables()
            if table_name not in tables:
                raise Exception(f'Tabela "{table_name}" não encontrada no banco {self._database}')
        except Exception as e:
            return False
        return True

    def _execute_query_with_dict(self, query: str, attr: dict):
        """Executa query com parâmetros em dicionário."""
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, attr)
            self.conn.commit()
        except TypeError as e:
            raise Exception(f'Erro durante inserção no banco {self._database}: {e}')
        except Exception as e:
            raise Exception(f'Erro de banco: {e}')
        finally:
            if cursor:
                cursor.close()

    def _returning_key_list_and_placeholders(self, attr: dict):
        """Retorna lista de chaves e placeholders para query."""
        key_list = ', '.join([f"`{key}`" for key in attr.keys()])
        placeholder = ', '.join([f'%({key})s' for key in attr.keys()])
        return key_list, placeholder

    # CRUD OPERATIONS (mantidos para compatibilidade)
    def create_line(self, attr: dict, table_name: str):
        """Cria linha na tabela."""
        if not self._is_on_database(table_name):
            return False
        
        key_list, placeholders = self._returning_key_list_and_placeholders(attr)
        insertion_query = f"INSERT INTO `{table_name}` ({key_list}) VALUES ({placeholders})"
        try: 
            self._execute_query_with_dict(insertion_query, attr)
            return True
        except Exception as e:
            print(f"Erro ao criar linha: {e}")
            return False

    def alter_table(self, table_name, query):
        """Altera estrutura da tabela."""
        if not self._is_on_database(table_name):
            return False
        
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao alterar tabela: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def read_table(self, table_name):
        """Lê dados da tabela."""
        if not self._is_on_database(table_name):
            return None
        return self.get_lines_from_table(table=table_name)

    def update_instance_by_id(self, table_name, id, data: dict):
        """Atualiza instância por ID."""
        if not self._is_on_database(table_name):
            return
        
        data['id'] = id
        set_clause = ', '.join([f"`{key}` = %({key})s" for key in data.keys() if key != 'id'])
        update_query = f'UPDATE `{table_name}` SET {set_clause} WHERE id = %(id)s'
        try:
            self._execute_query_with_dict(update_query, data)
        except Exception as e:
            print(f"Erro ao atualizar linha: {e}")

    def delete_instance(self, table_name: str, condition: str, value):
        """Deleta instância."""
        if not self._is_on_database(table_name):
            return
        
        delete_query = f'DELETE FROM `{table_name}` WHERE `{condition}` = %s'
        try:
            cursor = self.conn.cursor()
            cursor.execute(delete_query, (value,))
            self.conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Erro ao deletar linha: {e}")


    
if __name__ == "__main__":
    # python -m src.databases.azure_mysql.client
    db = AzureSQLManager()
    db.connect()
    print(db.get_table_info("netflix"))
    db.disconnect()