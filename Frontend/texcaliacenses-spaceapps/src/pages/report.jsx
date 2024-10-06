import React from "react";
import { useParams } from "react-router-dom";

import Header from "../components/common/header.jsx";
import Footer from "../components/common/footer.jsx";
import Summary from "../components/reports/summary.jsx";
import Actions from "../components/reports/actions.jsx";

import MicIcon from "../components/icons/mic.jsx";

export default function Report() {
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

  return (
    <>
      <div className="h-[100dvh] w-[100dvw] flex flex-col">
        <Header
          text={`Reporte para ${state}, ${country}`}
          className="mx-auto md:max-w-4xl"
        />
        <div className="h-[1.5px] bg-neutral-300 mb-3" />

        <main className="flex-grow w-full mx-auto md:max-w-4xl px-2 space-y-3 overflow-y-auto">
          <Summary temperature={25} precipitation={60} humidity={80} />
          <Actions action_list={action_list} />
        </main>

        <footer className="w-full mx-auto md:max-w-4xl px-2 pb-10 pt-4 md:pt-10 md:pb-24">
          <section className="w-full max-w-xs sm:max-w-sm md:max-w-lg mx-auto flex flex-col gap-3">
            <button className="w-full py-2 bg-black rounded-md text-white inline-flex items-center justify-center gap-2">
              <MicIcon className="size-3.5" />
              Preguntar al Asistente
            </button>
          </section>
        </footer>
      </div>
    </>
  );
}
