# 🚀 Guia Completo de Deploy - Azure

## 📋 Pré-requisitos

Antes de fazer o deploy, você precisa ter:

✅ **Recursos Azure criados:**
- Azure Language Service (CLU)
- Azure Text Analytics
- Azure Cosmos DB
- Amadeus API (conta developer)

✅ **Ferramentas instaladas:**
- Azure CLI (`az --version`)
- Git configurado
- Conta GitHub

---

## 🎯 Passo 1: Criar Azure Web App

### Via Portal Azure:

1. **Acesse:** https://portal.azure.com
2. **Clique:** "Criar um recurso" → "Aplicativo Web"
3. **Configure:**
   - **Assinatura:** Sua subscription
   - **Grupo de Recursos:** Criar novo ou usar existente (ex: `rg-chatbot-prod`)
   - **Nome:** `chatbot-voos-hoteis` (será: chatbot-voos-hoteis.azurewebsites.net)
   - **Publicar:** `Código`
   - **Pilha de runtime:** `Python 3.11`
   - **Região:** `East US 2` (ou mais próxima)
   - **Plano Linux:** Criar novo ou usar existente
   - **SKU:** `B1` (Basic) ou `F1` (Free - para testes)

4. **Clique:** "Revisar + criar" → "Criar"

### Via Azure CLI:

```bash
# Login
az login

# Criar grupo de recursos (se não existir)
az group create --name rg-chatbot-prod --location eastus2

# Criar plano de serviço
az appservice plan create \
  --name plan-chatbot \
  --resource-group rg-chatbot-prod \
  --sku B1 \
  --is-linux

# Criar Web App
az webapp create \
  --name chatbot-voos-hoteis \
  --resource-group rg-chatbot-prod \
  --plan plan-chatbot \
  --runtime "PYTHON:3.11"
```

---

## 🔐 Passo 2: Configurar Variáveis de Ambiente

### Via Portal Azure:

1. **Acesse:** Web App criado → "Configuração" (menu lateral)
2. **Clique:** "Configurações do aplicativo" → "+ Nova configuração do aplicativo"
3. **Adicione cada variável:**

| Nome | Valor | Onde Encontrar |
|------|-------|----------------|
| `CLU_PROJECT_NAME` | `Chatbot` | Azure Language Studio → Seu projeto |
| `CLU_DEPLOYMENT_NAME` | `Chatbot` | Azure Language Studio → Deployments |
| `CLU_ENDPOINT` | `https://seu-clu.cognitiveservices.azure.com` | Language Service → Chaves e Ponto de Extremidade |
| `CLU_KEY` | `sua-chave-clu` | Language Service → Chaves e Ponto de Extremidade |
| `TEXT_ANALYTICS_ENDPOINT` | `https://seu-ta.cognitiveservices.azure.com` | Text Analytics → Chaves e Ponto de Extremidade |
| `TEXT_ANALYTICS_KEY` | `sua-chave-ta` | Text Analytics → Chaves e Ponto de Extremidade |
| `AMADEUS_CLIENT_ID` | `seu-client-id` | Amadeus Developer Portal → Apps |
| `AMADEUS_CLIENT_SECRET` | `seu-secret` | Amadeus Developer Portal → Apps |
| `COSMOS_ENDPOINT` | `https://seu-cosmos.documents.azure.com:443/` | Cosmos DB → Chaves |
| `COSMOS_KEY` | `sua-chave-cosmos` | Cosmos DB → Chaves → PRIMARY KEY |
| `COSMOS_DATABASE` | `chatbotdb` | Nome do banco que você criou |
| `COSMOS_CONTAINER` | `conversations` | Nome do container que você criou |
| `PORT` | `8000` | Porta padrão Azure |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` | Habilita build automático |

4. **Clique:** "Salvar" (no topo da página)

### Via Azure CLI:

```bash
# Definir variáveis (substitua pelos seus valores)
az webapp config appsettings set \
  --name chatbot-voos-hoteis \
  --resource-group rg-chatbot-prod \
  --settings \
    CLU_PROJECT_NAME="Chatbot" \
    CLU_DEPLOYMENT_NAME="Chatbot" \
    CLU_ENDPOINT="https://seu-clu.cognitiveservices.azure.com" \
    CLU_KEY="sua-chave" \
    TEXT_ANALYTICS_ENDPOINT="https://seu-ta.cognitiveservices.azure.com" \
    TEXT_ANALYTICS_KEY="sua-chave" \
    AMADEUS_CLIENT_ID="seu-id" \
    AMADEUS_CLIENT_SECRET="seu-secret" \
    COSMOS_ENDPOINT="https://seu-cosmos.documents.azure.com:443/" \
    COSMOS_KEY="sua-chave" \
    COSMOS_DATABASE="chatbotdb" \
    COSMOS_CONTAINER="conversations" \
    PORT="8000" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"
