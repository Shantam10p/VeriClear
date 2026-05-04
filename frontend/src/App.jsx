import React, { useEffect, useRef, useState } from "react";

const API_URL = "http://127.0.0.1:8000/api/v1/query";

const DEMO_SCENARIOS = [
  { label: "Billing increase", customer_id: "cust_001", message: "Why did my bill go up this month?" },
  { label: "Confused billing", customer_id: "cust_005", message: "I am confused about why my bill increased this month." },
  { label: "Frustrated billing", customer_id: "cust_006", message: "This bill is ridiculous. Explain why it is so high." },
  { label: "Tech support", customer_id: "cust_002", message: "My phone service is down and my network is not working." },
  { label: "Account help", customer_id: "cust_004", message: "I need to update the owner on my account." },
];

const EMOTION_STYLES = {
  neutral:     { bg: "bg-slate-100",  text: "text-slate-600",  label: "Neutral" },
  happy:       { bg: "bg-emerald-50", text: "text-emerald-700", label: "Happy" },
  confused:    { bg: "bg-amber-50",   text: "text-amber-700",  label: "Confused" },
  frustrated:  { bg: "bg-red-50",     text: "text-red-700",    label: "Frustrated" },
  threatening: { bg: "bg-rose-100",   text: "text-rose-800",   label: "Escalated" },
};

const INTENT_STYLES = {
  billing:             { bg: "bg-blue-50",   text: "text-blue-700",   label: "Billing" },
  tech_support:        { bg: "bg-violet-50", text: "text-violet-700", label: "Tech Support" },
  account_management:  { bg: "bg-teal-50",   text: "text-teal-700",   label: "Account Mgmt" },
};

function Icon({ name, filled, className = "" }) {
  return (
    <span
      className={`material-symbols-outlined ${className}`}
      style={filled ? { fontVariationSettings: "'FILL' 1" } : undefined}
    >
      {name}
    </span>
  );
}

