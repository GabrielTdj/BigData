# ✈️ Flight & Hotel Chatbot - Assistente de Viagens

Chatbot inteligente para consulta, reserva e cancelamento de voos e hotéis, desenvolvido com Azure AI Services e integração com Amadeus API.

## 🌐 Deploy em Produção

**URL do Projeto:** https://chatbotviagem-eva3g9gxe7edbxde.eastus2-01.azurewebsites.net

## 🎯 Funcionalidades

### Intents Implementados
1. **ComprarVoos** - Consulta e compra de passagens aéreas
2. **ConsultarVoos** - Consulta de voos disponíveis
3. **CancelarVoos** - Cancelamento de reservas de voos
4. **ReservarHotel** - Reserva de hotéis
5. **ConsultarHotel** - Consulta de hotéis disponíveis
6. **CancelarHotel** - Cancelamento de reservas de hotéis

### Entidades/Tokens Reconhecidos
- **Origem** - Cidade de partida
- **Destino** - Cidade de destino
- **Cidade** - Cidade para reserva de hotel
- **Data** - Datas de check-in/check-out, ida/volta
- **NumeroPessoas** - Quantidade de pessoas/hóspedes

## 🏗️ Arquitetura

### Backend (Python)
- **Flask 2.2.5** - API REST
- **Gunicorn 21.2.0** - Servidor de produção
- **Máquina de Estados** - Gerenciamento de conversação
- **Normalização de Texto** - Case e accent insensitive

### Serviços Azure
- **Azure Language Service (CLU)** - Compreensão de linguagem natural
- **Azure Text Analytics** - Análise de sentimento
- **Azure Cosmos DB** - Histórico de conversas
- **Azure App Service** - Hospedagem (Python 3.11 Linux)

### APIs Externas
- **Amadeus API** - Dados reais de voos e hotéis
  - 70+ ofertas de voos por consulta
  - Hotéis com fallback para garantir disponibilidade

### Frontend
- **WebChat Interface** - HTML/JavaScript
- **Markdown Rendering** - Formatação de respostas do bot
- **Normalização** - Tratamento de acentos e maiúsculas

## 🚀 CI/CD

### GitHub Actions
- **Workflow:** `.github/workflows/main_chatbotviagem.yml`
- **Autenticação:** Federated Identity (sem publish profile)
- **Build:** ZIP do backend com exclusão de venv
- **Deploy:** UNZIP + Azure WebApps Deploy
- **Trigger:** Push para branch `main`

## 📁 Estrutura do Projeto

```
flight-hotel-chatbot/
├── backend/python/
│   ├── app.py                    # Flask API + Frontend serving
│   ├── bot.py                    # Lógica do chatbot e estados
│   ├── amadeus_client.py         # Integração Amadeus (voos/hotéis)
│   ├── luis_client.py            # Integração Azure CLU
│   ├── cosmos_client.py          # Armazenamento Cosmos DB
│   ├── text_analytics_client.py # Análise de sentimento
│   ├── azure_config.py           # Configurações Azure
│   ├── requirements.txt          # Dependências Python
│   └── .env                      # Variáveis de ambiente (14 vars)
├── frontend/webchat/
│   ├── index.html                # Interface do usuário
│   └── app.js                    # Lógica frontend + API calls
├── .github/workflows/
│   └── main_chatbotviagem.yml    # Pipeline CI/CD
├── .gitignore
└── README.md
```

## ⚙️ Variáveis de Ambiente

### Azure Language Service (CLU)
- `AZURE_LANGUAGE_KEY`
- `AZURE_LANGUAGE_ENDPOINT`
- `CLU_PROJECT_NAME`
- `CLU_DEPLOYMENT_NAME`

### Azure Text Analytics
- `TEXT_ANALYTICS_KEY`
- `TEXT_ANALYTICS_ENDPOINT`

### Azure Cosmos DB
- `COSMOS_ENDPOINT`
- `COSMOS_KEY`
- `COSMOS_DATABASE`
- `COSMOS_CONTAINER`

### Amadeus API
- `AMADEUS_CLIENT_ID`
- `AMADEUS_CLIENT_SECRET`

### Servidor
- `PORT` (padrão: 8000)

## 🎮 Como Usar

1. Acesse: https://chatbotviagem-eva3g9gxe7edbxde.eastus2-01.azurewebsites.net
2. Digite mensagens naturais como:
   - "Quero um voo para Paris"
   - "Reservar hotel em Lisboa"
   - "Cancelar minha reserva de voo"
3. O bot guiará você através do processo de reserva

## ✅ Requisitos do Projeto

- ✅ **CLU Integration** - Azure Language Understanding configurado
- ✅ **6 Intents** - Todos implementados com entidades
- ✅ **Azure Deployment** - App Service ativo e funcional
- ✅ **GitHub Actions** - CI/CD automatizado
- ✅ **Amadeus API** - Dados reais de voos e hotéis
- ✅ **Frontend + Backend** - Aplicação completa integrada

## 🔗 Links Úteis

- **Aplicação:** https://chatbotviagem-eva3g9gxe7edbxde.eastus2-01.azurewebsites.net
- **Repositório:** https://github.com/GabrielTdj/BigData
- **GitHub Actions:** https://github.com/GabrielTdj/BigData/actions

## 📊 Status do Projeto

**Status:** ✅ Produção  
**Última Atualização:** Novembro 2025  
**Versão:** 1.0
