# Simple Web Scraper

## Description
This project is a Python script for web scraping real estate websites in Brazil, extracting detailed information about listed properties and saving the results in CSV files. The script uses the `ScrapeGraphAI` library with a local language model (Ollama) to process page content and extract structured data.

## Features
- **HTML Cleaning**: Removes unnecessary elements (e.g., scripts, ads, pop-ups) using Playwright.
- **Structured Extraction**: Extracts details such as title, price, address, neighborhood, city, area, bedrooms, bathrooms, parking spaces, link, amenities, condominium fees, and property type.
- **CSV Output**: Saves results in CSV files organized by domain and timestamp.
- **Logging**: Logs progress and errors to a `scraper.log` file and the console.
- **Error Handling**: Includes robust handling for parsing and scraping failures.

## Requirements
- Python 3.8+
- Python libraries:
  ```bash
  pip install pandas scrapegraphai playwright
  ```
- Playwright:
  ```bash
  playwright install
  ```
- Ollama server running locally with the `llama3:8b-instruct-q4_K_M` model:
  - Install Ollama: [Instructions](https://ollama.ai/)
  - Pull the model: `ollama pull llama3:8b-instruct-q4_K_M`

## How to Use
1. Clone the repository or copy the code to a file (e.g., `scraper.py`).
2. Ensure the Ollama server is running (`ollama serve`).
3. Run the script:
   ```bash
   python scraper.py
   ```
4. Enter the URL of the real estate website (e.g., `https://www.zapimoveis.com.br`) or `sair` to exit.
5. Results will be saved in the `resultados_scraping` folder as CSV files.

## Project Structure
- `scraper.py`: Main script with functions for scraping, HTML cleaning, parsing, and saving.
- `resultados_scraping/`: Folder where CSV files are saved.
- `scraper.log`: Log file with process information and errors.

## Output Format
The CSV files contain the following columns:
- `titulo`: Listing title
- `preco`: Property price (e.g., R$ 1,200,000)
- `endereco`: Full address
- `bairro`: Neighborhood
- `cidade`: City
- `area`: Area in m²
- `quartos`: Number of bedrooms
- `banheiros`: Number of bathrooms
- `vagas`: Number of parking spaces
- `link`: Listing URL
- `amenidades`: List of amenities
- `condominio`: Condominium fee or "Incluso" (Included)
- `tipo`: Property type (e.g., Apartment, House)
- `site_origem`: Source website URL
- `data_coleta`: Data collection date and time

## Notes
- Websites like QuintoAndar, Zap Imóveis, and Viva Real may have anti-scraping protections, which could limit results.
- Ensure the Ollama server is properly configured at `http://localhost:11434`.
- CSV files are saved with `utf-8-sig` encoding and `;` as the separator for compatibility with Portuguese systems.

## Limitations
- Depends on the quality of the page's HTML and the language model's ability to interpret content.
- May fail on websites with strong anti-scraping measures or heavy dynamic JavaScript.
- Requires a stable connection to the Ollama server.

## License
This project is licensed under the MIT License.
