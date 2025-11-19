"""
Chatbot Core Logic - Sistema Inteligente de Reservas
Gerencia conversas naturais com contexto e memória
"""
import luis_client
import text_analytics_client
import cosmos_client
import amadeus_client
import re
from datetime import datetime, timedelta

# Inicializar clientes com tratamento de erros
try:
    clu = luis_client.CluClient()
    text_analytics = text_analytics_client.TextAnalytics()
    store = cosmos_client.ConversationStore()
    amadeus = amadeus_client.AmadeusClient()
    print('[STARTUP] Todos os clientes inicializados', flush=True)
except Exception as e:
    print(f'[ERROR] Falha ao inicializar clientes: {str(e)}', flush=True)
    raise

# Intents suportados
FLIGHT_INTENTS = ['ComprarVoos', 'ConsultarVoos', 'CancelarVoos']
HOTEL_INTENTS = ['ReservarHotel', 'ConsultarHotel', 'CancelarHotel']

# Estados da conversa
CONVERSATION_STATES = {
    'IDLE': 'idle',
    'WAITING_FLIGHT_DETAILS': 'waiting_flight_details',
    'WAITING_FLIGHT_SELECTION': 'waiting_flight_selection',
    'WAITING_PAYMENT': 'waiting_payment',
    'WAITING_HOTEL_DETAILS': 'waiting_hotel_details',
    'WAITING_HOTEL_PAYMENT': 'waiting_hotel_payment',
    'WAITING_CANCELLATION_INFO': 'waiting_cancellation_info'
}

# Contexto global por usuário (em produção, usar Redis ou Cosmos DB)
user_contexts = {}


def get_user_context(user_id):
    """Recupera ou cria contexto do usuário"""
    if user_id not in user_contexts:
        user_contexts[user_id] = {
            'state': CONVERSATION_STATES['IDLE'],
            'data': {},
            'last_intent': None,
            'flight_offers': [],
            'hotel_offers': []
        }
    return user_contexts[user_id]


def update_user_context(user_id, updates):
    """Atualiza contexto do usuário"""
    context = get_user_context(user_id)
    context.update(updates)
    return context


def normalize_text(text):
    """Normaliza texto removendo acentos e convertendo para minúsculas"""
    import unicodedata
    # Remove acentos
    nfkd = unicodedata.normalize('NFKD', text)
    text_without_accents = ''.join([c for c in nfkd if not unicodedata.combining(c)])
    return text_without_accents.lower().strip()


