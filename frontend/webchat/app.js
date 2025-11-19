// Chat Application
const API_URL = 'https://chatbotviagem-eva3g9gxe7edbxde.eastus2-01.azurewebsites.net/api/chat';
const messagesContainer = document.getElementById('chat-messages');
const inputField = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const newChatBtn = document.getElementById('new-chat-btn');

let userId = 'user-' + Math.random().toString(36).substr(2, 9);

// Start new conversation
function startNewConversation() {
  // Generate new userId to start fresh (preserves old history in Cosmos DB)
  userId = 'user-' + Math.random().toString(36).substr(2, 9);
  
  // Clear UI
  messagesContainer.innerHTML = '';
  
  // Show initial greeting
  addMessage('Olá! 👋 Sou seu assistente de viagens. Posso ajudar com:\n\n✈️ Consultar, comprar ou cancelar voos\n🏨 Reservar, consultar ou cancelar hotéis\n\nComo posso ajudá-lo hoje?');
  
  inputField.focus();
}


// Convert markdown to HTML
function parseMarkdown(text) {
  // Bold: **text** ou __text__
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  text = text.replace(/__(.+?)__/g, '<strong>$1</strong>');
  
  // Italic: *text* ou _text_
  text = text.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');
  text = text.replace(/(?<!_)_([^_]+)_(?!_)/g, '<em>$1</em>');
  
  // Preservar quebras de linha
  text = text.replace(/\n/g, '<br>');
  
  return text;
}

// Add message to chat
function addMessage(text, isUser = false) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
  
  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.textContent = isUser ? '👤' : '🤖';
  
  const content = document.createElement('div');
  content.className = 'message-content';
  
  // Bot messages: render markdown as HTML
  if (!isUser) {
    content.innerHTML = parseMarkdown(text);
  } else {
    // User messages: plain text
    content.style.whiteSpace = 'pre-wrap';
    content.textContent = text;
  }
  
  messageDiv.appendChild(avatar);
  messageDiv.appendChild(content);
  messagesContainer.appendChild(messageDiv);
  
  // Scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Show typing indicator
function showTyping() {
  const typingDiv = document.createElement('div');
  typingDiv.className = 'message bot';
  typingDiv.id = 'typing-indicator';
  
  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.textContent = '🤖';
  
  const typingContent = document.createElement('div');
  typingContent.className = 'message-content';
  typingContent.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
  
  typingDiv.appendChild(avatar);
  typingDiv.appendChild(typingContent);
  messagesContainer.appendChild(typingDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Remove typing indicator
function hideTyping() {
  const typing = document.getElementById('typing-indicator');
  if (typing) typing.remove();
}

// Send message to backend
async function sendMessage() {
  const text = inputField.value.trim();
  if (!text) return;
  
  // Add user message
  addMessage(text, true);
  inputField.value = '';
  sendBtn.disabled = true;
  
  // Show typing
  showTyping();
  
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId, message: text })  // Backend espera 'message'
    });
    
    const data = await response.json();
    hideTyping();
    
    // Add bot response - backend retorna 'response'
    addMessage(data.response || data.text || 'Desculpe, não consegui processar sua mensagem.');
  } catch (error) {
    hideTyping();
    addMessage('❌ Erro ao conectar com o servidor. Certifique-se de que o backend está rodando em ' + API_URL);
    console.error('Error:', error);
  } finally {
    sendBtn.disabled = false;
    inputField.focus();
  }
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);
inputField.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendMessage();
});
newChatBtn.addEventListener('click', startNewConversation);

// Initial greeting
window.addEventListener('load', () => {
  addMessage('Olá! 👋 Sou seu assistente de viagens. Posso ajudar com:\n\n✈️ Consultar, comprar ou cancelar voos\n🏨 Reservar, consultar ou cancelar hotéis\n\nComo posso ajudá-lo hoje?');
  inputField.focus();
});
