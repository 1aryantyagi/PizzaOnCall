document.addEventListener('DOMContentLoaded', () => {
    loadMenu();
    setInterval(updateCart, 3000);
});

async function loadMenu() {
    try {
        const response = await fetch('/menu');
        const menu = await response.json();
        const menuContainer = document.getElementById('menuItems');

        menuContainer.innerHTML = `
            <h3>🍕 Pizzas</h3>
            ${menu.pizzas}
            <h3>🧀 Customizations</h3>
            ${menu.customizations}
        `;
    } catch (error) {
        console.error('Error loading menu:', error);
    }
}

async function updateCart() {
    try {
        const response = await fetch('/cart');
        const cart = await response.json();

        document.getElementById('cartItems').textContent = cart.items;
        document.getElementById('cartTotal').textContent = cart.total;
    } catch (error) {
        console.error('Error updating cart:', error);
    }
}

async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    if (!message) return;

    // Add user message
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML += `
        <div class="message user-message">
            👤 ${message}
        </div>
    `;

    try {
        const response = await fetch('/process_message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        chatMessages.innerHTML += `
            <div class="message bot-message">
                🤖 ${data.response}
            </div>
        `;

        // Scroll to bottom and clear input
        chatMessages.scrollTop = chatMessages.scrollHeight;
        input.value = '';
    } catch (error) {
        console.error('Error:', error);
        chatMessages.innerHTML += `
            <div class="message bot-message error">
                ❌ Oops! Something went wrong. Please try again.
            </div>
        `;
    }
}

// Handle Enter key
document.getElementById('userInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});