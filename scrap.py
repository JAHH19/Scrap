from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/generate-curl', methods=['GET'])
def generate_curl():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL missing in request'}), 400

    # Aquí colocas tu lógica para generar el comando curl

    curl_command = f'curl -L -o \'filename\' \'{url}\''
    
    # Devuelve el resultado en formato JSON
    return jsonify({'curl_command': curl_command})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
