from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import azure_config

class TextAnalytics:
    def __init__(self):
        if not azure_config.TEXT_ANALYTICS_ENDPOINT or not azure_config.TEXT_ANALYTICS_KEY:
            self.client = None
            return
        self.client = TextAnalyticsClient(endpoint=azure_config.TEXT_ANALYTICS_ENDPOINT, credential=AzureKeyCredential(azure_config.TEXT_ANALYTICS_KEY))

    def analyze_sentiment(self, text):
        if not self.client:
            return None
        try:
            response = self.client.analyze_sentiment([text])[0]
            return {
                'sentiment': response.sentiment,
                'scores': {
                    'positive': response.confidence_scores.positive,
                    'neutral': response.confidence_scores.neutral,
                    'negative': response.confidence_scores.negative
                }
            }
        except Exception as e:
            return {'error': str(e)}