function Badge({ bg, text, children }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${bg} ${text}`}>
      {children}
    </span>
  );
}

function BillingCard({ billing }) {
  if (!billing) return null;
  const delta = (billing.current_total - billing.previous_total).toFixed(2);
  return (
    <div className="billing-card">
      <div className="billing-card-header">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Statement Summary</span>
        <Icon name="receipt_long" className="text-blue-600 text-lg" />
      </div>
      <div className="billing-card-body">
        <div className="billing-row">
          <div>
            <p className="text-sm font-semibold text-slate-800">Plan: {billing.plan_name}</p>
            <p className="text-[11px] text-slate-500">Monthly base charge</p>
          </div>
          <span className="text-sm font-bold text-slate-800">${billing.monthly_plan_cost.toFixed(2)}</span>
        </div>
        {billing.activation_fee > 0 && (
          <div className="billing-row">
            <div>
              <p className="text-sm font-semibold text-slate-800">Activation Fee</p>
              <p className="text-[11px] text-slate-500">One-time charge</p>
            </div>
            <span className="text-sm font-bold text-slate-800">${billing.activation_fee.toFixed(2)}</span>
          </div>
        )}
        {billing.prorated_charge > 0 && (
          <div className="billing-row">
            <div>
              <p className="text-sm font-semibold text-slate-800">Prorated Charge</p>
              <p className="text-[11px] text-slate-500">Mid-cycle adjustment</p>
            </div>
            <span className="text-sm font-bold text-slate-800">${billing.prorated_charge.toFixed(2)}</span>
          </div>
        )}
        {billing.overage_charge > 0 && (
          <div className="billing-row">
            <div>
              <p className="text-sm font-semibold text-slate-800">Overage Charge</p>
              <p className="text-[11px] text-slate-500">Usage beyond included limit</p>
            </div>
            <span className="text-sm font-bold text-slate-800">${billing.overage_charge.toFixed(2)}</span>
          </div>
        )}
        <div className="billing-row">
          <div>
            <p className="text-sm font-semibold text-slate-800">Taxes &amp; Fees</p>
          </div>
          <span className="text-sm font-bold text-slate-800">${billing.taxes_and_fees.toFixed(2)}</span>
        </div>
        <div className="billing-total">
          <span className="text-sm font-extrabold text-blue-700 uppercase tracking-tight">Total</span>
          <span className="text-xl font-extrabold text-blue-700">${billing.current_total.toFixed(2)}</span>
        </div>
        <p className="text-[11px] text-slate-400 mt-1">Previous month: ${billing.previous_total.toFixed(2)} &middot; Change: +${delta}</p>
      </div>
    </div>
  );
}

function MetadataBadges({ data }) {
  if (!data) return null;
  const emotion = EMOTION_STYLES[data.emotion] || EMOTION_STYLES.neutral;
  const intent = INTENT_STYLES[data.intent] || INTENT_STYLES.billing;
  return (
    <div className="flex flex-wrap gap-2 mt-3">
      <Badge bg={intent.bg} text={intent.text}>
        <Icon name="category" className="text-[13px]" /> {intent.label}
      </Badge>
      <Badge bg={emotion.bg} text={emotion.text}>
        <Icon name="mood" className="text-[13px]" /> {emotion.label}
      </Badge>
      <Badge bg="bg-slate-100" text="text-slate-600">
        <Icon name="speed" className="text-[13px]" /> {(data.confidence * 100).toFixed(0)}%
      </Badge>
      {data.auto_resolve ? (
        <Badge bg="bg-emerald-50" text="text-emerald-700">
          <Icon name="check_circle" className="text-[13px]" /> Auto-resolved
        </Badge>
      ) : (
        <Badge bg="bg-amber-50" text="text-amber-700">
          <Icon name="support_agent" className="text-[13px]" /> CSR Handoff
        </Badge>
      )}
    </div>
  );
}

function CustomerBubble({ text, time }) {
  return (
    <div className="chat-row chat-row--customer">
      <div className="bubble bubble--customer">
        <p>{text}</p>
      </div>
      <span className="bubble-meta bubble-meta--right">{time}</span>
    </div>
  );
}

function AssistantBubble({ summary, billing, transfer, metadata }) {
  return (
    <div className="chat-row chat-row--assistant">
      <div className="assistant-identity">
        <div className="assistant-avatar">
          <Icon name="smart_toy" filled className="text-sm text-blue-600" />
        </div>
        <span className="text-[11px] font-bold text-blue-600 uppercase tracking-widest">VeriClear AI</span>
      </div>
      <div className="bubble bubble--assistant">
        {summary && summary.length > 0 && (
          <div className="space-y-3">
            {summary.map((line, i) => (
              <p key={i} className="text-sm leading-relaxed text-slate-700">{line}</p>
            ))}
          </div>
        )}
        {billing && <BillingCard billing={billing} />}
        {transfer && (
          <div className="transfer-banner">
            <Icon name="support_agent" className="text-amber-600 text-lg" />
            <p className="text-sm text-amber-800">{transfer}</p>
          </div>
        )}
        <MetadataBadges data={metadata} />
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="chat-row chat-row--assistant">
      <div className="assistant-identity">
        <div className="assistant-avatar">
          <Icon name="smart_toy" filled className="text-sm text-blue-600" />
        </div>
        <span className="text-[11px] font-bold text-blue-600 uppercase tracking-widest">VeriClear AI</span>
      </div>
      <div className="bubble bubble--assistant typing-bubble">
        <div className="typing-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [customerId, setCustomerId] = useState("cust_001");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    const userMsg = { role: "customer", text: text.trim(), time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customer_id: customerId, message: text.trim() }),
      });
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const data = await res.json();
      const assistantMsg = {
        role: "assistant",
        summary: data.summary || [],
        billing: data.billing_data || null,
        transfer: data.transfer_message || null,
        metadata: {
          intent: data.intent,
          emotion: data.emotion,
          confidence: data.confidence,
          auto_resolve: data.auto_resolve,
        },
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", summary: ["Sorry, something went wrong connecting to the backend. Please try again."], billing: null, transfer: null, metadata: null },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleScenario = (scenario) => {
    setCustomerId(scenario.customer_id);
    sendMessage(scenario.message);
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <nav className={`sidebar ${sidebarOpen ? "sidebar--open" : "sidebar--closed"}`}>
        <div className="sidebar-brand">
          <div className="brand-icon">
            <Icon name="dataset" filled className="text-white text-lg" />
          </div>
          <div className="brand-text">
            <span className="text-lg font-bold text-blue-600">VeriClear</span>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">Premium Support</p>
          </div>
        </div>

        <div className="sidebar-section">
          <p className="sidebar-label">Customer ID</p>
          <input
            className="sidebar-input"
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            placeholder="cust_001"
          />
        </div>

        <div className="sidebar-section">
          <p className="sidebar-label">Demo Scenarios</p>
          <div className="scenario-list">
            {DEMO_SCENARIOS.map((s) => (
              <button key={s.label} className="scenario-btn" onClick={() => handleScenario(s)}>
                <Icon name={
                  s.label.includes("Billing") || s.label.includes("billing") ? "receipt_long" :
                  s.label.includes("Tech") ? "wifi_off" : "manage_accounts"
                } className="text-base" />
                <span>{s.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="sidebar-footer">
          <button className="scenario-btn" onClick={clearChat}>
            <Icon name="delete_sweep" className="text-base" />
            <span>Clear chat</span>
          </button>
        </div>
      </nav>

      {/* Main */}
      <main className="chat-main">
        {/* Header */}
        <header className="chat-header">
          <div className="flex items-center gap-3">
            <button className="sidebar-toggle" onClick={() => setSidebarOpen((v) => !v)}>
              <Icon name="menu" />
            </button>
            <h1 className="text-base font-extrabold text-blue-600" style={{ fontFamily: "Manrope, sans-serif" }}>
              AI Billing Assistant
            </h1>
            <div className="status-pill">
              <span className="status-dot"></span>
              <span>Online</span>
            </div>
          </div>
        </header>

        {/* Messages */}
        <div className="chat-scroll" ref={scrollRef}>
          <div className="chat-container">
            {messages.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">
                  <Icon name="chat_bubble" filled className="text-4xl text-blue-200" />
                </div>
                <h2>Welcome to VeriClear</h2>
                <p>Ask a billing question or pick a demo scenario from the sidebar.</p>
              </div>
            )}

            {messages.map((msg, i) =>
              msg.role === "customer" ? (
                <CustomerBubble key={i} text={msg.text} time={msg.time} />
              ) : (
                <AssistantBubble
                  key={i}
                  summary={msg.summary}
                  billing={msg.billing}
                  transfer={msg.transfer}
                  metadata={msg.metadata}
                />
              )
            )}

            {loading && <TypingIndicator />}
          </div>
        </div>

        {/* Composer */}
        <footer className="chat-composer">
          <form className="composer-form" onSubmit={handleSubmit}>
            <input
              className="composer-input"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message here..."
              disabled={loading}
            />
            <button className="composer-send" type="submit" disabled={loading || !input.trim()}>
              <Icon name="send" filled />
            </button>
          </form>
          <p className="composer-disclaimer">AI can make mistakes. Check important billing info.</p>
        </footer>
      </main>
    </div>
  );
}

export default App;
