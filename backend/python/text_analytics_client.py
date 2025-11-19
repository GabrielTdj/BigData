from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import azure_config

class TextAnalytics:
    def __init__(self):
        try:
            if not azure_config.TEXT_ANALYTICS_ENDPOINT or not azure_config.TEXT_ANALYTICS_KEY:
                self.client = None
                print('[WARN] Text Analytics não configurado', flush=True)
                return
            
            self.client = TextAnalyticsClient(
                endpoint=azure_config.TEXT_ANALYTICS_ENDPOINT, 
                credential=AzureKeyCredential(azure_config.TEXT_ANALYTICS_KEY)
            )
            print('[INFO] Text Analytics conectado', flush=True)
        except Exception as e:
            print(f'[ERROR] Text Analytics init failed: {str(e)}', flush=True)
            self.client = None

    def analyze_sentiment(self, text):
        if not self.client:
            return None
        
        try:
            response = self.client.analyze_sentiment([text[:500]])[0]  # Limitar tamanho
            return {
                'sentiment': response.sentiment,
                'scores': {
                    'positive': response.confidence_scores.positive,
                    'neutral': response.confidence_scores.neutral,
                    'negative': response.confidence_scores.negative
                }
            }
        except Exception as e:
            print(f'[ERROR] Sentiment analysis failed: {str(e)[:100]}', flush=True)
            return None