def extract_detailed_info(text):
    """Extrai informações detalhadas da mensagem usando regex e NLP"""
    info = {}
    text_lower = text.lower()
    text_normalized = normalize_text(text)
    
    # Extrair cidade/destino expandido (com variações ortográficas)
    cities = {
        'zurique': 'Zurique', 'zurich': 'Zurique', 'lisboa': 'Lisboa', 'lisbon': 'Lisboa',
        'paris': 'Paris', 'pariz': 'Paris', 'dublin': 'Dublin', 'dublim': 'Dublin',
        'londres': 'Londres', 'london': 'Londres', 'roma': 'Roma', 'rome': 'Roma',
        'madrid': 'Madrid', 'madri': 'Madrid', 'barcelona': 'Barcelona', 'barça': 'Barcelona',
        'berlim': 'Berlim', 'berlin': 'Berlim', 'amsterdam': 'Amsterdam', 'amsterda': 'Amsterdam',
        'praga': 'Praga', 'prague': 'Praga', 'viena': 'Viena', 'vienna': 'Viena',
        'nova york': 'Nova York', 'new york': 'Nova York', 'ny': 'Nova York', 'miami': 'Miami',
        'tokyo': 'Tokyo', 'toquio': 'Tokyo', 'dubai': 'Dubai', 'dubay': 'Dubai',
        'sao paulo': 'São Paulo', 'são paulo': 'São Paulo', 'sampa': 'São Paulo',
        'rio': 'Rio de Janeiro', 'rio de janeiro': 'Rio de Janeiro', 'rj': 'Rio de Janeiro',
        'italia': 'Roma', 'italy': 'Roma', 'irlanda': 'Dublin', 'ireland': 'Dublin',
        'milano': 'Milano', 'milan': 'Milano', 'veneza': 'Veneza', 'venice': 'Veneza',
        'florenca': 'Florenca', 'florence': 'Florenca', 'janeiro': 'Rio de Janeiro',
        'chile': 'Santiago', 'santiago': 'Santiago', 'buenos aires': 'Buenos Aires',
        'buenosaires': 'Buenos Aires', 'lima': 'Lima', 'bogota': 'Bogota', 'bogotá': 'Bogota',
        'mexico': 'Cidade do Mexico', 'méxico': 'Cidade do Mexico', 'cancun': 'Cancun',
        'brasilia': 'Brasília', 'brasília': 'Brasília', 'salvador': 'Salvador',
        'fortaleza': 'Fortaleza', 'recife': 'Recife', 'manaus': 'Manaus'
    }
    
    # Buscar cidade usando texto normalizado (sem acentos, case-insensitive)
    for city_key, city_name in cities.items():
        city_key_normalized = normalize_text(city_key)
        if city_key_normalized in text_normalized:
            info['cidade'] = city_name
            break
    
    # Extrair datas
    date_patterns = [
        r'(\d{1,2})/(\d{1,2})/(\d{4})',
        r'(\d{1,2})-(\d{1,2})-(\d{4})',
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
    ]
    
    dates_found = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                if len(match[0]) == 4:
                    date_str = f"{match[0]}-{match[1].zfill(2)}-{match[2].zfill(2)}"
                else:
                    date_str = f"{match[2]}-{match[1].zfill(2)}-{match[0].zfill(2)}"
                dates_found.append(date_str)
            except:
                pass
    
    if len(dates_found) >= 2:
        info['data_ida'] = dates_found[0]
        info['data_volta'] = dates_found[1]
        info['checkin'] = dates_found[0]
        info['checkout'] = dates_found[1]
    elif len(dates_found) == 1:
        info['data_ida'] = dates_found[0]
        info['checkin'] = dates_found[0]
    
    # Extrair número de pessoas
    num_patterns = [
        r'(\d+)\s*(?:pessoa|pessoas|adulto|adultos|passageiro|passageiros)',
        r'(?:para|sao|são)\s+(\d+)',
    ]
    for pattern in num_patterns:
        match = re.search(pattern, text_lower)
        if match:
            info['pessoas'] = int(match.group(1))
            break
    
    # Extrair número de voo selecionado
    select_patterns = [
        r'(?:voo|opcao|opção|numero|número)?\s*(\d+)',
        r'^(\d+)$'
    ]
    for pattern in select_patterns:
        match = re.search(pattern, text_lower.strip())
        if match and 1 <= int(match.group(1)) <= 10:
            info['selecao'] = int(match.group(1))
            break
    
    # Extrair CPF
    cpf_patterns = [
        r'\b(\d{3}\.?\d{3}\.?\d{3}-?\d{2})\b',
        r'\b(\d{11})\b',
    ]
    for pattern in cpf_patterns:
        match = re.search(pattern, text)
        if match:
            cpf = match.group(1)
            cpf_digits = re.sub(r'\D', '', cpf)
            if len(cpf_digits) == 11:
                info['cpf'] = f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:]}"
                break
    
    # Extrair nome completo (aceita 2 ou mais palavras, maiúsculas ou minúsculas)
    # Primeiro tenta padrão capitalizado
    name_pattern = r'\b([A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][a-zàáâãéêíóôõúç]+(?:\s+[A-ZÀÁÂÃÉÊÍÓÔÕÚÇ][a-zàáâãéêíóôõúç]+)+)\b'
    name_matches = re.findall(name_pattern, text)
    for potential_name in name_matches:
        words = potential_name.split()
        city_lower = potential_name.lower()
        # Verificar que não é cidade e tem 2+ palavras
        if len(words) >= 2 and city_lower not in cities.keys() and not any(city in city_lower for city in ['paris', 'roma', 'lisboa', 'dublin', 'londres', 'janeiro']):
            info['nome'] = potential_name
            break
    
    # Se não encontrou, tenta padrão mais flexível (qualquer caso, 2+ palavras)
    if 'nome' not in info:
        # Remove números e símbolos comuns, pega sequências de 2+ palavras
        words_in_text = re.findall(r'\b[A-Za-zÀ-ÿ]{2,}\b', text)
        if len(words_in_text) >= 2:
            # Verifica se as primeiras 2-3 palavras podem ser um nome
            for i in range(len(words_in_text) - 1):
                candidate = ' '.join(words_in_text[i:i+2])
                candidate_lower = candidate.lower()
                # Ignora se é palavra comum ou cidade
                if candidate_lower not in cities.keys() and candidate_lower not in ['voo', 'para', 'hotel', 'quero', 'preciso', 'pessoas', 'pessoa', 'adulto', 'adultos']:
                    info['nome'] = candidate.title()  # Capitaliza o nome
                    break
    
    # Extrair forma de pagamento
    payment_keywords = {
        'crédito': 'Cartão de Crédito', 'credito': 'Cartão de Crédito',
        'débito': 'Cartão de Débito', 'debito': 'Cartão de Débito',
        'pix': 'PIX', 'boleto': 'Boleto', 'dinheiro': 'Dinheiro'
    }
    for keyword, payment_type in payment_keywords.items():
        if keyword in text_lower:
            info['pagamento'] = payment_type
            break
    
    return info


