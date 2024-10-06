export default function Actions({ action_list }) {
  return (
    <article className="w-full rounded-md border-[1.5px] border-neutral-300 px-4 py-4">
      <h2 className="text-xl font-semibold mb-6 md:mb-10">
        Acciones recomendadas
      </h2>
      <section className="flex flex-col gap-1">
        <ul className="list-disc list-inside text-sm text-pretty space-y-1 px-2">
          {action_list.map((action, index) => (
            <li key={index} className="text-base">
              {action.description}
            </li>
          ))}
        </ul>
      </section>
    </article>
  );
}
