from amadeus import Client, ResponseError
import azure_config

# Mapeamento de cidades para códigos IATA (com variações ortográficas)
CITY_TO_IATA = {
    'lisboa': 'LIS', 'lisbon': 'LIS',
    'madrid': 'MAD', 'madri': 'MAD',
    'paris': 'CDG', 'pariz': 'CDG',
    'londres': 'LHR', 'london': 'LHR',
    'roma': 'FCO', 'rome': 'FCO',
    'barcelona': 'BCN', 'barça': 'BCN',
    'berlim': 'BER', 'berlin': 'BER',
    'amsterda': 'AMS', 'amsterdam': 'AMS',
    'dublin': 'DUB', 'dublim': 'DUB',
    'irlanda': 'DUB', 'ireland': 'DUB',
    'praga': 'PRG', 'prague': 'PRG',
    'viena': 'VIE', 'vienna': 'VIE',
    'budapeste': 'BUD',
    'varsovia': 'WAW',
    'atenas': 'ATH',
    'istambul': 'IST',
    'italia': 'FCO',
    'milao': 'MXP',
    'veneza': 'VCE',
    'florenca': 'FLR',
    'napoles': 'NAP',
    'sao paulo': 'GRU',
    'rio de janeiro': 'GIG',
    'rio': 'GIG',
    'brasilia': 'BSB',
    'salvador': 'SSA',
    'fortaleza': 'FOR',
    'recife': 'REC',
    'manaus': 'MAO',
    'curitiba': 'CWB',
    'porto alegre': 'POA',
    'belo horizonte': 'CNF',
    'miami': 'MIA',
    'nova york': 'JFK',
    'nova iorque': 'JFK',
    'new york': 'JFK',
    'los angeles': 'LAX',
    'chicago': 'ORD',
    'toronto': 'YYZ',
    'cidade do mexico': 'MEX',
    'mexico': 'MEX',
    'buenos aires': 'EZE',
    'lima': 'LIM',
    'santiago': 'SCL',
    'chile': 'SCL',
    'bogota': 'BOG',
    'toquio': 'NRT',
    'tokyo': 'NRT',
    'seul': 'ICN',
    'pequim': 'PEK',
    'xangai': 'PVG',
    'singapura': 'SIN',
    'dubai': 'DXB',
    'sidney': 'SYD',
    'sydney': 'SYD',
    'melbourne': 'MEL',
}

def normalize_city_name(city_name):
    """Remove acentos e normaliza nome da cidade"""
    import unicodedata
    nfkd = unicodedata.normalize('NFKD', city_name)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()

def get_iata_code(city_name):
    """Converte nome de cidade para código IATA (tolerante a erros)"""
    if not city_name:
        return None
    city_lower = city_name.lower().strip()
    city_normalized = normalize_city_name(city_name)
    
    # Se já é um código IATA (3 letras maiúsculas)
    if len(city_lower) == 3:
        return city_lower.upper()
    
    # Buscar no dicionário (original e normalizado)
    return CITY_TO_IATA.get(city_lower) or CITY_TO_IATA.get(city_normalized)

class AmadeusClient:
    def __init__(self):
        if not azure_config.AMADEUS_CLIENT_ID or not azure_config.AMADEUS_CLIENT_SECRET:
            self.client = None
        else:
            self.client = Client(client_id=azure_config.AMADEUS_CLIENT_ID, client_secret=azure_config.AMADEUS_CLIENT_SECRET)

    def search_flights(self, origin, destination, departureDate, returnDate=None, adults=1):
        if not self.client:
            return {'error': 'Amadeus credentials not set'}
        
        # Converter nomes de cidades para códigos IATA
        origin_code = get_iata_code(origin) or 'GRU'
        dest_code = get_iata_code(destination)
        
        if not dest_code:
            return {'error': f'Cidade {destination} não encontrada'}
        
        try:
            response = self.client.shopping.flight_offers_search.get(
                originLocationCode=origin_code,
                destinationLocationCode=dest_code,
                departureDate=departureDate,
                adults=adults
            )
            return response.data
        except ResponseError as e:
            return {'error': str(e)}

    def search_hotels(self, cityCode, checkInDate, checkOutDate, roomQuantity=1):
        if not self.client:
            return {'error': 'Amadeus credentials not set'}
        
        print(f"[INFO] Usando dados simulados para hotéis (Amadeus API limitada)", flush=True)
        
        # Simulação realista baseada na cidade
        city_hotels = {
            'LIS': [
                {'name': 'Hotel Avenida Palace', 'price': 120},
                {'name': 'Memmo Alfama Hotel', 'price': 95},
                {'name': 'Lisboa Carmo Hotel', 'price': 85},
                {'name': 'Hotel do Chiado', 'price': 110},
                {'name': 'Browns Downtown Hotel', 'price': 75}
            ],
            'CDG': [
                {'name': 'Hotel Eiffel Trocadéro', 'price': 150},
                {'name': 'Le Marais Boutique Hotel', 'price': 130},
                {'name': 'Montmartre Hotel', 'price': 95},
                {'name': 'Latin Quarter Hotel', 'price': 110},
                {'name': 'Champs Elysées Plaza', 'price': 180}
            ],
            'FCO': [
                {'name': 'Hotel Artemide', 'price': 140},
                {'name': 'Hotel Forum', 'price': 130},
                {'name': 'Hotel Centrale', 'price': 95},
                {'name': 'NH Collection Palazzo Cinquecento', 'price': 150},
                {'name': 'Hotel Quirinale', 'price': 120}
            ],
            'SCL': [
                {'name': 'Hotel Plaza San Francisco', 'price': 100},
                {'name': 'The Singular Santiago', 'price': 140},
                {'name': 'W Santiago', 'price': 160},
                {'name': 'Hotel Cumbres Lastarria', 'price': 90},
                {'name': 'NH Collection Plaza Santiago', 'price': 110}
            ],
            'DUB': [
                {'name': 'The Merrion Hotel', 'price': 180},
                {'name': 'Trinity City Hotel', 'price': 120},
                {'name': 'The Marker Hotel', 'price': 150},
                {'name': 'Clayton Hotel Burlington Road', 'price': 95},
                {'name': 'The Morrison Hotel', 'price': 110}
            ],
            'GIG': [
                {'name': 'Copacabana Palace', 'price': 250},
                {'name': 'Hotel Fasano Rio de Janeiro', 'price': 280},
                {'name': 'Belmond Copacabana Palace', 'price': 300},
                {'name': 'Porto Bay Rio Internacional', 'price': 150},
                {'name': 'Hotel Atlantico Copacabana', 'price': 120}
            ]
        }
        
        # Hotéis genéricos para cidades não mapeadas
        default_hotels = [
            {'name': f'Grand Hotel {cityCode}', 'price': 100},
            {'name': f'{cityCode} Plaza Hotel', 'price': 120},
            {'name': f'Central {cityCode} Hotel', 'price': 85},
            {'name': f'{cityCode} Boutique Hotel', 'price': 95},
            {'name': f'Downtown {cityCode} Hotel', 'price': 75}
        ]
        
        hotels_data = city_hotels.get(cityCode, default_hotels)
        
        # Formatar no padrão Amadeus
        simulated_data = []
        for hotel in hotels_data:
            simulated_data.append({
                'hotel': {
                    'name': hotel['name'],
                    'cityCode': cityCode
                },
                'offers': [{
                    'price': {
                        'total': str(hotel['price']),
                        'currency': 'EUR'
                    },
                    'checkInDate': checkInDate,
                    'checkOutDate': checkOutDate
                }]
            })
        
        return simulated_data
