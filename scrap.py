#!/usr/bin/env python
import os
import re
import requests
import chardet
from flask import Flask, request, jsonify

app = Flask(__name__)

PREFIX = 'https:/'

def get_curl_command(url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Connection': 'keep-alive',
    }
    session = requests.Session()
    response = session.get(url, headers=headers)
    
    # Detect and handle encoding using chardet
    result = chardet.detect(response.content)
    encoding = result['encoding'] or 'utf-8'
    html = response.content.decode(encoding, errors='ignore')
    
    try:
        token = re.search(r".*document.getElementById.*\('norobotlink'\).innerHTML =.*?token=(.*?)'.*?;", html, re.M|re.S).group(1)
        infix = re.search(r'.*<div id="ideoooolink" style="display:none;">(.*?token=).*?<[/]div>', html, re.M|re.S).group(1)
        final_URL = f'{PREFIX}{infix}{token}'
        orig_title = re.search(r'.*<meta name="og:title" content="(.*?)">', html, re.M|re.S).group(1)
        return f"curl -L -o '{orig_title}' '{final_URL}'"
    except AttributeError:
        raise ValueError("Unable to extract required information from the HTML response")

@app.route('/generate-curl', methods=['GET'])
def generate_curl():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL missing in request'}), 400

    try:
        curl_command = get_curl_command(url)
        return jsonify({'curl_command': curl_command})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
