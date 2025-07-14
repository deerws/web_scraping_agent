# Scraper de Imóveis

## Descrição
Este projeto é um script Python para realizar web scraping de sites de imóveis no Brasil, extraindo informações detalhadas sobre imóveis listados e salvando os resultados em arquivos CSV. O script utiliza a biblioteca `ScrapeGraphAI` com um modelo de linguagem local (Ollama) para processar o conteúdo das páginas e extrair dados estruturados.

## Funcionalidades
- **Limpeza de HTML**: Remove elementos desnecessários (como scripts, anúncios e pop-ups) usando Playwright.
- **Extração Estruturada**: Extrai informações como título, preço, endereço, bairro, cidade, área, quartos, banheiros, vagas, link, amenidades, condomínio e tipo do imóvel.
- **Saída em CSV**: Salva os resultados em arquivos CSV organizados por domínio e timestamp.
- **Logging**: Registra o progresso e erros em um arquivo `scraper.log` e no console.
- **Tratamento de Erros**: Inclui tratamento robusto para falhas de parsing e scraping.

## Requisitos
- Python 3.8+
- Bibliotecas Python:
  ```bash
  pip install pandas scrapegraphai playwright
  ```
- Playwright:
  ```bash
  playwright install
  ```
- Servidor Ollama rodando localmente com o modelo `llama3:8b-instruct-q4_K_M`:
  - Instale o Ollama: [Instruções](https://ollama.ai/)
  - Baixe o modelo: `ollama pull llama3:8b-instruct-q4_K_M`

## Como Usar
1. Clone o repositório ou copie o código para um arquivo (ex.: `scraper.py`).
2. Certifique-se de que o servidor Ollama está rodando (`ollama serve`).
3. Execute o script:
   ```bash
   python scraper.py
   ```
4. Digite a URL do site de imóveis (ex.: `https://www.zapimoveis.com.br`) ou `sair` para encerrar.
5. Os resultados serão salvos na pasta `resultados_scraping` como arquivos CSV.

## Estrutura do Projeto
- `scraper.py`: Script principal com as funções de scraping, limpeza de HTML, parsing e salvamento.
- `resultados_scraping/`: Pasta onde os arquivos CSV são salvos.
- `scraper.log`: Arquivo de log gerado com informações e erros do processo.

## Formato da Saída
Os arquivos CSV contêm as seguintes colunas:
- `titulo`: Título do anúncio
- `preco`: Preço do imóvel (ex.: R$ 1.200.000)
- `endereco`: Endereço completo
- `bairro`: Bairro do imóvel
- `cidade`: Cidade do imóvel
- `area`: Área em m²
- `quartos`: Número de quartos
- `banheiros`: Número de banheiros
- `vagas`: Número de vagas de garagem
- `link`: URL do anúncio
- `amenidades`: Lista de amenidades
- `condominio`: Valor do condomínio ou "Incluso"
- `tipo`: Tipo do imóvel (ex.: Apartamento, Casa)
- `site_origem`: URL do site fonte
- `data_coleta`: Data e hora da coleta

## Notas
- Sites como QuintoAndar, Zap Imóveis e Viva Real podem ter proteção contra scraping, o que pode limitar os resultados.
- Certifique-se de que o servidor Ollama está configurado corretamente em `http://localhost:11434`.
- Os arquivos CSV são salvos com encoding `utf-8-sig` e separados por `;` para compatibilidade com sistemas em português.

## Limitações
- Depende da qualidade do HTML da página e da capacidade do modelo de linguagem de interpretar o conteúdo.
- Pode falhar em sites com forte proteção anti-scraping ou JavaScript dinâmico pesado.
- Requer conexão estável com o servidor Ollama.

## Licença
Este projeto é fornecido sob a licença MIT.