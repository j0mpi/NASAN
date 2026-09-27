import { useState, type FormEvent } from "react";
import { RefreshCw, Send } from "lucide-react";

interface SearchBarProps {
    onSubmit: (message: string) => void;
    isActive: boolean;
    showNewChat: boolean;
}

export default function SearchBar({ onSubmit, isActive, showNewChat }: SearchBarProps) {
    const [value, setValue] = useState("");

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        const trimmed = value.trim();
        if (!trimmed) return;
        onSubmit(trimmed);
        setValue("");
    };

    if (showNewChat) {
        return (
            <button
                type="button"
                onClick={() => window.location.reload()}
                className="mx-auto flex items-center gap-2 rounded-full bg-brand-yellow px-5 py-2.5 text-sm font-semibold text-[#333E89] shadow-md transition hover:brightness-95"
            >
                Start a new chat
                <RefreshCw className="h-4 w-4" />
            </button>
        );
    }

    return (
        <form onSubmit={handleSubmit} className="w-full">
            <div
                className={`flex items-center gap-3 rounded-full border border-gray-200 shadow-md bg-white transition-all duration-500 ease-in-out ${isActive ? "px-5 py-2.5" : "px-5 py-3"
                    }`}
            >
                <input
                    type="text"
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    placeholder={
                        isActive
                            ? "Ask another question..."
                            : "Welcome to NASAN. How can we help you find the right scholarship?"
                    }
                    className="flex-1 outline-none text-sm text-gray-700 placeholder:text-gray-400 bg-transparent"
                />
                <button
                    type="submit"
                    className="flex items-center gap-2 bg-brand-yellow hover:brightness-95 transition rounded-full px-4 py-2 text-sm font-semibold text-[#333E89] shrink-0 cursor-pointer"
                >
                    Send
                    <Send className="w-4 h-4" />
                </button>
            </div>
        </form>
    );
}