from azure.cosmos import CosmosClient, PartitionKey
import azure_config
import uuid
from datetime import datetime

class ConversationStore:
    def __init__(self):
        try:
            if not azure_config.COSMOS_ENDPOINT or not azure_config.COSMOS_KEY:
                self.client = None
                print('[WARN] Cosmos DB não configurado', flush=True)
                return
            
            self.client = CosmosClient(azure_config.COSMOS_ENDPOINT, credential=azure_config.COSMOS_KEY)
            self.db = self.client.create_database_if_not_exists(id=azure_config.COSMOS_DATABASE)
            self.container = self.db.create_container_if_not_exists(
                id=azure_config.COSMOS_CONTAINER, 
                partition_key=PartitionKey(path="/userId")
            )
            print('[INFO] Cosmos DB conectado', flush=True)
        except Exception as e:
            print(f'[ERROR] Cosmos DB init failed: {str(e)}', flush=True)
            self.client = None

    def save_message(self, userId, message, role, sentiment=None, metadata=None):
        if not self.client:
            return None
        
        try:
            item = {
                'id': str(uuid.uuid4()),
                'userId': userId,
                'role': role,
                'message': message[:500],  # Limitar tamanho
                'sentiment': sentiment,
                'metadata': metadata,
                'timestamp': datetime.utcnow().isoformat()
            }
            return self.container.create_item(body=item)
        except Exception as e:
            print(f'[ERROR] Cosmos save failed: {str(e)[:100]}', flush=True)
            return None
    
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
            return list(reversed(items))
        except Exception as e:
            print(f'[ERROR] Cosmos query failed: {str(e)[:100]}', flush=True)
            return []

