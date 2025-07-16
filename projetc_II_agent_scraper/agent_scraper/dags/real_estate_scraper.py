from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import requests
from bs4 import BeautifulSoup
import logging

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 7, 15),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'debug_real_estate_scraper',
    default_args=default_args,
    description='DAG de debug para scraping',
    schedule_interval=None,
    catchup=False,
)

def debug_scrape():
    logger = logging.getLogger(__name__)
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # Dados mockados para teste - substitua por scraping real depois
    test_data = {
        'titulo': 'Apartamento Teste Debug',
        'preco': 350000.00,
        'area': 70,
        'quartos': 2,
        'endereco': 'Rua Debug, 123',
        'bairro': 'Centro',
        'cidade': 'Debug City',
        'url_anuncio': 'https://exemplo.com/debug',
        'fonte': 'debug'
    }
    
    try:
        with pg_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO imoveis_scraper.anuncios (
                        titulo, preco, area, quartos, endereco, 
                        bairro, cidade, url_anuncio, fonte
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    test_data['titulo'],
                    test_data['preco'],
                    test_data['area'],
                    test_data['quartos'],
                    test_data['endereco'],
                    test_data['bairro'],
                    test_data['cidade'],
                    test_data['url_anuncio'],
                    test_data['fonte']
                ))
                
                cursor.execute("""
                    INSERT INTO imoveis_scraper.execucoes 
                    (total_anuncios, status, detalhes)
                    VALUES (%s, %s, %s)
                """, (1, 'sucesso', 'Dados de teste inseridos'))
                
                conn.commit()
                logger.info("Dados de teste inseridos com sucesso!")
                
    except Exception as e:
        logger.error(f"ERRO CRÍTICO: {str(e)}")
        raise

debug_task = PythonOperator(
    task_id='debug_scrape_task',
    python_callable=debug_scrape,
    dag=dag,
)