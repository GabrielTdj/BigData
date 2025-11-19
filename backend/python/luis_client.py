import requests
import azure_config

class CluClient:
    def __init__(self):
        self.project_name = azure_config.CLU_PROJECT_NAME
        self.deployment_name = azure_config.CLU_DEPLOYMENT_NAME
        self.endpoint = azure_config.CLU_ENDPOINT
        self.key = azure_config.CLU_KEY
        self.enabled = bool(self.project_name and self.endpoint and self.key)

    def recognize(self, text, language='pt-br'):
        if not self.enabled:
            print('[WARN] CLU não configurado, usando fallback', flush=True)
            return {'error': 'CLU credentials not set'}
        
        try:
            url = f"{self.endpoint}/language/:analyze-conversations?api-version=2022-10-01-preview"
            
            payload = {
                "kind": "Conversation",
                "analysisInput": {
                    "conversationItem": {
                        "id": "1",
                        "participantId": "user",
                        "language": language,
                        "text": text
                    }
                },
                "parameters": {
                    "projectName": self.project_name,
                    "deploymentName": self.deployment_name,
                    "stringIndexType": "TextElement_V8"
                }
            }
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.key,
                'Content-Type': 'application/json'
            }
            
            r = requests.post(url, json=payload, headers=headers, timeout=10)
            r.raise_for_status()
            return r.json()
            
        except requests.exceptions.Timeout:
            return {'error': 'CLU timeout'}
        except requests.exceptions.RequestException as e:
            print(f'[ERROR] CLU request failed: {str(e)}', flush=True)
            return {'error': f'CLU error: {str(e)[:100]}'}
