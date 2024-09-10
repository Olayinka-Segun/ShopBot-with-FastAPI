document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const chatBox = document.getElementById("chat-box");
    const userMessageInput = document.getElementById("user-message");

    chatForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        
        const userMessage = userMessageInput.value;
        if (userMessage.trim() === "") return;

        // Add user message to chat
        chatBox.innerHTML += `<div>User: ${userMessage}</div>`;
        userMessageInput.value = "";

        try {
            // Send message to the server
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: userMessage }),
            });

            if (!response.ok) throw new Error("Chat request failed");

            const data = await response.json();
            // Add bot response to chat
            chatBox.innerHTML += `<div>ShopBot: ${data.response}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the bottom
        } catch (error) {
            chatBox.innerHTML += `<div>ShopBot: Sorry, there was an error.</div>`;
        }
    });
});
