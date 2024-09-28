from flask import Flask, request, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех маршрутов

# Указываем путь к драйверу Chrome
chrome_service = Service('C:/chromedriver-win64/chromedriver.exe')  # Замените на путь к вашему chromedriver

chrome_options = Options()
chrome_options.add_argument('--headless')  # Если хотите видеть браузер, уберите эту строку

# Инициализация драйвера
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

@app.route('/')
def index():
    return render_template('index.html')  # Отправляем index.html, когда запрашивается корень

@app.route('/search', methods=['POST'])
def search_google():
    try:
        data = request.get_json()
        print(f"Полученные данные: {data}")
        keywords = data.get('q', '')  # Получаем ключевые слова из запроса

        if not keywords:
            return jsonify({"error": "Пожалуйста, введите ключевые слова"}), 400

        query = "+".join(keywords.split())
        url = f"https://www.google.com/search?q={query}&num=10"
        
        driver.get(url)
        time.sleep(3)  # Даем время странице загрузиться

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        results = []

        # Извлечение результатов поиска
        for item in soup.find_all('div', class_='MjjYud'):
            title = item.find('h3')
            link = item.find('a')
            snippet = item.find('span')

            # Проверяем, существует ли элемент перед доступом к его атрибутам
            if title and link and snippet:
                result_link = link.get('href')  # Используем get для безопасного получения атрибута
                if result_link:  # Дополнительная проверка
                    formatted_snippet = snippet.text.replace('https', ' https')
                    results.append({
                        "title": title.text,
                        "url": result_link,
                        "snippet": formatted_snippet
                    })
        print(results)
        return jsonify(results) if results else jsonify({"message": "Нет результатов"}), 200

    except Exception as e:
        print(f"Произошла ошибка: {e}")  # Логируем ошибку
        return jsonify({"error": str(e)}), 500 

if __name__ == "__main__":
    app.run(debug=True)
