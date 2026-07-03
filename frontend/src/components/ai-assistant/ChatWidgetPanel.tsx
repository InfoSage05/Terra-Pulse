import React, { useRef, useEffect } from "react";
import { X, Send } from "lucide-react";
import { ChatMessage } from "./ChatMessage";
import { useChatWidget } from "./useChatWidget";

interface ChatWidgetPanelProps {
  widget: ReturnType<typeof useChatWidget>;
}

export function ChatWidgetPanel({ widget }: ChatWidgetPanelProps) {
  const { isOpen, close, messages, input, setInput, sendMessage } = widget;
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isOpen]);

  if (!isOpen) return null;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="fixed bottom-24 right-6 z-50 w-[400px] h-[560px] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden animate-in">
      {/* Header */}
      <div className="px-4 py-3 bg-indigo-600 text-white flex items-center justify-between">
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" />
          </svg>
          <span className="font-semibold text-sm">TerraPulse Assistant</span>
        </div>
        <button onClick={close} className="p-1 hover:bg-indigo-500 rounded-md transition-colors">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Preview badge */}
      <div className="px-4 py-1.5 bg-amber-50 border-b border-amber-100 text-xs text-amber-700 text-center font-medium">
        Preview — AI search coming soon
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-3 bg-gray-50">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
      </div>

      {/* Input */}
      <div className="px-3 py-3 border-t border-gray-200 bg-white flex items-center gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about areas, prices, safety..."
          className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400"
        />
        <button
          onClick={sendMessage}
          disabled={!input.trim()}
          className="p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-40 transition-colors"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
