import pandas as pd
from scrapegraphai.graphs import SmartScraperGraph
import logging
from datetime import datetime
import json
from json import JSONDecodeError
import os
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def clean_html(url):
    """Remove elementos desnecessários da página usando Playwright"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            
            # Remove elementos que podem interferir no scraping
            page.evaluate("""
                () => {
                    const selectors = [
                        'script', 'style', 'footer', 'nav', 
                        'iframe', 'img', '.ads', '.popup',
                        '.cookie-banner', '.modal'
                    ];
                    selectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => el.remove());
                    });
                }
            """)
            
            cleaned_html = page.content()
            browser.close()
            return cleaned_html
    except Exception as e:
        logger.error(f"Erro ao limpar HTML: {str(e)}")
        return None

def parse_scraper_output(output):
    """Tenta extrair JSON da saída do modelo com tratamento robusto"""
    try:
        if isinstance(output, dict):
            return output
        
        if isinstance(output, str):
            # Tenta encontrar JSON válido na string
            try:
                return json.loads(output)
            except JSONDecodeError:
                # Tenta encontrar o primeiro bloco JSON válido
                start_idx = output.find('{')
                end_idx = output.rfind('}')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = output[start_idx:end_idx+1]
                    return json.loads(json_str)
                
        logger.warning("Formato de saída não reconhecido - tentando reparar")
        # Última tentativa - procura por padrão semelhante a JSON
        if 'imoveis' in output.lower():
            fixed_output = output.replace("'", '"')
            start = fixed_output.find('{')
            end = fixed_output.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(fixed_output[start:end])
        
        raise ValueError("Não foi possível extrair JSON válido")
    except Exception as e:
        logger.error(f"Erro ao parsear saída: {str(e)}")
        raise

def save_to_csv(df, url):
    """Salva os resultados em CSV com nome organizado"""
    try:
        # Cria diretório se não existir
        os.makedirs('resultados_scraping', exist_ok=True)
        
        # Gera nome do arquivo seguro
        domain = urlparse(url).netloc.replace('www.', '').split('.')[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resultados_scraping/{domain}_{timestamp}.csv"
        
        # Garante que os dados estão limpos antes de salvar
        df.replace({'\n': ' ', '\r': ' '}, regex=True, inplace=True)
        
        # Salva com encoding apropriado para Português
        df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';')
        
        logger.info(f"Arquivo CSV gerado: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Falha ao salvar CSV: {str(e)}")
        return None

def run_scraper(url):
    """Executa todo o processo de scraping"""
    try:
        # Configuração do modelo Ollama
        graph_config = {
            "llm": {
                "model": "ollama/llama3:8b-instruct-q4_K_M",
                "temperature": 0,
                "base_url": "http://localhost:11434",
                "options": {
                    "num_ctx": 4096,
                    "num_thread": 8,
                    "format": "json"
                }
            },
            "verbose": False,
            "timeout": 180
        }

        logger.info(f"Iniciando scraping de: {url}")
        
        # Prompt otimizado para sites brasileiros de imóveis
        prompt = """
        ANALISE O HTML E EXTRAIA APENAS UM JSON VÁLIDO com os imóveis listados.
        ESTRUTURA REQUERIDA:
        {
            "imoveis": [{
                "titulo": "string",
                "preco": "string (ex: R$ 1.200.000)",
                "endereco": "string",
                "bairro": "string",
                "cidade": "string",
                "area": "number (m²)",
                "quartos": "number",
                "banheiros": "number",
                "vagas": "number",
                "link": "string (URL completo)",
                "amenidades": ["string"],
                "condominio": "string (valor ou 'Incluso')",
                "tipo": "string (Apartamento, Casa, etc)"
            }]
        }
        Preencha todos os campos possíveis. Para campos não encontrados, use null.
        REMOVA TODOS OS TEXTOS EXTRAS - APENAS O JSON É REQUERIDO.
        """
        
        # Obtém e limpa o HTML
        cleaned_html = clean_html(url)
        if not cleaned_html:
            raise ValueError("Falha ao obter conteúdo da página")
        
        # Executa o scraping
        scraper = SmartScraperGraph(
            prompt=prompt,
            source=cleaned_html,
            config=graph_config
        )
        
        result = scraper.run()
        parsed_data = parse_scraper_output(result)
        
        if not parsed_data or 'imoveis' not in parsed_data:
            raise ValueError("Nenhum dado válido encontrado na página")
        
        # Processa os dados
        df = pd.DataFrame(parsed_data['imoveis'])
        df['site_origem'] = url
        df['data_coleta'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Salva os resultados
        csv_path = save_to_csv(df, url)
        
        if csv_path:
            print(f"\n✅ SCRAPING CONCLUÍDO COM SUCESSO!")
            print(f"📊 {len(df)} imóveis encontrados")
            print(f"💾 Arquivo salvo em: {os.path.abspath(csv_path)}")
        
        return df

    except Exception as e:
        logger.error(f"ERRO NO SCRAPING: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("SCRAPER DE IMÓVEIS - VERSÃO 1.0")
    print("="*50 + "\n")
    
    while True:
        try:
            url = input("Digite a URL do site de imóveis (ou 'sair' para encerrar): ").strip()
            
            if url.lower() in ('sair', 'exit', 'quit'):
                break
                
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            if 'quintoandar' in url or 'zapimoveis' in url or 'vivareal' in url:
                print("\n⚠️ Sites conhecidos podem ter proteção contra scraping!")
                print("Os resultados podem ser limitados.\n")
            
            _ = run_scraper(url)
            
        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ ERRO: {str(e)}")
            continue

    print("\nScraper encerrado. Verifique a pasta 'resultados_scraping' para os arquivos CSV.")