```

---

## 📦 Passo 3: Configurar Startup Command

### Via Portal Azure:

1. **Acesse:** Web App → "Configuração" → "Configurações gerais"
2. **Comando de inicialização:** 
   ```bash
   gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app
   ```
3. **Clique:** "Salvar"

### Adicionar gunicorn ao requirements.txt:

Antes de fazer deploy, adicione ao `backend/python/requirements.txt`:
```
gunicorn==21.2.0
```

---

## 🔄 Passo 4: Deploy Automático com GitHub Actions

### 4.1 Obter Perfil de Publicação

**Via Portal:**
1. **Acesse:** Web App → "Visão geral"
2. **Clique:** "Obter perfil de publicação" (botão no topo)
3. **Salve** o arquivo `.PublishSettings` baixado

### 4.2 Adicionar Secret no GitHub

1. **Acesse:** Seu repositório GitHub
2. **Clique:** "Settings" → "Secrets and variables" → "Actions"
3. **Clique:** "New repository secret"
4. **Configure:**
   - **Nome:** `AZURE_WEBAPP_PUBLISH_PROFILE_PY`
   - **Valor:** Cole todo o conteúdo do arquivo `.PublishSettings`
5. **Clique:** "Add secret"

### 4.3 Adicionar Nome do Web App

1. **Clique:** "New repository secret"
2. **Configure:**
   - **Nome:** `AZURE_WEBAPP_NAME_PY`
   - **Valor:** `chatbot-voos-hoteis` (nome do seu Web App)
3. **Clique:** "Add secret"

### 4.4 Workflow já configurado ✅

O arquivo `.github/workflows/azure-deploy-python.yml` já está pronto!

**O que ele faz:**
- ✅ Roda automaticamente quando você faz `git push` na branch `main`
- ✅ Instala dependências Python
- ✅ Faz deploy do conteúdo de `backend/python/` para o Azure

---

## 🚀 Passo 5: Fazer o Deploy

### 5.1 Commit e Push

```bash
# No terminal, na pasta do projeto
cd C:\Users\202402627295\Desktop\BigData\flight-hotel-chatbot

# Adicionar arquivos
git add .

# Commit
git commit -m "Deploy: chatbot voos e hotéis"

# Push para GitHub (dispara o workflow)
git push origin main
```

### 5.2 Acompanhar Deploy

1. **Acesse:** GitHub → Seu repositório → "Actions"
2. **Veja:** O workflow rodando em tempo real
3. **Aguarde:** Deploy completo (~3-5 minutos)

---

## 🧪 Passo 6: Testar a Aplicação

### 6.1 Testar API Backend

```bash
# URL do seu backend
https://chatbot-voos-hoteis.azurewebsites.net/health

# Deve retornar:
{
  "status": "ok",
  "service": "flight-hotel-chatbot"
}
```

### 6.2 Testar Chat

```bash
curl -X POST https://chatbot-voos-hoteis.azurewebsites.net/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test123",
    "message": "quero voo para paris"
  }'
```

---

## 🌐 Passo 7: Deploy do Frontend (Opcional)

### Opção A: Azure Static Web Apps

```bash
# Criar Static Web App
az staticwebapp create \
  --name chatbot-frontend \
  --resource-group rg-chatbot-prod \
  --source frontend/webchat \
  --location eastus2 \
  --branch main \
  --app-location "/" \
  --output-location "/"
```

### Opção B: Azure Storage (Static Website)

```bash
# Criar storage account
az storage account create \
  --name chatbotfrontendstorage \
  --resource-group rg-chatbot-prod \
  --location eastus2 \
  --sku Standard_LRS

# Habilitar static website
az storage blob service-properties update \
  --account-name chatbotfrontendstorage \
  --static-website \
  --index-document index.html

# Upload dos arquivos
az storage blob upload-batch \
  --account-name chatbotfrontendstorage \
  --destination '$web' \
  --source frontend/webchat
