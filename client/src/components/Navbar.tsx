import nuLogo from "../assets/nu-logo.svg";

export default function Navbar() {
    return (
        <header className="w-full shrink-0">
            <div className="h-14 w-full bg-brand-navy flex items-center px-6">
                <img src={nuLogo} alt="National University" className="mr-3 h-8 w-8 object-contain" />
                <span className="text-brand-gold font-bold text-xl tracking-wide">
                    NASAN
                </span>
            </div>
            <div className="h-1 w-full bg-brand-yellow" />
        </header>
    );
}