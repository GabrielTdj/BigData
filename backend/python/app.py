"""
Flask API - Flight & Hotel Chatbot
Integrado com Azure CLU, Text Analytics, Cosmos DB e Amadeus
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import bot
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint principal do chatbot
    Body: {"userId": "string", "message": "string"}
    Response: {"response": "string"}
    """
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'response': 'Mensagem inválida', 'error': True}), 400
        
        resp = bot.rest_handle(data)
        return jsonify(resp)
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({'response': 'Erro interno do servidor', 'error': True}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'flight-hotel-chatbot'})

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'service': 'Flight & Hotel Chatbot API',
        'version': '1.0',
        'endpoints': {
            '/api/chat': 'POST - Enviar mensagem ao chatbot',
            '/health': 'GET - Status do serviço'
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
