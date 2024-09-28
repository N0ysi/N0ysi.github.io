from flask import Flask, request, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)  # Povolit CORS pro všechny trasy

# Určete cestu k ovladači Chrome
chrome_service = Service('C:/chromedriver-win64/chromedriver.exe')  # Nahraďte cestou k vašemu chromedriveru

chrome_options = Options()
chrome_options.add_argument('--headless')   # Pokud chcete vidět prohlížeč, odstraňte tento řádek

# Inicializace ovladače
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

@app.route('/')
def index():
    return render_template('index.html')  # Zasíláme index.html, když je požadován kořenový adresář

@app.route('/search', methods=['POST'])
def search_google():
    try:
        data = request.get_json()
        print(f"Získaná data: {data}")
        keywords = data.get('q', '')  ## Získání klíčových slov z požadavku

        if not keywords:
            return jsonify({"error": "Zadejte prosím klíčová slova"}), 400

        query = "+".join(keywords.split())
        url = f"https://www.google.com/search?q={query}&num=10"
        
        driver.get(url)
        time.sleep(3)  # # Dáme stránce čas na načtení

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        results = []

        # Extrakce výsledků vyhledávání
        for item in soup.find_all('div', class_='MjjYud'):
            title = item.find('h3')
            link = item.find('a')
            snippet = item.find('span')

            # Zkontrolujeme, zda element existuje před přístupem k jeho atributům
            if title and link and snippet:
                result_link = link.get('href')  # Používáme get pro bezpečné získání atributu
                if result_link:  # Další kontrola
                    formatted_snippet = snippet.text.replace('https', ' https')
                    results.append({
                        "title": title.text,
                        "url": result_link,
                        "snippet": formatted_snippet
                    })
        print(results)
        return jsonify(results) if results else jsonify({"message": "Žádné výsledky"}), 200

    except Exception as e:
        print(f"Došlo k chybě: {e}")  # Logujeme chybu
        return jsonify({"error": str(e)}), 500 

if __name__ == "__main__":
    app.run(debug=True)
