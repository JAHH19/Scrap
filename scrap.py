import os
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from flask import Flask, request, jsonify
import chromedriver_autoinstaller

app = Flask(__name__)

PREFIX = 'https:/'

chromedriver_path = chromedriver_autoinstaller.install()

def get_curl_command(url: str) -> str:
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('start-maximized')
        options.add_argument('disable-infobars')
        options.add_argument('--disable-extensions')

        service = Service()

        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        # Esperar hasta que el contenido esté completamente cargado
        time.sleep(5)

        html = driver.page_source

        # Cerrar el navegador
        driver.quit()

        # Procesar el HTML y extraer el contenido necesario
        token_match = re.search(r".*document.getElementById.*\('norobotlink'\).innerHTML =.*?token=(.*?)'.*?;", html, re.M | re.S)
        if not token_match:
            raise ValueError("Token not found in HTML response")
        token = token_match.group(1)

        infix_match = re.search(r'.*<div id="ideoooolink" style="display:none;">(.*?token=).*?<[/]div>', html, re.M | re.S)
        if not infix_match:
            raise ValueError("Infix not found in HTML response")
        infix = infix_match.group(1)

        final_URL = f'{PREFIX}{infix}{token}'

        title_match = re.search(r'.*<meta name="og:title" content="(.*?)">', html, re.M | re.S)
        if not title_match:
            raise ValueError("Original title not found in HTML response")
        orig_title = title_match.group(1)

        return f"curl -L -o '{orig_title}' '{final_URL}'"

    except ValueError as ve:
        raise ve

    except Exception as e:
        raise ValueError(f"Error processing HTML response: {str(e)}")

@app.route('/generate-curl', methods=['GET'])
def generate_curl():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL missing in request'}), 400

    try:
        curl_command = get_curl_command(url)
        return jsonify({'curl_command': curl_command})

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
