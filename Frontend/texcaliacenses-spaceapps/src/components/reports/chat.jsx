import React, { useState, useEffect } from "react";
import { GoogleGenerativeAI } from "@google/generative-ai";
import ReactMarkdown from "react-markdown";

const genAI = new GoogleGenerativeAI(
  import.meta.env.VITE_GOOGLE_GENERATIVE_AI_API_KEY
);
const model = genAI.getGenerativeModel({
  model: "gemini-1.5-flash",
});

const Avatar = ({ children, role }) => (
  <div
    className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold text-gray-500 ${
      role === "user" ? "bg-neutral-300" : "bg-neutral-200"
    }`}>
    {children}
  </div>
);

const Button = ({ children, ...props }) => (
  <button
    className="p-2 bg-neutral-700 text-white rounded-full hover:bg-neutral-900 transition-colors duration-600 hover:scale-110 flex items-center justify-center"
    {...props}>
    {children}
  </button>
);

const Card = ({ children }) => (
  <div className="w-full max-w-2xl mx-auto border rounded-lg shadow-lg bg-white overflow-hidden">
    {children}
  </div>
);

const CardHeader = ({ children }) => (
  <div className="p-4 bg-gray-50 border-b font-semibold text-lg">
    {children}
  </div>
);

const CardContent = ({ children }) => <div className="p-4">{children}</div>;

const CardFooter = ({ children }) => (
  <div className="p-4 border-t bg-gray-50">{children}</div>
);

const Input = (props) => (
  <input
    className="w-full py-2 border rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 px-4"
    {...props}
  />
);

const ScrollArea = ({ children }) => (
  <div className="h-[550px] overflow-y-auto pr-4 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
    {children}
  </div>
);

const SendIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round">
    <line
      x1="22"
      y1="2"
      x2="11"
      y2="13"></line>
    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
  </svg>
);

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [chat, setChat] = useState(null);

  const initialConfig = `Eres un asistente especializado en agricultura y horticultura, diseñado para proporcionar consejos personalizados y responder preguntas sobre prácticas agrícolas óptimas. Utilizas los siguientes datos específicos del usuario y su zona para adaptar tus recomendaciones:
  
      - Temperatura: 32°C
      - Precipitación: 60mm
      - Humedad del suelo: 80%
      - Ubicación: Morelos, México
      
      Tus responsabilidades incluyen:
      
      1. Recomendar cultivos adecuados para las condiciones climáticas y del suelo proporcionadas.
      2. Sugerir técnicas de riego eficientes basadas en la precipitación y la humedad del suelo.
      3. Proponer métodos de control de plagas y enfermedades comunes en la región.
      4. Aconsejar sobre la rotación de cultivos y la planificación de la siembra según la temporada.
      5. Ofrecer ideas para la conservación del agua y la gestión sostenible del suelo.
      6. Informar sobre las mejores prácticas de fertilización considerando el tipo de suelo y los cultivos.
      7. Proporcionar información sobre las técnicas de agricultura de precisión aplicables a la zona.
      8. Sugerir estrategias para mitigar los efectos del cambio climático en la agricultura local.
      
      Asegúrate de que tus respuestas sean:
      - Específicas para la región de Morelos y sus condiciones climáticas particulares.
      - Adaptadas a las condiciones de alta temperatura y humedad proporcionadas.
      - Prácticas y aplicables para agricultores tanto a pequeña como a gran escala.
      - Respetuosas con el medio ambiente y orientadas hacia la sostenibilidad.
      - Basadas en datos científicos y prácticas agrícolas probadas.
      
      Si se te pide información fuera de tu ámbito del sector agricola, indica que no estas diseñado para esas preguntas.`;

  useEffect(() => {
    const initializeChat = async () => {
      const newChat = model.startChat({
        history: [
          {
            role: "user",
            parts: [{ text: initialConfig }],
          },
        ],
      });
      setChat(newChat);
    };

    initializeChat();
  }, []);

  const sendMessage = async (message) => {
    if (!chat) return;

    let result = await chat.sendMessage(message);
    const responseText = await result.response.text();
    setMessages((prevMessages) => [
      ...prevMessages,
      { role: "user", text: message },
      { role: "model", text: responseText },
    ]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      sendMessage(input);
      setInput("");
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex space-x-1 items-center">
          <p>
            Habla con tu
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-teal-500 to-sky-600">
              {" "}
              Asistente Agrícola
            </span>
          </p>
          <svg
            className="text-sky-600"
            xmlns="http://www.w3.org/2000/svg"
            width="1em"
            height="1em"
            viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d="m19 1l-1.26 2.75L15 5l2.74 1.26L19 9l1.25-2.74L23 5l-2.75-1.25M9 4L6.5 9.5L1 12l5.5 2.5L9 20l2.5-5.5L17 12l-5.5-2.5M19 15l-1.26 2.74L15 19l2.74 1.25L19 23l1.25-2.75L23 19l-2.75-1.26"
            />
          </svg>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea>
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex items-start space-x-3 mb-4 ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}>
              {msg.role !== "user" && (
                <Avatar role={msg.role}>
                  {msg.role === "user" ? "U" : "🌱"}
                </Avatar>
              )}
              <div
                className={`max-w-[70%] p-3 rounded-lg ${
                  msg.role === "user"
                    ? "bg-neutral-700 text-gray-50"
                    : "bg-gray-100 text-gray-900"
                }`}>
                <p className="text-sm">
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                </p>
              </div>
              {msg.role === "user" && (
                <Avatar role={msg.role}>
                  {msg.role === "user" ? "U" : "🌱"}
                </Avatar>
              )}
            </div>
          ))}
        </ScrollArea>
      </CardContent>
      <CardFooter>
        <form
          onSubmit={handleSubmit}
          className="flex items-center space-x-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe tu pregunta sobre agricultura..."
          />
          <Button type="submit">
            <div className="flex items-center justify-center">
              <SendIcon />
            </div>
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}
