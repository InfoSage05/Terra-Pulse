import { useState, useCallback } from "react";

export interface ChatMessageData {
  id: number;
  role: "user" | "assistant";
  text: string;
}

const CANNED_GREETING: ChatMessageData = {
  id: 0,
  role: "assistant",
  text: "Hi! I can help you find areas that match what you're looking for. (AI search coming soon — for now, try the filters on the search page!)",
};

const CANNED_RESPONSE: ChatMessageData = {
  id: -1,
  role: "assistant",
  text: "Thanks for your message! This is a preview of the TerraPulse Assistant. Real AI-powered search is coming in a future update — for now, please use the filters on the search page to narrow down properties.",
};

export function useChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessageData[]>([CANNED_GREETING]);
  const [input, setInput] = useState("");

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);
  const toggle = useCallback(() => setIsOpen(prev => !prev), []);

  const sendMessage = useCallback(() => {
    const trimmed = input.trim();
    if (!trimmed) return;

    const userMsg: ChatMessageData = {
      id: Date.now(),
      role: "user",
      text: trimmed,
    };

    setMessages(prev => [...prev, userMsg, { ...CANNED_RESPONSE, id: Date.now() + 1 }]);
    setInput("");
  }, [input]);

  return {
    isOpen,
    messages,
    input,
    open,
    close,
    toggle,
    setInput,
    sendMessage,
  };
}
