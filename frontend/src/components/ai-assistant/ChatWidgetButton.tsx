import React from "react";
import { ChatWidgetPanel } from "./ChatWidgetPanel";
import { useChatWidget } from "./useChatWidget";

export function ChatWidgetButton() {
  const widget = useChatWidget();

  return (
    <>
      <button
        onClick={widget.toggle}
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full shadow-xl flex items-center justify-center transition-all duration-200 hover:scale-110 ${
          widget.isOpen
            ? "bg-gray-800 text-white"
            : "bg-indigo-600 text-white hover:bg-indigo-700"
        }`}
        aria-label="Open AI assistant"
      >
        {widget.isOpen ? (
          <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        ) : (
          <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" />
          </svg>
        )}
      </button>
      <ChatWidgetPanel widget={widget} />
    </>
  );
}