def handle_message(user_id, text):
    """Processa mensagem com contexto e máquina de estados"""
    try:
        # Salvar mensagem do usuário
        sentiment = None
        if text_analytics and text_analytics.client:
            sentiment = text_analytics.analyze_sentiment(text)
        
        if store and store.client:
            store.save_message(user_id, text, 'user', sentiment=sentiment)

        # Obter contexto do usuário
        context = get_user_context(user_id)
        current_state = context['state']
        
        # Extrair informações da mensagem
        detailed_info = extract_detailed_info(text)
        
        # Atualizar dados do contexto com novas informações
        context['data'].update({k: v for k, v in detailed_info.items() if v})
        
        # Reconhecer intent via CLU
        clu_res = clu.recognize(text)
        if 'error' in clu_res:
            print(f'[WARN] CLU error: {clu_res["error"]}', flush=True)
            reply = {'text': 'Desculpe, estou com problemas técnicos. Tente novamente em instantes.'}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply

        intent, entities = extract_intent_entities(clu_res)
        
        # Adicionar entidades ao contexto
        if entities.get('Cidade'):
            context['data']['cidade'] = entities['Cidade']
        if entities.get('Destino'):
            context['data']['cidade'] = entities['Destino']
        if entities.get('Origem'):
            context['data']['origem'] = entities['Origem']
        
        # Máquina de estados conversacional
        if current_state == CONVERSATION_STATES['IDLE']:
            # Estado inicial - processar novo intent
            if intent in FLIGHT_INTENTS:
                return handle_flight_conversation(user_id, intent, context, text)
            elif intent in HOTEL_INTENTS:
                return handle_hotel_conversation(user_id, intent, context, text)
            else:
                reply = {'text': "Olá! 👋 Sou seu assistente de viagens.\n\nPosso ajudar com:\n\n✈️ Voos - Consultar, comprar ou cancelar\n🏨 Hotéis - Reservar, consultar ou cancelar\n\nO que você precisa hoje?"}
                if store and store.client:
                    store.save_message(user_id, reply['text'], 'bot')
                return reply
        
        elif current_state == CONVERSATION_STATES['WAITING_FLIGHT_SELECTION']:
            return handle_flight_selection(user_id, context, detailed_info, text)
        
        elif current_state == CONVERSATION_STATES['WAITING_PAYMENT']:
            return handle_payment_info(user_id, context, detailed_info)
        
        elif current_state == CONVERSATION_STATES['WAITING_HOTEL_DETAILS']:
            return handle_hotel_conversation(user_id, 'ReservarHotel', context, text)
        
        elif current_state == CONVERSATION_STATES['WAITING_HOTEL_PAYMENT']:
            return handle_hotel_payment(user_id, context, detailed_info)
        
        else:
            # Estado desconhecido, resetar
            context['state'] = CONVERSATION_STATES['IDLE']
            return handle_message(user_id, text)
    
    except Exception as e:
        print(f'[ERROR] handle_message failed: {str(e)}', flush=True)
        return {'text': f'Erro: {str(e)[:100]}. Por favor, tente novamente.'}


