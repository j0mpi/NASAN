import { useEffect, useRef, useState } from "react";
import Navbar from "./components/Navbar";
import SearchBar from "./components/SearchBar";
import ScholarshipCard from "./components/ScholarshipCard";
import type { ChatMessage, ChatRequestPayload, ScholarshipResult } from "./types";

const API_ENDPOINT = "/api/chat";

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isActive, setIsActive] = useState(false);
  const [context, setContext] = useState<ChatRequestPayload["context"]>({});
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const hasNoScholarshipFallback = messages.some(
    (message) =>
      message.role === "assistant" &&
      message.content.startsWith("I couldn't find a scholarship that matches"),
  );

  useEffect(() => {
    const frame = requestAnimationFrame(() => {
      messagesContainerRef.current?.scrollTo({
        top: messagesContainerRef.current.scrollHeight,
        behavior: "smooth",
      });
    });
    return () => cancelAnimationFrame(frame);
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!isActive) setIsActive(true);

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const payload: ChatRequestPayload = { message: text, context };
      const response = await fetch(API_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data: {
        reply: string;
        results: ScholarshipResult[];
        entities?: ChatRequestPayload["context"];
        options?: string[];
      } = await response.json();
      if (data.entities) setContext((previous) => ({ ...previous, ...data.entities }));

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.reply,
        result: data.results,
        options: data.options,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "Sorry, we couldn't find your scholarship matches right now. Please try again.",
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-white">
      <Navbar />

      <div className="flex-1 relative overflow-hidden">
        <div
          ref={messagesContainerRef}
          className={`absolute inset-0 overflow-y-auto px-4 py-6 transition-opacity duration-500 ease-in-out ${isActive ? "opacity-100" : "opacity-0 pointer-events-none"
            }`}
        >
          <div className="max-w-2xl mx-auto space-y-4 pb-20">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`chat-message-in flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "user" ? (
                  <div className="bg-brand-navy text-white rounded-2xl px-4 py-2 max-w-md text-sm">
                    {msg.content}
                  </div>
                ) : msg.result && msg.result.length > 0 ? (
                  <div className="space-y-2">
                    <p className="text-sm text-gray-600">{msg.content}</p>
                    {msg.result.map((result) => (
                      <ScholarshipCard
                        key={result["Scholarship Name"]}
                        result={result}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="max-w-lg space-y-3">
                    <div className="bg-gray-100 text-gray-700 rounded-2xl px-4 py-2 text-sm">
                      {msg.content}
                    </div>
                    {msg.options && msg.options.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {msg.options.map((option) => (
                          <button
                            key={option}
                            type="button"
                            onClick={() => sendMessage(option)}
                            className="rounded-full border border-brand-navy px-3 py-1.5 text-xs font-medium text-brand-navy transition hover:bg-brand-navy hover:text-white"
                          >
                            {option}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div
          className="absolute left-1/2 w-full max-w-2xl px-4 transition-all duration-500 ease-in-out"
          style={{
            top: isActive ? "calc(100% - 72px)" : "50%",
            transform: isActive ? "translate(-50%, 0)" : "translate(-50%, -50%)",
          }}
        >
          <SearchBar
            onSubmit={sendMessage}
            isActive={isActive}
            showNewChat={hasNoScholarshipFallback}
          />
        </div>
      </div>
    </div>
  );
}