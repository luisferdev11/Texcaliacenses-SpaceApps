export default function Footer({ className }) {
  const currentYear = new Date().getFullYear();
  return (
    <footer className={`w-full pb-4 pt-2.5 ${className}`}>
      <div className="mb-2 flex flex-row justify-center text-neutral-500 text-sm gap-4">
        <a href="">Privacidad</a>
        <a href="">Términos de uso</a>
        <a href="">Contacto</a>
      </div>
      <p className="text-center text-neutral-500 text-xs">
        © {currentYear} Asistente Agrícola. Todos los derechos reservados.
      </p>
    </footer>
  );
}
