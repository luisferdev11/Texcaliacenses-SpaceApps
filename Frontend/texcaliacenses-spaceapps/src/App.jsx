import React, { useState } from "react";

import Header from "./components/common/header.jsx";
import Footer from "./components/common/footer.jsx";

import SearchIcon from "./components/icons/search.jsx";
import LocationIcon from "./components/icons/location.jsx";

function App() {
  const [location, setLocation] = useState(null);
  const [error, setError] = useState(null);

  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
          console.log("Ubicación obtenida:", location);
          setError(null);
        },
        (error) => {
          setError("No se pudo obtener la ubicación.");
          console.error("No se pudo obtener la ubicación.", error);
          setLocation(null);
        }
      );
    } else {
      setError("La geolocalización no es soportada por este navegador.");
      console.error("La geolocalización no es soportada por este navegador.");
    }
  };

  return (
    <>
      <div className="h-[100dvh] w-[100dvw] flex flex-col">
        <Header text="Asistente Agrícola" className="mx-auto md:max-w-4xl" />
        <div className="h-[1.5px] bg-neutral-300"></div>

        {/* Main content */}
        <main className="flex-grow flex flex-col justify-center w-full mx-auto md:max-w-4xl gap-5">
          <h2 className="font-bold text-2xl md:text-3xl text-pretty text-center tracking-tight px-2">
            ¡Bienvenido! Obtén recomendaciones agrícolas basadas en tu
            ubicación.
          </h2>

          <section className="w-full max-w-xs sm:max-w-sm md:max-w-lg mx-auto flex flex-col gap-3">
            <button
              className="w-full py-2 bg-black rounded-md text-white inline-flex items-center justify-center gap-2"
              onClick={handleGetLocation}
            >
              <LocationIcon className="size-3.5" />
              Usar mi ubicación actual
            </button>

            <div className="w-full flex flex-row items-center">
              <div className="flex-1 h-[1px] bg-neutral-300"></div>
              <div className="px-4 text-neutral-400"> ó </div>
              <div className="flex-1 h-[1px] bg-neutral-300"></div>
            </div>

            <form className="flex flex-col sm:flex-row gap-2">
              <input
                type="text"
                id="location"
                name="location"
                placeholder="Ingresa tu dirección o coordenadas"
                className="flex-1 p-2 border border-neutral-300 rounded-md"
              />
              <button className="py-2 bg-black inline-flex items-center  gap-2 px-3 rounded-md text-white justify-center">
                <SearchIcon className="size-3.5" />
                Buscar
              </button>
            </form>
          </section>
        </main>

        <Footer className="mx-auto md:max-w-4xl" />
      </div>
    </>
  );
}

export default App;
