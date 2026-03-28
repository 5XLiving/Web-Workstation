import { useState } from "react";

async function sendDevCommand(message) {
  const payload = {
    company: "5xLiving",
    project: "VR Workstation",
    module: "devroom",
    message,
  };

  const res = await fetch("/api/dev/command", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const text = await res.text();

  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = { ok: false, error: text || `HTTP ${res.status}` };
  }

  if (!res.ok) {
    throw new Error(data.error || data.msg || `HTTP ${res.status}`);
  }

  return data;
}

export default function DevRoomPage() {
  const [input, setInput] = useState("status");
  const [loading, setLoading] = useState(false);
  const [reply, setReply] = useState("");
  const [error, setError] = useState("");

  async function handleSend() {
    const message = input.trim();
    if (!message || loading) return;

    setLoading(true);
    setError("");
    setReply("");

    try {
      const data = await sendDevCommand(message);
      const pretty =
        typeof data === "string" ? data : JSON.stringify(data, null, 2);
      setReply(pretty);
    } catch (err) {
      setError(err.message || "Request failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0f1115",
        color: "#f5f7fa",
        padding: "32px",
        fontFamily:
          'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      }}
    >
      <div
        style={{
          maxWidth: 980,
          margin: "0 auto",
          display: "grid",
          gap: 20,
        }}
      >
        <div
          style={{
            border: "1px solid #2a2f3a",
            borderRadius: 16,
            padding: 20,
            background: "#171b22",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
            <div>
              <h1 style={{ margin: 0, fontSize: 28 }}>Dev Room</h1>
              <div style={{ marginTop: 8, color: "#aab4c3" }}>
                5xLiving Internal · VR Workstation
              </div>
            </div>
            <div
              style={{
                alignSelf: "start",
                border: "1px solid #3b4454",
                borderRadius: 999,
                padding: "8px 12px",
                color: "#d7deea",
                background: "#11151b",
              }}
            >
              Shared Worker Mode
            </div>
          </div>
        </div>

        <div
          style={{
            border: "1px solid #2a2f3a",
            borderRadius: 16,
            padding: 20,
            background: "#171b22",
          }}
        >
          <label
            htmlFor="devroom-input"
            style={{ display: "block", marginBottom: 12, fontWeight: 600 }}
          >
            Command
          </label>

          <textarea
            id="devroom-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a Dev Room command..."
            rows={6}
            style={{
              width: "100%",
              resize: "vertical",
              borderRadius: 12,
              border: "1px solid #31394a",
              background: "#0f1319",
              color: "#f5f7fa",
              padding: 14,
              fontSize: 15,
              boxSizing: "border-box",
            }}
          />

          <div style={{ marginTop: 16, display: "flex", gap: 12 }}>
            <button
              onClick={handleSend}
              disabled={loading}
              style={{
                border: 0,
                borderRadius: 12,
                padding: "12px 18px",
                background: loading ? "#4d5768" : "#d5b15b",
                color: "#101317",
                fontWeight: 700,
                cursor: loading ? "not-allowed" : "pointer",
              }}
            >
              {loading ? "Sending..." : "Send"}
            </button>

            <button
              onClick={() => {
                setInput("status");
                setReply("");
                setError("");
              }}
              style={{
                border: "1px solid #31394a",
                borderRadius: 12,
                padding: "12px 18px",
                background: "#11151b",
                color: "#f5f7fa",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Reset
            </button>
          </div>
        </div>

        <div
          style={{
            border: "1px solid #2a2f3a",
            borderRadius: 16,
            padding: 20,
            background: "#171b22",
          }}
        >
          <div style={{ fontWeight: 700, marginBottom: 12 }}>Response</div>

          {error ? (
            <pre
              style={{
                margin: 0,
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                color: "#ff8f8f",
                background: "#11151b",
                borderRadius: 12,
                padding: 14,
                border: "1px solid #3d2222",
              }}
            >
              {error}
            </pre>
          ) : (
            <pre
              style={{
                margin: 0,
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                color: "#d7deea",
                background: "#11151b",
                borderRadius: 12,
                padding: 14,
                border: "1px solid #31394a",
                minHeight: 180,
              }}
            >
              {reply || "No response yet."}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}