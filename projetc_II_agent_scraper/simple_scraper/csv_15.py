import requests
import json
import pandas as pd
from datetime import datetime
import os
import logging
from urllib.parse import urlparse, urljoin
import time
import random
from typing import List, Dict, Optional
import re

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jina_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JinaAIRealEstateScraper:
    """
    Scraper de imóveis usando Jina AI Reader API
    - Gratuito e sem necessidade de API key
    - Converte qualquer URL em texto limpo para LLM
    - Rate limit: 20 req/min sem API key, 200 req/min com API key gratuita
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://r.jina.ai/"
        self.api_key = api_key
        self.session = requests.Session()
        
        # Headers para requisições
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/plain, application/json',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8'
        }
        
        # Adiciona API key se fornecida (para rate limit maior)
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            logger.info("✅ API key configurada - Rate limit: 200 req/min")
        else:
            logger.info("⚠️ Sem API key - Rate limit: 20 req/min")
        
        self.session.headers.update(headers)
        
        # Configurações de rate limiting
        self.requests_per_minute = 200 if self.api_key else 20
        self.min_delay = 60 / self.requests_per_minute  # segundos entre requisições
        self.last_request_time = 0

    def respect_rate_limit(self):
        """Implementa rate limiting para não exceder os limites da API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            logger.info(f"⏳ Aguardando {sleep_time:.1f}s para respeitar rate limit...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def extract_clean_content(self, url: str) -> Optional[str]:
        """
        Extrai conteúdo limpo de uma URL usando Jina AI Reader
        
        Args:
            url: URL para extrair conteúdo
            
        Returns:
            Texto limpo da página ou None se erro
        """
        try:
            self.respect_rate_limit()
            
            # URL da Jina AI Reader
            jina_url = f"{self.base_url}{url}"
            
            logger.info(f"📖 Extraindo conteúdo de: {url}")
            
            # Faz requisição para Jina AI
            response = self.session.get(jina_url, timeout=30)
            response.raise_for_status()
            
            # O conteúdo vem como texto limpo
            clean_content = response.text
            
            if len(clean_content) > 100:  # Verifica se tem conteúdo substancial
                logger.info(f"✅ Conteúdo extraído: {len(clean_content)} caracteres")
                return clean_content
            else:
                logger.warning(f"⚠️ Conteúdo muito pequeno: {len(clean_content)} caracteres")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro ao extrair conteúdo de {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {str(e)}")
            return None

    def extract_property_data_with_llm(self, clean_content: str, url: str) -> List[Dict]:
        """
        Extrai dados de imóveis do conteúdo limpo usando LLM local (Ollama)
        
        Args:
            clean_content: Conteúdo limpo da página
            url: URL original
            
        Returns:
            Lista de dicionários com dados dos imóveis
        """
        try:
            # Prompt otimizado para extração de imóveis
            prompt = f"""
            Analise o seguinte conteúdo de uma página de imóveis e extraia TODOS os imóveis encontrados.
            Retorne APENAS um JSON válido seguindo esta estrutura EXATA:

            {{
                "imoveis": [
                    {{
                        "titulo": "título do imóvel",
                        "preco": "preço (ex: R$ 850.000)",
                        "endereco": "endereço completo (SEM bairro e cidade)",
                        "bairro": "bairro (extrair do endereço se necessário)", 
                        "cidade": "cidade (extrair do endereço se necessário)",
                        "area_m2": "área em m² (apenas número)",
                        "quartos": "número de quartos (apenas número)",
                        "banheiros": "número de banheiros (apenas número)",
                        "vagas": "número de vagas (apenas número)",
                        "tipo": "tipo do imóvel",
                        "condominio": "valor do condomínio",
                        "caracteristicas": ["lista de características"],
                        "link": "URL do imóvel se encontrada"
                    }}
                ]
            }}

            REGRAS IMPORTANTES:
            - Extraia TODOS os imóveis da página
            - Para campos não encontrados, use null
            - Para números, use apenas o valor numérico
            - URLs devem ser completas
            - NUNCA inclua texto explicativo, apenas o JSON
            - Endereço NÃO deve conter bairro e cidade (devem ir em campos separados)
            - Se bairro/cidade estiverem no endereço, extraia para os campos corretos

            CONTEÚDO DA PÁGINA:
            {clean_content[:8000]}  # Limita para não exceder contexto
            """

            # Faz requisição para Ollama local
            ollama_url = "http://localhost:11434/api/generate"
            payload = {
                "model": "llama3:8b-instruct-q4_K_M",
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_ctx": 8192
                }
            }

            logger.info("🤖 Processando com Ollama...")
            response = requests.post(ollama_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get('response', '')
                
                # Parseia o JSON retornado
                try:
                    properties_data = json.loads(llm_response)
                    properties = properties_data.get('imoveis', [])
                    
                    # Pós-processamento para garantir separação de endereço/bairro/cidade
                    for prop in properties:
                        self.clean_address_fields(prop)
                    
                    logger.info(f"✅ {len(properties)} imóveis extraídos pelo LLM")
                    return properties
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Erro ao parsear JSON do LLM: {str(e)}")
                    # Tenta extrair JSON válido da resposta
                    return self.extract_json_from_text(llm_response)
            else:
                logger.error(f"❌ Erro no Ollama: {response.status_code}")
                return []

        except requests.exceptions.ConnectionError:
            logger.error("❌ Ollama não está rodando. Execute: ollama serve")
            return []
        except Exception as e:
            logger.error(f"❌ Erro no processamento LLM: {str(e)}")
            return []

    def clean_address_fields(self, property_data: Dict):
        """Garante que endereço, bairro e cidade estejam corretamente separados"""
        if 'endereco' in property_data and property_data['endereco']:
            address = property_data['endereco']
            
            # Se bairro está vazio mas pode estar no endereço
            if not property_data.get('bairro') and ',' in address:
                parts = [p.strip() for p in address.split(',')]
                if len(parts) > 1:
                    property_data['bairro'] = parts[-1]
                    property_data['endereco'] = ','.join(parts[:-1])
            
            # Se cidade está vazia mas pode estar no endereço
            if not property_data.get('cidade') and '-' in address:
                parts = [p.strip() for p in address.split('-')]
                if len(parts) > 1:
                    property_data['cidade'] = parts[-1]
                    property_data['endereco'] = '-'.join(parts[:-1])

    def extract_json_from_text(self, text: str) -> List[Dict]:
        """Tenta extrair JSON válido de um texto que pode conter outros elementos"""
        try:
            # Procura por padrão JSON
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx+1]
                data = json.loads(json_str)
                properties = data.get('imoveis', [])
                
                # Aplica limpeza de campos de endereço
                for prop in properties:
                    self.clean_address_fields(prop)
                
                return properties
        except:
            pass
        
        return []

    def extract_properties_simple(self, clean_content: str, url: str) -> List[Dict]:
        """
        Extração simples usando regex (fallback se Ollama não estiver disponível)
        """
        properties = []
        
        try:
            # Padrões regex para detectar informações de imóveis
            price_pattern = r'R\$\s*[\d.,]+(?:\s*mil)?'
            room_pattern = r'(\d+)\s*(?:quarto|dormitório|bedroom)'
            bath_pattern = r'(\d+)\s*(?:banheiro|bathroom|wc)'
            area_pattern = r'(\d+(?:[.,]\d+)?)\s*m[²2]'
            
            # Divide o conteúdo em seções (assumindo que cada imóvel é uma seção)
            sections = re.split(r'\n\s*\n', clean_content)
            
            for i, section in enumerate(sections):
                if len(section) < 50:  # Pula seções muito pequenas
                    continue
                    
                # Busca por preços na seção
                prices = re.findall(price_pattern, section, re.IGNORECASE)
                if not prices:
                    continue
                
                # Extrai informações básicas
                property_data = {
                    'titulo': self.extract_title_from_section(section),
                    'preco': prices[0] if prices else None,
                    'endereco': None,
                    'bairro': None,
                    'cidade': None,
                    'area_m2': None,
                    'quartos': None,
                    'banheiros': None,
                    'vagas': None,
                    'tipo': None,
                    'condominio': None,
                    'caracteristicas': [],
                    'link': url
                }
                
                # Extrai endereço, bairro e cidade
                address_info = self.extract_address_from_section(section)
                if address_info:
                    property_data['endereco'] = address_info.get('endereco')
                    property_data['bairro'] = address_info.get('bairro')
                    property_data['cidade'] = address_info.get('cidade')
                
                # Extrai quartos
                rooms = re.findall(room_pattern, section, re.IGNORECASE)
                if rooms:
                    property_data['quartos'] = int(rooms[0])
                
                # Extrai banheiros
                baths = re.findall(bath_pattern, section, re.IGNORECASE)
                if baths:
                    property_data['banheiros'] = int(baths[0])
                
                # Extrai área
                areas = re.findall(area_pattern, section, re.IGNORECASE)
                if areas:
                    property_data['area_m2'] = float(areas[0].replace(',', '.'))
                
                properties.append(property_data)
                
                # Limita a 20 imóveis para não sobrecarregar
                if len(properties) >= 20:
                    break
            
            logger.info(f"✅ {len(properties)} imóveis extraídos com regex")
            return properties
            
        except Exception as e:
            logger.error(f"❌ Erro na extração simples: {str(e)}")
            return []

    def extract_title_from_section(self, section: str) -> str:
        """Extrai título provável de uma seção"""
        lines = section.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 100:
                # Verifica se parece com um título
                if any(word in line.lower() for word in ['apartamento', 'casa', 'imóvel', 'venda', 'aluguel']):
                    return line
        
        # Se não encontrar, usa a primeira linha não vazia
        for line in lines:
            line = line.strip()
            if len(line) > 5:
                return line[:80]
        
        return "Título não identificado"

    def extract_address_from_section(self, section: str) -> Optional[Dict]:
        """Extrai endereço, bairro e cidade de uma seção"""
        # Padrões comuns de endereço
        address_pattern = r'(?:Rua|Av|Avenida|Alameda|Travessa|Praça)\s+[^,]+(?:,\s*\d+)?(?:,\s*[^-]+)?(?:-\s*[^,]+)?(?:,\s*[^-]+)?'
        matches = re.findall(address_pattern, section, re.IGNORECASE)
        
        if not matches:
            return None
            
        full_address = matches[0].strip()
        result = {'endereco': full_address, 'bairro': None, 'cidade': None}
        
        # Tenta extrair bairro e cidade
        parts = [p.strip() for p in full_address.split(',')]
        if len(parts) > 1:
            result['bairro'] = parts[-1]
            result['endereco'] = ','.join(parts[:-1])
            
            # Verifica se tem cidade após hífen
            if '-' in result['bairro']:
                city_parts = result['bairro'].split('-')
                if len(city_parts) > 1:
                    result['cidade'] = city_parts[-1].strip()
                    result['bairro'] = city_parts[0].strip()
        
        return result

    def process_url(self, url: str, use_llm: bool = True) -> List[Dict]:
        """
        Processa uma URL completa: extrai conteúdo + processa com LLM
        
        Args:
            url: URL para processar
            use_llm: Se deve usar LLM (Ollama) para processamento
            
        Returns:
            Lista de imóveis extraídos
        """
        logger.info(f"🏠 Processando URL: {url}")
        
        # 1. Extrai conteúdo limpo com Jina AI
        clean_content = self.extract_clean_content(url)
        if not clean_content:
            logger.error("❌ Não foi possível extrair conteúdo da URL")
            return []
        
        # 2. Processa conteúdo com LLM ou regex
        if use_llm:
            properties = self.extract_property_data_with_llm(clean_content, url)
            
            # Se LLM falhar, usa método simples
            if not properties:
                logger.info("🔄 LLM falhou, tentando extração simples...")
                properties = self.extract_properties_simple(clean_content, url)
        else:
            properties = self.extract_properties_simple(clean_content, url)
        
        # 3. Adiciona metadados
        for prop in properties:
            prop['site_origem'] = urlparse(url).netloc
            prop['data_coleta'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prop['url_origem'] = url
        
        return properties

    def process_multiple_urls(self, urls: List[str], use_llm: bool = True) -> List[Dict]:
        """
        Processa múltiplas URLs
        
        Args:
            urls: Lista de URLs para processar
            use_llm: Se deve usar LLM
            
        Returns:
            Lista combinada de todos os imóveis
        """
        all_properties = []
        
        logger.info(f"🔄 Processando {len(urls)} URLs...")
        
        for i, url in enumerate(urls, 1):
            logger.info(f"📍 URL {i}/{len(urls)}: {url}")
            
            properties = self.process_url(url, use_llm)
            all_properties.extend(properties)
            
            logger.info(f"✅ {len(properties)} imóveis encontrados nesta URL")
            
            # Pausa entre URLs para ser respeitoso
            if i < len(urls):
                time.sleep(random.uniform(1, 3))
        
        logger.info(f"🎉 Total: {len(all_properties)} imóveis de todas as URLs")
        return all_properties

    def save_to_csv(self, properties: List[Dict], filename: Optional[str] = None) -> str:
        """
        Salva imóveis em arquivo CSV
        
        Args:
            properties: Lista de imóveis
            filename: Nome do arquivo (opcional)
            
        Returns:
            Path do arquivo salvo
        """
        if not properties:
            logger.warning("⚠️ Nenhum imóvel para salvar")
            return ""
        
        try:
            # Cria DataFrame
            df = pd.DataFrame(properties)
            
            # Remove duplicatas baseado em título + preço
            initial_count = len(df)
            df = df.drop_duplicates(subset=['titulo', 'preco'], keep='first')
            final_count = len(df)
            
            if initial_count > final_count:
                logger.info(f"🔄 Removidas {initial_count - final_count} duplicatas")
            
            # Reorganiza colunas (removendo descrição)
            priority_cols = ['titulo', 'preco', 'endereco', 'bairro', 'cidade', 
                           'area_m2', 'quartos', 'banheiros', 'vagas', 'tipo', 'condominio']
            
            existing_priority = [col for col in priority_cols if col in df.columns]
            other_cols = [col for col in df.columns if col not in existing_priority and col != 'descricao']
            df = df[existing_priority + other_cols]
            
            # Cria diretório
            os.makedirs('resultados_jina', exist_ok=True)
            
            # Nome do arquivo
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"resultados_jina/imoveis_jina_{timestamp}.csv"
            
            # Salva CSV
            df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';')
            
            logger.info(f"💾 CSV salvo: {filename} ({len(df)} imóveis)")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar CSV: {str(e)}")
            return ""

    def get_sample_urls(self) -> List[str]:
        """Retorna URLs de exemplo para teste"""
        return [
            "https://www.chavesnamao.com.br/apartamentos-venda-sao-paulo-sp",
            "https://www.123i.com.br/apartamento-venda-sao-paulo-sp",
            "https://casa.com.br/venda/sp/sao-paulo/apartamento",
            "https://www.wimoveis.com.br/apartamentos-venda-sao-paulo-sp.html",
            "https://www.imovelweb.com.br/apartamentos-venda-sao-paulo-sp.html"
        ]

def main():
    """Função principal"""
    print("\n" + "="*70)
    print("🏠 SCRAPER DE IMÓVEIS COM JINA AI - v1.1")
    print("   Powered by Jina AI Reader API (Gratuito!)")
    print("="*70)
    
    # Pergunta sobre API key
    print("\n🔑 API KEY DA JINA AI (OPCIONAL)")
    print("   • Sem API key: 20 requisições/min (gratuito)")
    print("   • Com API key gratuita: 200 requisições/min")
    print("   • Para obter API key: https://jina.ai/reader/")
    
    api_key = input("\nDigite sua API key da Jina AI (ou Enter para pular): ").strip()
    api_key = api_key if api_key else None
    
    # Inicializa scraper
    scraper = JinaAIRealEstateScraper(api_key=api_key)
    
    # Pergunta sobre LLM
    print("\n🤖 PROCESSAMENTO DE DADOS")
    print("1. 🧠 Com Ollama (melhor qualidade - requer ollama local)")
    print("2. 📝 Regex simples (funciona sem dependências)")
    
    llm_choice = input("\nEscolha (1 ou 2): ").strip()
    use_llm = llm_choice == "1"
    
    if use_llm:
        print("\n⚠️  CERTIFIQUE-SE QUE O OLLAMA ESTÁ RODANDO:")
        print("   ollama serve")
        print("   ollama pull llama3:8b-instruct-q4_K_M")
    
    # URLs de exemplo
    sample_urls = scraper.get_sample_urls()
    print(f"\n💡 URLS DE EXEMPLO:")
    for i, url in enumerate(sample_urls, 1):
        print(f"   {i}. {url}")
    
    print(f"\n💡 DICA: Use URLs específicas de busca para melhores resultados!")
    
    while True:
        try:
            print(f"\n" + "="*50)
            urls_input = input("Digite URL(s) separadas por vírgula (ou 'sair'): ").strip()
            
            if urls_input.lower() in ('sair', 'exit', 'quit', 's'):
                print("👋 Encerrando scraper...")
                break
            
            if not urls_input:
                continue
            
            # Processa URLs
            urls = [url.strip() for url in urls_input.split(',') if url.strip()]
            
            # Valida URLs
            valid_urls = []
            for url in urls:
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                try:
                    parsed = urlparse(url)
                    if parsed.netloc:
                        valid_urls.append(url)
                    else:
                        print(f"❌ URL inválida: {url}")
                except:
                    print(f"❌ URL inválida: {url}")
            
            if not valid_urls:
                print("❌ Nenhuma URL válida fornecida")
                continue
            
            print(f"\n🚀 Iniciando scraping de {len(valid_urls)} URL(s)...")
            print(f"🔧 Método: {'Jina AI + Ollama' if use_llm else 'Jina AI + Regex'}")
            
            # Processa URLs
            all_properties = scraper.process_multiple_urls(valid_urls, use_llm)
            
            if all_properties:
                # Salva CSV
                csv_file = scraper.save_to_csv(all_properties)
                
                # Relatório final
                print(f"\n{'='*60}")
                print(f"🎉 SCRAPING CONCLUÍDO!")
                print(f"{'='*60}")
                print(f"📊 Total de imóveis: {len(all_properties)}")
                print(f"🌐 URLs processadas: {len(valid_urls)}")
                if csv_file:
                    print(f"💾 Arquivo CSV: {os.path.abspath(csv_file)}")
                
                # Preview dos dados
                if all_properties:
                    print(f"\n📋 PREVIEW DOS DADOS:")
                    print(f"{'─'*40}")
                    
                    for i, prop in enumerate(all_properties[:3], 1):
                        print(f"🏠 Imóvel {i}:")
                        if prop.get('titulo'):
                            print(f"   Título: {prop['titulo'][:60]}...")
                        if prop.get('preco'):
                            print(f"   Preço: {prop['preco']}")
                        if prop.get('endereco'):
                            print(f"   Endereço: {prop['endereco']}")
                        if prop.get('bairro'):
                            print(f"   Bairro: {prop['bairro']}")
                        if prop.get('cidade'):
                            print(f"   Cidade: {prop['cidade']}")
                        print()
                
                print(f"🕒 Concluído em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                print(f"{'='*60}")
                
            else:
                print("⚠️  Nenhum imóvel foi extraído.")
                print("   Possíveis causas:")
                print("   • URL não contém listagem de imóveis")
                print("   • Site tem proteção anti-scraping")
                print("   • Conteúdo não foi reconhecido como imóveis")
                
        except KeyboardInterrupt:
            print("\n\n⛔ Operação cancelada pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ ERRO INESPERADO: {str(e)}")
            logger.error(f"Erro não tratado: {str(e)}")
            continue
    
    print(f"\n🏁 Scraper encerrado.")
    print(f"📁 Verifique a pasta 'resultados_jina' para os arquivos CSV.")
    print(f"\n📋 SOBRE A JINA AI:")
    print(f"   ✅ Completamente gratuita (até 20 req/min)")
    print(f"   🧹 Extrai apenas conteúdo relevante")
    print(f"   🚀 Funciona com qualquer site")
    print(f"   📊 Ideal para alimentar LLMs")

if __name__ == "__main__":
    main()
