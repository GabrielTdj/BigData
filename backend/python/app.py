"""
Flask API - Flight & Hotel Chatbot
Integrado com Azure CLU, Text Analytics, Cosmos DB e Amadeus
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import bot
import os
import sys

app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal do chatbot"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'response': 'Mensagem inválida. Envie {"userId": "id", "message": "texto"}', 'error': True}), 400
        
        user_id = data.get('userId', 'anonymous')
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'response': 'Mensagem vazia', 'error': True}), 400
        
        print(f"[INFO] User {user_id}: {message[:50]}...", flush=True)
        
        resp = bot.rest_handle(data)
        return jsonify(resp)
        
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] {error_msg}", flush=True)
        return jsonify({'response': f'Erro: {error_msg[:100]}', 'error': True}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'flight-hotel-chatbot', 'version': '1.0'})

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'service': 'Flight & Hotel Chatbot API',
        'version': '1.0',
        'status': 'running',
        'endpoints': {
            'POST /api/chat': 'Enviar mensagem ao chatbot',
            'GET /health': 'Status do serviço',
            'GET /': 'Informações da API'
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    print(f"[STARTUP] Flask rodando na porta {port}", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
