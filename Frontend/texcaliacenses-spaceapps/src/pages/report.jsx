import React, { useState, useRef, useEffect } from "react";
import { useParams } from "react-router-dom";

import Header from "../components/common/header.jsx";
import HorizontalSpliter from "../components/common/spliter.jsx";
import Summary from "../components/reports/summary.jsx";
import Actions from "../components/reports/actions.jsx";

import MicIcon from "../components/icons/mic.jsx";
import SendIcon from "../components/icons/send.jsx";

export default function Report() {
  const [showChat, setShowChat] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const { city, state, country } = useParams();

  const containerRef = useRef(null);
  const textareaRef = useRef(null);
  const chatContainerRef = useRef(null);

  const action_list = [
    {
      description:
        "Regar los cultivos en las próximas 24 horas debido a la baja humedad del suelo.",
    },
    {
      description:
        "Aplicar fertilizante nitrogenado para aprovechar condiciones de humedad actuales.",
    },
    {
      description:
        "Monitorear la aparición de plagas debido a las altas temperaturas.",
    },
    {
      description:
        "Considerar la instalación de sistema de riego por goteo para optimizar el uso del agua.",
    },
  ];

  const handleChat = () => {
    setShowChat(!showChat);
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [inputMessage]);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
  };

  const handleSendMessage = () => {
    if (inputMessage.trim() !== "") {
      const newMessage = {
        text: inputMessage,
        sender: "user",
        timestamp: new Date().toISOString(),
      };
      setMessages([...messages, newMessage]);
      setInputMessage("");

      // Simulate AI response (replace with actual API call in production)
      setTimeout(() => {
        const aiResponse = {
          text: `Respuesta de AI a: "${inputMessage}"`,
          sender: "ai",
          timestamp: new Date().toISOString(),
        };
        setMessages((prevMessages) => [...prevMessages, aiResponse]);
      }, 1000);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <>
      <div className="h-[100dvh] w-[100dvw] flex flex-col">
        {/* Header */}
        <Header
          text={`Reporte para ${state}, ${country}`}
          className="mx-auto md:max-w-4xl"
        />
        <div className="h-[1.5px] bg-neutral-300 mb-3" />

        {/* --------------------Container------------------- */}
        <main
          className={`flex-grow w-full mx-auto ${
            showChat ? "md:max-w-7xl" : "md:max-w-4xl"
          }`}
        >
          <HorizontalSpliter
            initialSize={showChat ? 50 : 0}
            style={{ transition: "width 0.9s" }}
          >
            {/* ------------------------Chat logic AI------------------------------- */}
            <div
              className={`${showChat ? "block" : "hidden"} h-full w-full px-2`}
            >
              <section
                className="h-full w-full rounded-t-md flex flex-col"
                ref={containerRef}
              >
                <div
                  className="flex-1 overflow-y-auto p-4 px-8 w-full"
                  ref={chatContainerRef}
                >
                  {messages.map((message, index) => (
                    <div key={index} className={`mb-4 w-full`}>
                      <div
                        className={` w-full p-2 px-4 rounded-lg ${
                          message.sender === "user"
                            ? "bg-black text-white"
                            : "bg-neutral-100 text-black"
                        }`}
                      >
                        {message.text}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="rounded-t-md  p-4 pt-2 gap-5 bg-neutral-100 ">
                  <div className="inline-flex w-full items-center gap-2">
                    <textarea
                      ref={textareaRef}
                      value={inputMessage}
                      onChange={handleInputChange}
                      onKeyPress={handleKeyPress}
                      rows="1"
                      className="block p-2.5 w-full text-sm text-gray-900 bg-neutral-100 rounded-lg border-gray-300 resize-none focus:outline-none focus:border-transparent overflow-hidden"
                      placeholder="Your message..."
                      style={{ minHeight: "32px", maxHeight: "200px" }}
                    ></textarea>
                    <button
                      className="bg-black p-3 rounded-full flex-shrink-0"
                      onClick={handleSendMessage}
                    >
                      <SendIcon className="size-4" />
                    </button>
                  </div>
                </div>
              </section>
            </div>

            <div className="flex flex-grow h-full flex-col">
              {/* ----------------------------Summary------------------- */}
              <section className="flex-grow w-full px-2 space-y-3 overflow-y-auto">
                <Summary temperature={25} precipitation={60} humidity={80} />
                <Actions action_list={action_list} />
              </section>

              <div
                className={`w-full mx-auto md:max-w-4xl px-2 pb-10 pt-4 md:pt-10 md:pb-24
                ${showChat ? "hidden" : "block"}
                `}
              >
                <section className="w-full max-w-xs sm:max-w-sm md:max-w-lg mx-auto flex flex-col gap-3">
                  <button
                    className="w-full py-2 bg-black rounded-md text-white inline-flex items-center justify-center gap-2"
                    onClick={handleChat}
                  >
                    <MicIcon className="size-3.5" />
                    Preguntar al Asistente
                  </button>
                </section>
              </div>
            </div>
          </HorizontalSpliter>
        </main>
      </div>
    </>
  );
}
