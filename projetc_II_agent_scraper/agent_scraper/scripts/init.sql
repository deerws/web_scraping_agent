CREATE SCHEMA IF NOT EXISTS imoveis_scraper;

-- Tabela principal para anúncios
CREATE TABLE IF NOT EXISTS imoveis_scraper.anuncios (
    id SERIAL PRIMARY KEY,
    titulo TEXT,
    preco NUMERIC,
    area NUMERIC,
    quartos INTEGER,
    endereco TEXT,
    bairro TEXT,
    cidade TEXT,
    url_anuncio TEXT UNIQUE,
    fonte TEXT,
    detalhes TEXT,
    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de log de execuções
CREATE TABLE IF NOT EXISTS imoveis_scraper.execucoes (
    id SERIAL PRIMARY KEY,
    data_execucao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_anuncios INTEGER,
    status TEXT,
    detalhes TEXT
);

-- Permissões
GRANT ALL PRIVILEGES ON SCHEMA imoveis_scraper TO airflow;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA imoveis_scraper TO airflow;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA imoveis_scraper TO airflow;