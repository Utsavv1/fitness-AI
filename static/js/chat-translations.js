// Function to translate the chat interface
function translateChatInterface(lang) {
    document.title = translations[lang].chatTitle;
    document.querySelector('.header-subtitle').textContent = translations[lang].chatSubtitle;
    document.querySelector('.message-input').placeholder = translations[lang].messagePlaceholder;
    document.querySelector('.send-button').textContent = translations[lang].sendButton;
    document.querySelector('.back-button').textContent = translations[lang].backButton;
}

// Function to translate a message
async function translateMessage(text, targetLang) {
    if (targetLang === 'en') return text; // No translation needed for English

    try {
        const response = await fetch('https://api.mymemory.translated.net/get', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            params: {
                q: text,
                langpair: `en|${targetLang}`
            }
        });
        const data = await response.json();
        return data.responseData.translatedText;
    } catch (error) {
        console.error('Translation error:', error);
        return text; // Return original text if translation fails
    }
}

// Function to add a message to the chat
async function addMessage(content, isUser = false) {
    const lang = localStorage.getItem('selectedLanguage') || 'en';
    const messageContainer = document.createElement('div');
    messageContainer.className = `message-container ${isUser ? 'user' : 'assistant'}`;
    
    const prefix = isUser ? translations[lang].userPrefix : translations[lang].assistantPrefix;
    
    // Translate the message if not in English
    let translatedContent = content;
    if (lang !== 'en') {
        translatedContent = await translateMessage(content, lang);
    }
    
    messageContainer.innerHTML = `
        <div class="message-label">${prefix}</div>
        <div class="chat-message ${isUser ? 'user' : 'assistant'}">
            <div class="content">${translatedContent}</div>
        </div>
    `;
    
    document.querySelector('.chat-messages').appendChild(messageContainer);
    messageContainer.scrollIntoView({ behavior: 'smooth' });
}

// Initialize chat interface with saved language
document.addEventListener('DOMContentLoaded', () => {
    const savedLanguage = localStorage.getItem('selectedLanguage') || 'en';
    translateChatInterface(savedLanguage);
}); 