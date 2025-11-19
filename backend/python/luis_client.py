import requests
import azure_config

class CluClient:
    def __init__(self):
        self.project_name = azure_config.CLU_PROJECT_NAME
        self.deployment_name = azure_config.CLU_DEPLOYMENT_NAME
        self.endpoint = azure_config.CLU_ENDPOINT
        self.key = azure_config.CLU_KEY

    def recognize(self, text, language='pt-br'):
        if not self.project_name or not self.endpoint or not self.key:
            return {'error': 'CLU credentials not set'}
        
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
        
        r = requests.post(url, json=payload, headers=headers)
        return r.json()
