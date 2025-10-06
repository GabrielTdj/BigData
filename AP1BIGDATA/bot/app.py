# app.py - Servidor aiohttp que expõe /api/messages (formato Bot Framework)
from aiohttp import web
from bot import gerar_resposta, salvar_historico

routes = web.RouteTableDef()

@routes.post("/api/messages")
async def mensagens(req):
    try:
        data = await req.json()
    except Exception:
        return web.json_response({"type":"message","text":"Payload inválido"}, status=400)
    mensagem = data.get("text") or data.get("mensagem") or ""
    resposta = await gerar_resposta(mensagem)
    # salvamos o histórico (aguardamos para garantir persistência na demo)
    await salvar_historico(mensagem, resposta)
    return web.json_response({ "type": "message", "text": resposta })

app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=3978)
