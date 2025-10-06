# AP1BIGDATA - Chatbot integrado (Português)

Projeto pronto para apresentação: Bot (Python) em português, API (Java Spring Boot) para salvar histórico e PostgreSQL.
Tudo orquestrado com Docker Compose.

## Requisitos
- Docker Desktop (Windows) com WSL2 recomendado
- VS Code (opcional para visualizar arquivos)
- Bot Framework Emulator (desktop) para conversar com o bot

## Como rodar (Windows)
1. Extraia o ZIP e abra a pasta `AP1BIGDATA` no VS Code.
2. No terminal integrado, execute:
   ```bash
   docker compose up --build
   ```
3. Aguarde até os containers subirem (pode demorar na primeira execução).
4. Abra o Bot Framework Emulator e em *Open Bot* coloque:
   - Bot URL: `http://localhost:3978/api/messages`
   - Microsoft App ID / Password: deixar em branco
5. Converse com o bot em português. Exemplos de mensagens:
   - "Quero hotel em São Paulo"
   - "Preciso de passagem"
   - "Oi"

## Verificar histórico salvo
No terminal com docker-compose rodando, execute:
```bash
docker compose exec db psql -U postgres -d chatbotdb -c "SELECT id, mensagem, resposta, data_hora FROM conversas ORDER BY id DESC LIMIT 20;"
```

## Parar os serviços
```bash
docker compose down
```

## Observações
- Tudo foi traduzido para português (variáveis, classes e mensagens) para parecer autoria pessoal.
- Se houver erro ao buildar a API, verifique se o Maven consegue acessar a internet para baixar dependências.
