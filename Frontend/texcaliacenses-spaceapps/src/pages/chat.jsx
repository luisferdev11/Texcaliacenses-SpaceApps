import React, { useState } from "react";

function Chat() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");

  // Función para manejar el envío de mensajes
  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    // Agregar el mensaje del usuario a la lista
    const userMessage = { sender: "user", text: inputValue };
    setMessages([...messages, userMessage]);

    //mensaje estatico de la IA
    const aiMessage_ = { sender: "ai", text: "Hola, ¿en qué puedo ayudarte?" };
    setMessages([...messages, userMessage, aiMessage_]);

    // Aquí haces la llamada a la IA para obtener la respuesta
    const response = await fetch("/api/askAI", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: inputValue }),
    });

    const data = await response.json();
    const aiMessage = { sender: "ai", text: data.response };

    // Agregar la respuesta de la IA a la lista
    setMessages([...messages, userMessage, aiMessage]);

    // Limpiar el input
    setInputValue("");
  };

  return (
    <div>
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={msg.sender === "user" ? "user-message" : "ai-message"}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="Escribe un mensaje..."
      />
      <button onClick={handleSendMessage}>Enviar</button>
    </div>
  );
}

export default Chat;
