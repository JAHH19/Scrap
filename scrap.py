#!/usr/bin/env python
import os
import re
import requests
import chardet
from flask import Flask, request, jsonify

app = Flask(__name__)

PREFIX = 'https:/'

def get_html_content(url: str) -> str:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'deflate',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Connection': 'keep-alive',
            'Referer': url  # Agrega el encabezado Referer con la URL de origen
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP
        
        # Detectar la codificación del contenido
        encoding = chardet.detect(response.content)['encoding']
        if not encoding:
            encoding = 'utf-8'  # Si no se detecta, asumir UTF-8
        
        # Decodificar el contenido usando la codificación detectada
        html = response.content.decode(encoding, errors='ignore')
        print(html)
        return html
    
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error retrieving data from URL: {str(e)}")
    
    except Exception as e:
        raise ValueError(f"Error processing HTML response: {str(e)}")

def get_curl_command(url: str) -> str:
    try:
        html = get_html_content(url)
        
        token_match = re.search(r".*document.getElementById.*\('norobotlink'\).innerHTML =.*?token=(.*?)'.*?;", html, re.M|re.S)
        if not token_match:
            raise ValueError("Token not found in HTML response")
        token = token_match.group(1)
        
        infix_match = re.search(r'.*<div id="ideoooolink" style="display:none;">(.*?token=).*?<[/]div>', html, re.M|re.S)
        if not infix_match:
            raise ValueError("Infix not found in HTML response")
        infix = infix_match.group(1)
        
        final_URL = f'{PREFIX}{infix}{token}'
        
        title_match = re.search(r'.*<meta name="og:title" content="(.*?)">', html, re.M|re.S)
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
