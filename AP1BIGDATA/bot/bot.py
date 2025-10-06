# bot.py - Lógica do chatbot (em português)
import aiohttp
import asyncio

URL_API = "http://api:8080/api/conversas"  # serviço 'api' no docker-compose

async def gerar_resposta(mensagem: str) -> str:
    """Gera uma resposta simples em português baseada na mensagem do usuário."""
    if not mensagem:
        return "Desculpe, não entendi. Pode reformular?"
    m = mensagem.lower()
    if "hotel" in m:
        return "Certo! Estou procurando hotéis disponíveis."
    elif "voo" in m or "passagem" in m:
        return "Tudo bem! Vou buscar voos disponíveis."
    else:
        return "Desculpe, não entendi. Pode reformular?"

async def salvar_historico(mensagem: str, resposta: str):
    """Envia o histórico para a API Java (em container 'api')."""
    payload = {"mensagem": mensagem, "resposta": resposta}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(URL_API, json=payload) as resp:
                if resp.status not in (200,201):
                    print(f"[ERRO] Falha ao salvar histórico: status {resp.status}")
    except Exception as e:
        print(f"[ERRO] Não foi possível conectar à API de histórico: {e}")
