// Debug script para testar chatbot diretamente no navegador
console.log('=== TESTE CHATBOT DEBUG ===');

// Verificar se elementos existem
const elements = {
    toggle: document.getElementById('chatbot-toggle'),
    window: document.getElementById('chatbot-window'),
    messages: document.getElementById('chatbot-messages'),
    input: document.getElementById('chatbot-input'),
    send: document.getElementById('chatbot-send')
};

console.log('Elementos encontrados:');
Object.keys(elements).forEach(key => {
    console.log(`${key}: ${elements[key] ? 'OK' : 'MISSING'}`);
});

// Verificar se o CSS está aplicado
if (elements.toggle) {
    const styles = window.getComputedStyle(elements.toggle);
    console.log('Estilos do botão toggle:');
    console.log(`position: ${styles.position}`);
    console.log(`bottom: ${styles.bottom}`);
    console.log(`right: ${styles.right}`);
    console.log(`z-index: ${styles.zIndex}`);
    console.log(`display: ${styles.display}`);
    console.log(`visibility: ${styles.visibility}`);
}

// Testar evento de clique
if (elements.toggle) {
    console.log('Adicionando evento de teste ao botão...');
    elements.toggle.addEventListener('click', function() {
        console.log('CLIQUE DETECTADO NO BOTÃO!');
        if (elements.window) {
            const isHidden = elements.window.style.display === 'none';
            elements.window.style.display = isHidden ? 'flex' : 'none';
            console.log(`Janela do chat ${isHidden ? 'aberta' : 'fechada'}`);
        }
    });
}

// Testar API do chatbot
async function testChatbotAPI() {
    console.log('Testando API do chatbot...');
    try {
        const response = await fetch('/chatbot/api/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: 'teste de conexão' })
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('API funcionando:', data);
        } else {
            console.log('Erro na API:', response.status);
        }
    } catch (error) {
        console.error('Erro ao testar API:', error);
    }
}

testChatbotAPI();

console.log('=== FIM DO TESTE ===');