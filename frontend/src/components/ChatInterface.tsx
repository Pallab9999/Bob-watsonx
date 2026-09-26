import React, { useState, useRef, useEffect, useCallback } from "react";
import { useLocation } from "react-router-dom";
import { api } from "../services/api";
import type { ChatMessage, OnboardingPlan } from "../types";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface LocationState {
  plan?: OnboardingPlan;
  repoData?: Record<string, unknown>;
}

const EXAMPLE_QUESTIONS = [
  "What does this repository do?",
  "Where is the main entry point?",
  "How is authentication implemented?",
  "What testing framework is used?",
  "How do I run the tests?",
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ChatInterface() {
  const location = useLocation();
  const state = location.state as LocationState | null;

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hi! I'm your codebase guide. Ask me anything about this repository — architecture, file locations, how to run things, or where to start contributing.",
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const buildContext = useCallback(() => {
    const repoData = state?.repoData ?? {};
    const plan = state?.plan;
    const history = messages
      .filter((m) => m.id !== "welcome")
      .slice(-10)
      .map((m) => ({ role: m.role, content: m.content }));
    return {
      repo_summary: repoData,
      plan_overview: plan?.overview ?? null,
      conversation_history: history,
    };
  }, [state, messages]);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || loading) return;

      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: trimmed,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setInput("");
      setLoading(true);

      try {
        const answer = await api.chat(trimmed, buildContext());
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: answer,
            timestamp: new Date().toISOString(),
          },
        ]);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Request failed";
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: `⚠️ Error: ${msg}`,
            timestamp: new Date().toISOString(),
          },
        ]);
      } finally {
        setLoading(false);
        inputRef.current?.focus();
      }
    },
    [loading, buildContext]
  );

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        {/* Title bar */}
        <div style={styles.titleBar}>
          <h2 style={styles.title}>Ask the Codebase</h2>
          <span style={styles.subtitle}>Powered by AI · Context-aware answers</span>
        </div>

        {/* Message list */}
        <div style={styles.messageList}>
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          {loading && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>

        {/* Example questions */}
        {messages.length === 1 && (
          <div style={styles.examples}>
            {EXAMPLE_QUESTIONS.map((q) => (
              <button
                key={q}
                style={styles.exampleBtn}
                onClick={() => sendMessage(q)}
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {/* Input area */}
        <div style={styles.inputRow}>
          <textarea
            ref={inputRef}
            style={styles.textarea}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about the codebase…"
            rows={2}
            disabled={loading}
          />
          <button
            style={{
              ...styles.sendBtn,
              opacity: !input.trim() || loading ? 0.5 : 1,
              cursor: !input.trim() || loading ? "not-allowed" : "pointer",
            }}
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || loading}
          >
            Send
          </button>
        </div>
        <p style={styles.hint}>Press Enter to send · Shift+Enter for new line</p>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <div
      style={{
        ...styles.bubble,
        alignSelf: isUser ? "flex-end" : "flex-start",
        background: isUser ? "#3b82d4" : "#f7f8fa",
        color: isUser ? "#fff" : "#1f2328",
        borderRadius: isUser ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
      }}
    >
      <MessageContent content={message.content} isUser={isUser} />
    </div>
  );
}

function MessageContent({ content, isUser }: { content: string; isUser: boolean }) {
  // Render inline code and fenced code blocks simply
  const parts = content.split(/(```[\s\S]*?```)/g);
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith("```")) {
          const inner = part.replace(/^```[a-z]*\n?/, "").replace(/```$/, "");
          return (
            <pre
              key={i}
              style={{
                background: isUser ? "rgba(0,0,0,0.2)" : "#e8eaed",
                borderRadius: 4,
                padding: "8px 12px",
                fontSize: 12,
                overflow: "auto",
                margin: "6px 0",
                whiteSpace: "pre-wrap",
                wordBreak: "break-all",
              }}
            >
              <code>{inner}</code>
            </pre>
          );
        }
        return (
          <span
            key={i}
            style={{ fontSize: 14, lineHeight: 1.6, whiteSpace: "pre-wrap" }}
          >
            {part}
          </span>
        );
      })}
    </>
  );
}

function TypingIndicator() {
  return (
    <div style={{ ...styles.bubble, background: "#f7f8fa", alignSelf: "flex-start" }}>
      <span style={{ fontSize: 20, letterSpacing: 2 }}>
        <DotFlicker delay={0} />
        <DotFlicker delay={200} />
        <DotFlicker delay={400} />
      </span>
    </div>
  );
}

function DotFlicker({ delay }: { delay: number }) {
  const [visible, setVisible] = useState(true);
  useEffect(() => {
    const t = setTimeout(() => {
      const interval = setInterval(() => setVisible((v) => !v), 600);
      return () => clearInterval(interval);
    }, delay);
    return () => clearTimeout(t);
  }, [delay]);
  return <span style={{ opacity: visible ? 1 : 0.2 }}>·</span>;
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh",
    background: "#f7f8fa",
    display: "flex",
    alignItems: "stretch",
    fontFamily: '-apple-system, "Segoe UI", system-ui, sans-serif',
  },
  container: {
    flex: 1,
    maxWidth: 760,
    margin: "0 auto",
    display: "flex",
    flexDirection: "column",
    padding: "0 0 24px",
  },
  titleBar: {
    padding: "24px 24px 16px",
    borderBottom: "1px solid #e5e7eb",
    background: "#fff",
  },
  title: {
    fontSize: 20,
    fontWeight: 700,
    margin: "0 0 2px",
    color: "#1f2328",
  },
  subtitle: {
    fontSize: 12,
    color: "#57606a",
  },
  messageList: {
    flex: 1,
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: 12,
    padding: "20px 24px",
    minHeight: 300,
  },
  bubble: {
    maxWidth: "75%",
    padding: "12px 16px",
    borderRadius: 16,
    display: "flex",
    flexDirection: "column",
  },
  examples: {
    display: "flex",
    flexWrap: "wrap",
    gap: 8,
    padding: "0 24px 16px",
  },
  exampleBtn: {
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: 20,
    padding: "6px 14px",
    fontSize: 13,
    color: "#3b82d4",
    cursor: "pointer",
  },
  inputRow: {
    display: "flex",
    gap: 8,
    padding: "0 24px",
    alignItems: "flex-end",
  },
  textarea: {
    flex: 1,
    resize: "none",
    border: "1px solid #e5e7eb",
    borderRadius: 8,
    padding: "10px 14px",
    fontSize: 14,
    fontFamily: "inherit",
    lineHeight: 1.5,
    outline: "none",
  },
  sendBtn: {
    background: "#3b82d4",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    padding: "10px 20px",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    flexShrink: 0,
  },
  hint: {
    fontSize: 11,
    color: "#57606a",
    margin: "6px 24px 0",
  },
};