```

### Atualizar URL da API no Frontend

Edite `frontend/webchat/app.js`:
```javascript
// Linha ~100
const API_URL = 'https://chatbot-voos-hoteis.azurewebsites.net/api/chat';
```

---

## 🔍 Passo 8: Monitoramento e Logs

### Ver Logs em Tempo Real

**Via Portal:**
1. **Acesse:** Web App → "Log stream" (menu lateral)
2. **Escolha:** "Application logs"

**Via CLI:**
```bash
az webapp log tail \
  --name chatbot-voos-hoteis \
  --resource-group rg-chatbot-prod
```

### Habilitar Application Insights (Recomendado)

```bash
# Criar Application Insights
az monitor app-insights component create \
  --app chatbot-insights \
  --location eastus2 \
  --resource-group rg-chatbot-prod \
  --application-type web

# Conectar ao Web App
az webapp config appsettings set \
  --name chatbot-voos-hoteis \
  --resource-group rg-chatbot-prod \
  --settings APPLICATIONINSIGHTS_CONNECTION_STRING="<connection-string>"
```

---

## ✅ Checklist Final

### Recursos Azure Criados:
- [ ] Azure Language Service (CLU) configurado com 6 intents
- [ ] Text Analytics com Sentiment Analysis
- [ ] Cosmos DB com database `chatbotdb` e container `conversations`
- [ ] Web App Python 3.11 criado
- [ ] Variáveis de ambiente configuradas (14 variáveis)
- [ ] Startup command configurado (gunicorn)
- [ ] Application Insights habilitado (opcional)

### GitHub:
- [ ] Repositório criado e código commitado
- [ ] Secret `AZURE_WEBAPP_PUBLISH_PROFILE_PY` adicionado
- [ ] Secret `AZURE_WEBAPP_NAME_PY` adicionado
- [ ] Workflow `.github/workflows/azure-deploy-python.yml` presente
- [ ] Push para branch `main` feito

### Testes:
- [ ] Endpoint `/health` retorna 200
- [ ] Endpoint `/api/chat` responde a mensagens
- [ ] Voos: "quero voo para paris" retorna lista de voos
- [ ] Hotéis: "hotel em lisboa" retorna lista de hotéis
- [ ] Fluxo completo: seleção + pagamento + confirmação
- [ ] Histórico salvo no Cosmos DB
- [ ] Markdown renderizado no frontend (**negrito**, _itálico_)
- [ ] Aceita variações: chile/Chile/CHILE, sao paulo/São Paulo

---

## 🐛 Troubleshooting

### Erro: "Application Error"
**Solução:** Verifique logs com `az webapp log tail`

### Erro: "Module not found"
**Solução:** Adicione `SCM_DO_BUILD_DURING_DEPLOYMENT=true` nas configurações

### Erro: "Connection timeout"
**Solução:** Aumente timeout no gunicorn: `--timeout 600`

### Erro: Amadeus API 400
**Solução:** Já implementado fallback com hotéis simulados

### Frontend não conecta ao backend
**Solução:** Verifique CORS no `app.py` e URL em `app.js`

---

## 💰 Custos Estimados

| Recurso | SKU | Custo Mensal (USD) |
|---------|-----|-------------------|
| Web App | B1 Basic | ~$13 |
| Web App | F1 Free | $0 |
| Language Service | Free (F0) | $0 até 5k chamadas/mês |
| Text Analytics | Free (F0) | $0 até 5k chamadas/mês |
| Cosmos DB | Free tier | $0 até 1000 RU/s |
| Storage (Frontend) | Standard | ~$0.50 |
| **TOTAL (Free tier)** | | **~$0.50/mês** |
| **TOTAL (Basic)** | | **~$13.50/mês** |

---

## 📚 Recursos Úteis

- **Azure Portal:** https://portal.azure.com
- **Azure CLI Docs:** https://learn.microsoft.com/cli/azure/
- **GitHub Actions:** https://docs.github.com/actions
- **Amadeus API:** https://developers.amadeus.com
- **Flask Azure:** https://learn.microsoft.com/azure/app-service/quickstart-python

---

## 🎯 Próximos Passos

Após deploy concluído:

1. ✅ Configurar domínio customizado (opcional)
2. ✅ Habilitar HTTPS (automático no Azure)
3. ✅ Configurar autoscaling (se necessário)
4. ✅ Adicionar testes automatizados
5. ✅ Configurar CI/CD para staging + produção
6. ✅ Monitorar custos no Azure Cost Management

---

**Desenvolvido com:** Python 3.13 | Flask | Azure CLU | Amadeus API | Cosmos DB  
**Status:** ✅ Pronto para produção
