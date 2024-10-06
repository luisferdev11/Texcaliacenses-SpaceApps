import React, { useState } from "react";
import { useParams } from "react-router-dom";

import Header from "../components/common/header.jsx";
import HorizontalSpliter from "../components/common/spliter.jsx";
import Summary from "../components/reports/summary.jsx";
import Actions from "../components/reports/actions.jsx";

import MicIcon from "../components/icons/mic.jsx";
import Chat from "../components/reports/chat.jsx";

export default function Report() {
  const [showChat, setShowChat] = useState(false);
  const { city, state, country } = useParams();

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
          }`}>
          <HorizontalSpliter
            initialSize={showChat ? 50 : 0}
            style={{ transition: "width 0.9s" }}>
            {/* ------------------------Chat logic AI------------------------------- */}
            <div
              className={`${showChat ? "block" : "hidden"} h-full w-full px-2`}>
              <section className=" w-full">
                <Chat />
              </section>
            </div>

            <div className="flex flex-grow h-full flex-col">
              {/* ----------------------------Summary------------------- */}
              <section className="flex-grow w-full px-2 space-y-3 overflow-y-auto">
                <Summary
                  temperature={25}
                  precipitation={60}
                  humidity={80}
                />
                <Actions action_list={action_list} />
              </section>

              <div
                className={`w-full mx-auto md:max-w-4xl px-2 pb-10 pt-4 md:pt-10 md:pb-24
                ${showChat ? "hidden" : "block"}
                `}>
                <section className="w-full max-w-xs sm:max-w-sm md:max-w-lg mx-auto flex flex-col gap-3">
                  <button
                    className="w-full py-2 bg-black rounded-md text-white inline-flex items-center justify-center gap-2"
                    onClick={handleChat}>
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
