from azure.cosmos import CosmosClient, PartitionKey
import azure_config
import uuid
from datetime import datetime

class ConversationStore:
    def __init__(self):
        if not azure_config.COSMOS_ENDPOINT or not azure_config.COSMOS_KEY:
            self.client = None
            return
        self.client = CosmosClient(azure_config.COSMOS_ENDPOINT, credential=azure_config.COSMOS_KEY)
        self.db = self.client.create_database_if_not_exists(id=azure_config.COSMOS_DATABASE)
        self.container = self.db.create_container_if_not_exists(id=azure_config.COSMOS_CONTAINER, partition_key=PartitionKey(path="/userId"))

    def save_message(self, userId, message, role, sentiment=None, metadata=None):
        if not self.client:
            return None
        item = {
            'id': str(uuid.uuid4()),
            'userId': userId,
            'role': role,
            'message': message,
            'sentiment': sentiment,
            'metadata': metadata,
            'timestamp': datetime.utcnow().isoformat()
        }
        return self.container.create_item(body=item)
    
    def get_conversation_context(self, userId, limit=10):
        """Recupera as últimas mensagens da conversa para contexto"""
        if not self.client:
            return []
        
        try:
            query = f"SELECT TOP {limit} * FROM c WHERE c.userId = @userId ORDER BY c.timestamp DESC"
            items = list(self.container.query_items(
                query=query,
                parameters=[{"name": "@userId", "value": userId}],
                enable_cross_partition_query=True
            ))
            # Retornar em ordem cronológica (mais antiga primeiro)
            return list(reversed(items))
        except Exception as e:
            print(f"Erro ao buscar contexto: {e}")
            return []

