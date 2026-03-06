"use client";

import { useEffect, useRef, useState } from "react";
import { sendChatMessage, type ChatMessage } from "@/lib/api";

export function ChatAssistant() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, open]);

  const send = async () => {
    const msg = input.trim();
    if (!msg || loading) return;
    setInput("");
    const userMsg: ChatMessage = { role: "user", content: msg };
    setHistory((h) => [...h, userMsg]);
    setLoading(true);
    try {
      const { reply } = await sendChatMessage(msg, history);
      setHistory((h) => [...h, { role: "assistant", content: reply }]);
    } catch {
      setHistory((h) => [
        ...h,
        { role: "assistant", content: "Sorry, something went wrong. Is the backend running?" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-[#282828] text-white shadow-lg hover:bg-black transition-colors"
        aria-label="Toggle chat"
      >
        {open ? (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-3 3-3-3z" />
          </svg>
        )}
      </button>

      {/* Chat panel */}
      {open && (
        <div className="fixed bottom-24 right-6 z-50 flex w-[360px] max-w-[calc(100vw-24px)] flex-col rounded-2xl border border-[#e7e7e7] bg-white shadow-xl">
          {/* Header */}
          <div className="flex items-center gap-2 rounded-t-2xl bg-[#282828] px-4 py-3 text-white">
            <div className="h-2 w-2 rounded-full bg-[#d2b777]" />
            <span className="text-sm font-semibold">Ask about products</span>
            <span className="ml-auto text-xs text-gray-400">Powered by Claude</span>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 max-h-[400px] min-h-[200px]">
            {history.length === 0 && (
              <div className="space-y-2">
                <p className="text-xs text-gray-400">Ask anything about stored products, e.g.:</p>
                {[
                  "What was the price of Anveshan A2 cow ghee per kg on 5th March?",
                  "Which ghee has the highest quality score?",
                  "Compare prices of cold pressed oils",
                  "What certifications does Two Brothers honey have?",
                ].map((ex) => (
                  <button
                    key={ex}
                    onClick={() => { setInput(ex); }}
                    className="block w-full rounded-lg border border-[#e7e7e7] px-3 py-1.5 text-left text-xs text-gray-600 hover:bg-[#f6edd9] transition-colors"
                  >
                    {ex}
                  </button>
                ))}
              </div>
            )}
            {history.map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm whitespace-pre-wrap ${
                    m.role === "user"
                      ? "bg-[#282828] text-white rounded-br-sm"
                      : "bg-[#f6edd9] text-[#282828] rounded-bl-sm"
                  }`}
                >
                  {m.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="rounded-2xl rounded-bl-sm bg-[#f6edd9] px-3 py-2 text-sm text-gray-400">
                  <span className="animate-pulse">Thinking…</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-[#e7e7e7] p-3 flex gap-2">
            <input
              className="flex-1 rounded-lg border border-[#e7e7e7] px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#d2b777]"
              placeholder="Ask a question…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
              disabled={loading}
            />
            <button
              onClick={send}
              disabled={loading || !input.trim()}
              className="rounded-lg bg-[#282828] px-3 py-2 text-white text-sm hover:bg-black disabled:opacity-50 transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
}
