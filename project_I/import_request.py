from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)


url = 'https://www.zapimoveis.com.br/venda/apartamentos/go+goiania++setor-marista/'


driver.get(url)
driver.implicitly_wait(10)


html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
driver.quit()


areas = [item.text.strip() for item in soup.find_all('li', {'data-cy': 'rp-cardProperty-propertyArea-txt'})]
precos = [div.find('p', class_='l-text').text.strip() for div in soup.find_all('div', {'data-cy': 'rp-cardProperty-price-txt'})]
quartos = [item.text.strip() for item in soup.find_all('li', {'data-cy': 'rp-cardProperty-bedroomQuantity-txt'})]
banheiros = [item.text.strip() for item in soup.find_all('li', {'data-cy': 'rp-cardProperty-bathroomQuantity-txt'})]
vagas = [item.text.strip() for item in soup.find_all('li', {'data-cy': 'rp-cardProperty-parkingSpacesQuantity-txt'})]
enderecos = [item.text.strip() for item in soup.find_all('p', {'data-cy': 'rp-cardProperty-street-txt'})]


print("Valores extraídos:")
print("Áreas:", areas)
print("Preços:", precos)
print("Quartos:", quartos)
print("Banheiros:", banheiros)
print("Vagas:", vagas)
print("Endereços:", enderecos)


print("Tamanhos das listas extraídas:")
print("Áreas:", len(areas))
print("Preços:", len(precos))
print("Quartos:", len(quartos))
print("Banheiros:", len(banheiros))
print("Vagas:", len(vagas))
print("Endereços:", len(enderecos))


min_length = min(len(areas), len(precos), len(quartos), len(banheiros), len(vagas), len(enderecos))


areas = areas[:min_length]
precos = precos[:min_length]
quartos = quartos[:min_length]
banheiros = banheiros[:min_length]
vagas = vagas[:min_length]
enderecos = enderecos[:min_length]


data = {
    'Área': areas,
    'Preço': precos,
    'Quartos': quartos,
    'Banheiros': banheiros,
    'Vagas de Garagem': vagas,
    'Endereço': enderecos
}
df = pd.DataFrame(data)


print("DataFrame criado:")
print(df)


database_file = './apartamentos.db'
engine = create_engine(f'sqlite:///{database_file}')
df.to_sql('apartamentos', con=engine, if_exists='replace', index=False)


print("Dados armazenados com sucesso!")