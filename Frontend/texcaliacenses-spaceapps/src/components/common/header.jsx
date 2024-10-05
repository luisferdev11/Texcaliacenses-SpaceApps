import Logo from "../icons/logo.jsx";

export default function Header({ text, className }) {
  return (
    <header
      className={`relative w-full flex items-center justify-center py-2.5 ${className}`}
    >
      <div className="absolute left-2">
        <Logo className="size-7" />
      </div>
      <h1 className="font-extrabold text-xl">{text}</h1>
    </header>
  );
}
