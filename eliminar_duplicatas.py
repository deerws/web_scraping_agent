import pandas as pd
from sqlalchemy import create_engine


database_file = './apartamentos.db'
engine = create_engine(f'sqlite:///{database_file}')
df = pd.read_sql('apartamentos', con=engine)


df_duplicates = df[df.duplicated(subset=['Área', 'Preço', 'Quartos', 'Banheiros', 'Vagas de Garagem', 'Endereço'], keep=False)]


if not df_duplicates.empty:
    print("Duplicatas encontradas e removidas:")
    print(df_duplicates)


else:
    print("Não há duplicatas no conjunto de dados.")


df_deduplicated = df.drop_duplicates(subset=['Área', 'Preço', 'Quartos', 'Banheiros', 'Vagas de Garagem', 'Endereço'], keep='first')
df_deduplicated.to_sql('apartamentos', con=engine, if_exists='replace', index=False)


print("Duplicatas eliminadas e dados atualizados com sucesso!")
