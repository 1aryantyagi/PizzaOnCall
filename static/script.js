function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

function sendMessage() {
    let inputField = document.getElementById("user-input");
    let message = inputField.value.trim();
    if (!message) return;

    let chatBox = document.getElementById("chat-box");

    // Append User Message
    let userMessageDiv = document.createElement("div");
    userMessageDiv.className = "user-message";
    userMessageDiv.textContent = message;
    chatBox.appendChild(userMessageDiv);

    inputField.value = "";

    // Show Typing Animation
    let typingDiv = document.createElement("div");
    typingDiv.className = "bot-message typing";
    typingDiv.textContent = "PizzaBot is typing...";
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
        .then(response => response.json())
        .then(data => {
            chatBox.removeChild(typingDiv); // Remove typing animation

            let botMessageDiv = document.createElement("div");
            botMessageDiv.className = "bot-message";
            botMessageDiv.textContent = data.response;
            chatBox.appendChild(botMessageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(error => console.error("Error:", error));
}