def handle_flight_conversation(user_id, intent, context, text):
    """Gerencia conversa de voos de forma inteligente"""
    try:
        data = context['data']
        
        if intent == 'CancelarVoos':
            context['state'] = CONVERSATION_STATES['WAITING_CANCELLATION_INFO']
            reply = {'text': '❌ Vou ajudar com o cancelamento do seu voo.\n\nPreciso de:\n📝 Número da reserva ou localizador\n🆔 CPF do titular\n\nPor favor, me informe esses dados.'}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
        
        # Consultar ou Comprar Voos
        cidade_destino = data.get('cidade')
        origem = data.get('origem', 'São Paulo')
        
        if not cidade_destino:
            reply = {'text': '✈️ Perfeito! Para buscar os melhores voos, preciso saber:\n\n📍 Para qual cidade você quer viajar?\n\nExemplo: "quero voo para Roma" ou "voo para Rio de Janeiro"'}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
        
        # Buscar voos via Amadeus
        dest_code = amadeus_client.get_iata_code(cidade_destino.lower())
        
        if not dest_code:
            reply = {'text': f"🔍 Hmm, não encontrei '{cidade_destino}' no meu sistema.\n\nPor favor, especifique melhor a cidade.\n\nExemplos: Lisboa, Dublin, Paris, Nova York, Rio de Janeiro"}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
        
        # Buscar voos reais
        data_ida = data.get('data_ida', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
        pessoas = data.get('pessoas', 1)
        
        result = amadeus.search_flights(origem, cidade_destino.lower(), data_ida, adults=pessoas)
        
        if result and isinstance(result, list) and len(result) > 0:
            # Salvar ofertas no contexto
            context['flight_offers'] = result[:5]
            
            response_text = f"✈️ Encontrei {len(result)} voos de {origem} para {cidade_destino}!\n\n"
            response_text += f"🗓️ Data: {data_ida}\n👥 Passageiros: {pessoas}\n\n"
            response_text += "📋 Melhores opções:\n\n"
            
            for i, flight in enumerate(context['flight_offers'], 1):
                price = flight.get('price', {})
                price_total = price.get('total', 'N/A')
                currency = price.get('currency', 'EUR')
                
                if currency == 'EUR':
                    price_brl = float(price_total) * 6.0
                    price_display = f"€{price_total} ≈ R$ {price_brl:,.0f}".replace(',', '.')
                else:
                    price_display = f"{currency} {price_total}"
                
                itineraries = flight.get('itineraries', [])
                if itineraries:
                    segments = itineraries[0].get('segments', [])
                    if segments:
                        carrier = segments[0].get('carrierCode', '??')
                        departure = segments[0].get('departure', {}).get('at', '')
                        time = departure[11:16] if len(departure) > 11 else '??:??'
                        duration = itineraries[0].get('duration', '').replace('PT', '').replace('H', 'h').replace('M', 'm')
                        
                        response_text += f"{i}. {carrier} - Partida {time} - {price_display}"
                        if duration:
                            response_text += f" - {duration.lower()}"
                        response_text += "\n"
            
            # Mudar estado para aguardar seleção
            if intent == 'ComprarVoos':
                context['state'] = CONVERSATION_STATES['WAITING_FLIGHT_SELECTION']
                response_text += "\n\n💳 Para comprar: Digite o número do voo desejado (ex: 1, 2, 3...)"
            else:
                response_text += "\n\n📞 Gostou? Diga 'comprar voo [número]' para prosseguir!"
            
            reply = {'text': response_text}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
        
        else:
            reply = {'text': f"😔 Não encontrei voos disponíveis para {cidade_destino} nesta data.\n\nPosso ajudar com:\n• Outra cidade\n• Outra data\n\nO que prefere?"}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
    
    except Exception as e:
        print(f'[ERROR] handle_flight_conversation: {str(e)}', flush=True)
        return {'text': f'Erro ao buscar voos: {str(e)[:100]}'}


def handle_flight_selection(user_id, context, detailed_info, text):
    """Processa seleção de voo pelo usuário"""
    try:
        selecao = detailed_info.get('selecao')
        
        if not selecao or selecao > len(context['flight_offers']):
            reply = {'text': f"Por favor, escolha um voo válido (1 a {len(context['flight_offers'])}).\n\nDigite apenas o número."}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
        
        # Salvar voo selecionado
        selected_flight = context['flight_offers'][selecao - 1]
        context['data']['voo_selecionado'] = selected_flight
        context['data']['numero_voo'] = selecao
        
        # Extrair informações do voo
        price = selected_flight.get('price', {})
        price_total = price.get('total', 'N/A')
        currency = price.get('currency', 'EUR')
        
        if currency == 'EUR':
            price_brl = float(price_total) * 6.0
            price_display = f"€{price_total} (R$ {price_brl:,.0f})".replace(',', '.')
        else:
            price_display = f"{currency} {price_total}"
        
        # Solicitar dados de pagamento
        context['state'] = CONVERSATION_STATES['WAITING_PAYMENT']
        
        reply = {'text': f"✅ Ótima escolha! Voo #{selecao} selecionado.\n\n💰 Valor: {price_display}\n\n📋 Para finalizar, preciso de:\n\n1️⃣ Nome completo do passageiro\n2️⃣ CPF\n3️⃣ Forma de pagamento (crédito/débito/PIX)\n\nPode enviar tudo em uma mensagem!"}
        if store and store.client:
            store.save_message(user_id, reply['text'], 'bot')
        return reply
    
    except Exception as e:
        print(f'[ERROR] handle_flight_selection: {str(e)}', flush=True)
        return {'text': f'Erro: {str(e)[:100]}'}


def handle_payment_info(user_id, context, detailed_info):
    """Processa informações de pagamento"""
    try:
        nome = detailed_info.get('nome') or context['data'].get('nome')
        cpf = detailed_info.get('cpf') or context['data'].get('cpf')
        pagamento = detailed_info.get('pagamento') or context['data'].get('pagamento')
        
        # Atualizar dados
        if nome:
            context['data']['nome'] = nome
        if cpf:
            context['data']['cpf'] = cpf
        if pagamento:
            context['data']['pagamento'] = pagamento
        
        # Verificar se temos todos os dados
        if context['data'].get('nome') and context['data'].get('cpf') and context['data'].get('pagamento'):
            # Confirmar reserva
            voo = context['data']['voo_selecionado']
            price = voo.get('price', {})
            
            if price.get('currency') == 'EUR':
                price_brl = float(price.get('total')) * 6.0
                price_display = f"R$ {price_brl:,.0f}".replace(',', '.')
            else:
                price_display = f"{price.get('currency')} {price.get('total')}"
            
            # Gerar número de reserva
            reserva_num = f"VOO{context['data']['cpf'][-4:]}{datetime.now().strftime('%d%m%H%M')}"
            
            reply = {'text': f"🎉 Reserva confirmada com sucesso!\n\n📋 Resumo:\n✈️ Voo #{context['data']['numero_voo']}\n👤 {context['data']['nome']}\n🆔 CPF: {context['data']['cpf']}\n💳 {context['data']['pagamento']}\n💰 Total: {price_display}\n\n🎫 Número da reserva: {reserva_num}\n\n✅ Você receberá a confirmação por e-mail em instantes!\n\n🙏 Obrigado por escolher nossos serviços. Boa viagem!"}
            
            # Resetar contexto
            context['state'] = CONVERSATION_STATES['IDLE']
            context['data'] = {}
            context['flight_offers'] = []
            
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
        
        else:
            # Ainda faltam dados
            missing = []
            if not context['data'].get('nome'):
                missing.append('👤 Nome completo')
            if not context['data'].get('cpf'):
                missing.append('🆔 CPF')
            if not context['data'].get('pagamento'):
                missing.append('💳 Forma de pagamento')
            
            reply = {'text': f"Quase lá! Ainda preciso de:\n\n" + '\n'.join(missing) + "\n\nEnvie tudo em uma mensagem para agilizar!"}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
    
    except Exception as e:
        print(f'[ERROR] handle_payment_info: {str(e)}', flush=True)
        return {'text': f'Erro: {str(e)[:100]}'}


def extract_intent_entities(clu_response):
    """Extrai intent e entidades da resposta do CLU"""
    try:
        result = clu_response.get('result', {})
        prediction = result.get('prediction', {})
        intent = prediction.get('topIntent')
        
        entities = {}
        for entity in prediction.get('entities', []):
            category = entity.get('category')
            text = entity.get('text')
            if category and text:
                entities[category] = text
        
        return intent, entities
    except Exception:
        return None, {}


def handle_hotel_conversation(user_id, intent, context, text):
    """Gerencia conversa de hotéis de forma inteligente"""
    try:
        data = context['data']
        
        if intent == 'CancelarHotel':
            reply = {'text': '❌ Vou ajudar com o cancelamento da sua reserva de hotel.\n\nPreciso de:\n📝 Número da reserva\n👤 Nome do titular\n🆔 CPF\n\nPor favor, me informe esses dados.'}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
        
        # Consultar ou Reservar Hotel
        cidade = data.get('cidade')
        checkin = data.get('checkin')
        checkout = data.get('checkout')
        pessoas = data.get('pessoas')
        
        # Verificar informações necessárias
        if not cidade:
            reply = {'text': '🏨 Perfeito! Para buscar os melhores hotéis, preciso saber:\n\n📍 Em qual cidade?\n📅 Check-in? (DD/MM/YYYY)\n📅 Check-out? (DD/MM/YYYY)\n👥 Quantas pessoas?\n\nPode enviar tudo em uma mensagem!'}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            context['state'] = CONVERSATION_STATES['WAITING_HOTEL_DETAILS']
            return reply
        
        if not checkin or not checkout:
            reply = {'text': f"Ótimo! Hotel em {cidade}.\n\nAinda preciso de:\n\n📅 Data check-in (DD/MM/YYYY)\n📅 Data check-out (DD/MM/YYYY)" + (f"\n👥 Número de pessoas" if not pessoas else "") + "\n\n💡 Envie as datas em uma mensagem!"}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            context['state'] = CONVERSATION_STATES['WAITING_HOTEL_DETAILS']
            return reply
        
        if not pessoas:
            pessoas = 1
            data['pessoas'] = 1
        
        # Buscar hotéis via Amadeus
        city_code = amadeus_client.get_iata_code(cidade.lower())
        
        if not city_code:
            reply = {'text': f"🔍 Não encontrei '{cidade}' no sistema.\n\nTente: Lisboa, Paris, Dublin, Nova York, Rio de Janeiro..."}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
        
        result = amadeus.search_hotels(city_code, checkin, checkout, roomQuantity=1)
        
        if isinstance(result, dict) and 'error' in result:
            error_msg = result['error']
            print(f"[ERROR] Amadeus API error: {error_msg}", flush=True)
            reply = {'text': f"❌ Erro: {error_msg}\n\nTente:\n• Outra cidade\n• Outras datas"}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
        
        if result and isinstance(result, list) and len(result) > 0:
            context['hotel_offers'] = result[:5]
            
            response_text = f"🏨 Encontrei {len(result)} hotéis em {cidade}!\n\n"
            response_text += f"📅 {checkin} até {checkout}\n👥 {pessoas} pessoa(s)\n\n"
            response_text += "🏆 Melhores opções:\n\n"
            
            for i, hotel in enumerate(context['hotel_offers'], 1):
                name = hotel.get('hotel', {}).get('name', 'Hotel')
                offers = hotel.get('offers', [])
                if offers:
                    price = offers[0].get('price', {})
                    total = price.get('total', 'N/A')
                    currency = price.get('currency', 'EUR')
                    
                    if currency == 'EUR':
                        price_brl = float(total) * 6.0
                        price_display = f"€{total} ≈ R$ {price_brl:.0f}/noite"
                    else:
                        price_display = f"{currency} {total}/noite"
                    
                    response_text += f"{i}. {name}\n   {price_display}\n\n"
            
            if intent == 'ReservarHotel':
                context['state'] = CONVERSATION_STATES['WAITING_HOTEL_PAYMENT']
                response_text += "💳 Para reservar: Digite o número do hotel\n\nDepois precisarei de: nome, CPF e forma de pagamento"
            else:
                response_text += "📞 Gostou? Diga 'reservar hotel [número]'"
            
            reply = {'text': response_text}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
        
        else:
            reply = {'text': f"😔 Não encontrei hotéis disponíveis em {cidade} para essas datas.\n\nPosso ajudar com:\n• Outra cidade\n• Outras datas"}
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
    
    except Exception as e:
        print(f'[ERROR] handle_hotel_conversation: {str(e)}', flush=True)
        return {'text': f'Erro ao buscar hotéis: {str(e)[:100]}'}


def handle_hotel_payment(user_id, context, detailed_info):
    """Processa pagamento e confirmação de hotel"""
    try:
        # Verificar seleção de hotel
        selecao = detailed_info.get('selecao')
        
        if selecao and selecao <= len(context.get('hotel_offers', [])):
            context['data']['hotel_selecionado'] = context['hotel_offers'][selecao - 1]
            context['data']['numero_hotel'] = selecao
        
        # Atualizar dados de pagamento
        if detailed_info.get('nome'):
            context['data']['nome'] = detailed_info['nome']
        if detailed_info.get('cpf'):
            context['data']['cpf'] = detailed_info['cpf']
        if detailed_info.get('pagamento'):
            context['data']['pagamento'] = detailed_info['pagamento']
        
        # Verificar se temos todos os dados
        if (context['data'].get('hotel_selecionado') and 
            context['data'].get('nome') and 
            context['data'].get('cpf') and 
            context['data'].get('pagamento')):
            
            hotel = context['data']['hotel_selecionado']
            hotel_name = hotel.get('hotel', {}).get('name', 'Hotel')
            
            offers = hotel.get('offers', [])
            if offers:
                price = offers[0].get('price', {})
                total = float(price.get('total', 0))
                currency = price.get('currency', 'EUR')
                
                if currency == 'EUR':
                    price_brl = total * 6.0
                    price_display = f"R$ {price_brl:.0f}"
                else:
                    price_display = f"{currency} {total}"
            else:
                price_display = "N/A"
            
            reserva_num = f"HTL{context['data']['cpf'][-4:]}{datetime.now().strftime('%d%m%H%M')}"
            
            reply = {'text': f"🎉 Reserva confirmada com sucesso!\n\n📋 Resumo:\n🏨 {hotel_name}\n📍 {context['data']['cidade']}\n📅 {context['data']['checkin']} até {context['data']['checkout']}\n👥 {context['data']['pessoas']} pessoa(s)\n\n👤 {context['data']['nome']}\n🆔 {context['data']['cpf']}\n💳 {context['data']['pagamento']}\n💰 Total: {price_display}\n\n🎫 Número da reserva: {reserva_num}\n\n✅ Confirmação enviada por e-mail!\n\n🙏 Ótima estadia!"}
            
            # Resetar contexto
            context['state'] = CONVERSATION_STATES['IDLE']
            context['data'] = {}
            context['hotel_offers'] = []
            
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
        
        else:
            # Solicitar dados faltantes
            if not context['data'].get('hotel_selecionado'):
                reply = {'text': f"Por favor, escolha um hotel (1 a {len(context.get('hotel_offers', []))}).\n\nDigite o número."}
            else:
                missing = []
                if not context['data'].get('nome'):
                    missing.append('👤 Nome completo')
                if not context['data'].get('cpf'):
                    missing.append('🆔 CPF')
                if not context['data'].get('pagamento'):
                    missing.append('💳 Forma de pagamento (crédito/débito/PIX)')
                
                reply = {'text': f"Quase lá! Ainda preciso de:\n\n" + '\n'.join(missing) + "\n\nEnvie tudo em uma mensagem!"}
            
            if store and store.client:
                store.save_message(user_id, reply['text'], 'bot')
            return reply
    
    except Exception as e:
        print(f'[ERROR] handle_hotel_payment: {str(e)}', flush=True)
        return {'text': f'Erro: {str(e)[:100]}'}


def rest_handle(req_json):
    """Handler para requisições REST (usado pelo Flask)"""
    try:
        user_id = req_json.get('userId', 'anonymous')
        text = req_json.get('message', '').strip()
        
        if not text:
            return {'response': 'Mensagem vazia', 'error': True}
        
        result = handle_message(user_id, text)
        return {'response': result.get('text', 'Erro desconhecido')}
    
    except Exception as e:
        print(f'[ERROR] rest_handle: {str(e)}', flush=True)
        return {'response': f'Erro interno: {str(e)[:100]}', 'error': True}


if __name__ == '__main__':
    # Manual test
    print('[TEST] Testando bot...')
    print(rest_handle({'userId': 'test1', 'message': 'Olá'}))
    print(rest_handle({'userId': 'test1', 'message': 'Quero voo para Lisboa'}))
