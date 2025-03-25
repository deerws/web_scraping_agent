import pandas as pd
from sqlalchemy import create_engine


host = 'localhost'
user = 'root'
password = 'Italia010304'
database = 'apartamentos_db'


# Criar conexão com o banco de dados MySQL
engine_mysql = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')


# Conectar ao banco de dados SQLite existente
sqlite_file = './apartamentos.db'
engine_sqlite = create_engine(f'sqlite:///{sqlite_file}')


# Ler os dados do banco de dados SQLite
df_update = pd.read_sql('apartamentos', con=engine_sqlite)


# Exibir os dados a serem enviados
print("Dados a serem enviados para o MySQL:")
print(df_update)


# Enviar os dados para o MySQL
table_name = 'apartamentos'
df_update.to_sql(table_name, con=engine_mysql, if_exists='replace', index=False)


print("Dados enviados com sucesso para o banco de dados MySQL!")


