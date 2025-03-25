# Web Scraper

This project aims to collect apartment data from a sales website and store it in a SQLite database, later transferring it to a MySQL database. Additionally, the system automatically detects and removes duplicates.

## Technologies Used

- **Python** (Main language)
- **Selenium** (Web navigation automation)
- **BeautifulSoup** (HTML data extraction)
- **Pandas** (Data manipulation)
- **SQLAlchemy** (Database interface)
- **MySQL** and **SQLite** (Data storage)

## Project Structure

```
├── import_request.py        # Collects data from the website and stores it in SQLite
├── eliminar_duplicatas.py   # Removes duplicate records from the database
├── inserir_dados_mysql.py   # Transfers data from SQLite to MySQL
├── script_principal.py      # Executes all scripts in the correct order
├── apartamentos.db          # Generated SQLite database
└── README.md                # Project documentation
```

## Installation and Configuration

### 1. Clone the Repository

```sh
git clone https://github.com/deerws/web_scraping.git
cd web_scraping
```

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

### 3. Configure the MySQL Database

Before running the script, configure your MySQL database. In the **inserir\_dados\_mysql.py** file, edit the following credentials:

```python
host = 'localhost'
user = 'root'
password = 'YOUR_PASSWORD'
database = 'apartamentos_db'
```

### 4. Running the Script

To run the entire data collection and storage pipeline, execute:

```sh
python script_principal.py
```

## Script Functionality

### 1. **import\_request.py**

- Uses **Selenium** to access the Zap Imóveis website
- Extracts information such as price, area, number of rooms, and address
- Stores the data in a SQLite database

### 2. **eliminar\_duplicatas.py**

- Detects and removes duplicate records in SQLite
- Updates the database with unique data

### 3. **inserir\_dados\_mysql.py**

- Connects to the MySQL database
- Transfers data from SQLite to MySQL

### 4. **script\_principal.py**

- Automates the execution of the three scripts above in sequence

## Notes

- Ensure that **Google Chrome** is installed, as **Selenium** will use ChromeDriver.
- You may need to update the WebDriver using the command:

```sh
pip install --upgrade webdriver-manager
```

## Author

Project developed by **André Pinheiro Paes**. Feel free to contribute or report any issues!

## License

This project is licensed under the MIT License.

