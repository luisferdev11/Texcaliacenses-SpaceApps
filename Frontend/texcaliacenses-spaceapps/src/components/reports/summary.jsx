import SunIcon from "../icons/sun";
import HumidityIcon from "../icons/humidity";
import PrecipitationIcon from "../icons/precipitation";

export default function Summary({ temperature, precipitation, humidity }) {
  return (
    <>
      <article className="w-full rounded-md border-[1.5px] border-neutral-300 px-4 pt-2 pb-3">
        <h2 className="text-xl font-semibold mb-5">Resumen General</h2>
        <section className="flex md:flex-row flex-col text-sm gap-y-2">
          <div className="flex-1 inline-flex items-center gap-2">
            <SunIcon className="size-6" />
            <div>
              <h4>Temperatura promedio</h4>
              <p className="font-extrabold text-lg ">{temperature}°C</p>
            </div>
          </div>
          <div className="flex-1 inline-flex items-center gap-2">
            <PrecipitationIcon className="size-6 " />
            <div>
              <h4>Precipitación en los últimos 7 días</h4>
              <p className="font-extrabold text-lg ">{precipitation}mm</p>
            </div>
          </div>
          <div className="flex-1 inline-flex items-center gap-2">
            <HumidityIcon className="size-6" />
            <div>
              <h4>Humedad del suelo</h4>
              <p className="font-extrabold text-lg ">{humidity}%</p>
            </div>
          </div>
        </section>
      </article>
    </>
  );
}
