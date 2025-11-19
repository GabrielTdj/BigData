"""
Flask API - Flight & Hotel Chatbot
Integrado com Azure CLU, Text Analytics, Cosmos DB e Amadeus
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import bot
import os
import sys

# Detectar diretório do frontend automaticamente
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(current_dir, '..', '..', 'frontend', 'webchat')

# Se não existir, tentar caminho alternativo (Azure deploy)
if not os.path.exists(frontend_path):
    frontend_path = os.path.join(os.path.dirname(current_dir), 'frontend', 'webchat')

if not os.path.exists(frontend_path):
    frontend_path = os.path.join(current_dir, 'frontend', 'webchat')

print(f"[STARTUP] Frontend path: {frontend_path}", flush=True)
print(f"[STARTUP] Frontend exists: {os.path.exists(frontend_path)}", flush=True)
if os.path.exists(frontend_path):
    print(f"[STARTUP] Files: {os.listdir(frontend_path)}", flush=True)

app = Flask(__name__, static_folder=frontend_path, static_url_path='')
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
    """Serve frontend HTML"""
    try:
        if not os.path.exists(app.static_folder):
            return jsonify({
                'error': 'Frontend não encontrado',
                'static_folder': app.static_folder,
                'current_dir': os.getcwd(),
                'files_in_root': os.listdir('.')[:20]
            }), 404
        
        index_path = os.path.join(app.static_folder, 'index.html')
        if not os.path.exists(index_path):
            return jsonify({
                'error': 'index.html não encontrado',
                'static_folder': app.static_folder,
                'files_in_static': os.listdir(app.static_folder)
            }), 404
            
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        return jsonify({'error': str(e), 'static_folder': app.static_folder}), 500

@app.route('/api', methods=['GET'])
def api_info():
    """API info endpoint"""
    return jsonify({
        'service': 'Flight & Hotel Chatbot API',
        'version': '1.0',
        'status': 'running',
        'endpoints': {
            'GET /': 'Interface do chatbot',
            'GET /api': 'Informações da API',
            'POST /api/chat': 'Enviar mensagem ao chatbot',
            'GET /health': 'Status do serviço'
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    print(f"[STARTUP] Flask rodando na porta {port}", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
