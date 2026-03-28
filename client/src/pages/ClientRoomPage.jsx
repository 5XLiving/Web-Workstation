import { useState } from "react";
import { Link } from "react-router-dom";

const mockTasks = [
  { id: "scope", label: "Confirm project scope", status: "Ready" },
  { id: "codebook", label: "Load client-safe codebook", status: "Pending" },
  { id: "progress", label: "Save progress snapshot", status: "Pending" },
];

const defaultInput = "Summarize the current project goal for the client-safe view.";

export default function ClientRoomPage() {
  const [input, setInput] = useState(defaultInput);
  const [response, setResponse] = useState("No response yet.");
  const [status, setStatus] = useState("Idle");
  const [lastAction, setLastAction] = useState("Waiting for client task.");

  function handleSend() {
    const message = input.trim();
    if (!message) {
      setStatus("Needs input");
      setLastAction("Send blocked: enter a request first.");
      setResponse("No response generated. Add a client task request and try again.");
      return;
    }

    setStatus("Mock reply ready");
    setLastAction("Generated mock mini AI reply.");
    setResponse(
      [
        "Client Room mock response",
        "Scope: 5xLiving / PetPaws / client-room",
        "Codebook mode: client-safe if available, otherwise filtered master",
        `Request: ${message}`,
        "Next: connect this panel to the client-safe codebook loader and mini AI lane.",
      ].join("\n")
    );
  }

  function handleReset() {
    setInput(defaultInput);
    setResponse("No response yet.");
    setStatus("Idle");
    setLastAction("Reset to default mock state.");
  }

  function handleMockCheck() {
    setStatus("Mock check complete");
    setLastAction("Ran local shell check for client-room readiness.");
    setResponse(
      [
        "Mock check complete",
        "- Client-safe codebook lane: placeholder ready",
        "- Mini AI lane: not connected",
        "- Progress checklist: placeholder ready",
        "- Project memory: not connected",
      ].join("\n")
    );
  }

  function handleSaveProgress() {
    setStatus("Progress saved");
    setLastAction("Stored a mock progress checkpoint.");
    setResponse(
      [
        response,
        "",
        "Mock progress checkpoint saved for later project memory integration.",
      ].join("\n")
    );
  }

  return (
    <div className="workstation-shell">
      <section className="panel" style={{ padding: 24 }}>
        <div className="panel-heading compact">
          <div>
            <p className="panel-kicker">Client-Facing Workspace</p>
            <h2>Client Room</h2>
          </div>
          <div className="meta-cluster">
            <span className="status-pill paused">Mock Only</span>
            <Link className="secondary-link" to="/workstation">
              Back to Workstation
            </Link>
            <Link className="secondary-link" to="/review-room">
              Open Review Room
            </Link>
          </div>
        </div>

        <div
          className="scope-header-card"
          style={{ padding: 18, marginTop: 16 }}
        >
          <p className="panel-label">Current Scope</p>
          <strong>5xLiving / PetPaws / client-room</strong>
          <p className="panel-copy" style={{ marginBottom: 0 }}>
            Client-facing mini AI shell prepared for client-safe codebook loading.
          </p>
        </div>
      </section>

      <section
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(0, 1.45fr) minmax(320px, 0.8fr)",
          gap: 22,
          marginTop: 22,
        }}
      >
        <div style={{ display: "grid", gap: 22 }}>
          <section className="panel" style={{ padding: 24 }}>
            <div className="section-heading">
              <div>
                <p className="panel-kicker">Mini AI</p>
                <h3>Task Input</h3>
              </div>
            </div>

            <textarea
              className="field-input field-textarea"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Describe the client-safe task request..."
            />

            <div className="panel-actions" style={{ marginTop: 16 }}>
              <button className="button" onClick={handleSend} type="button">
                Send
              </button>
              <button className="button ghost" onClick={handleReset} type="button">
                Reset
              </button>
              <button className="button ghost" onClick={handleMockCheck} type="button">
                Run Mock Check
              </button>
              <button className="button" onClick={handleSaveProgress} type="button">
                Save Progress
              </button>
            </div>
          </section>

          <section className="panel" style={{ padding: 24 }}>
            <div className="section-heading">
              <div>
                <p className="panel-kicker">Response</p>
                <h3>Reply Panel</h3>
              </div>
            </div>

            <pre
              style={{
                margin: 0,
                minHeight: 220,
                padding: 18,
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                borderRadius: 22,
                border: "1px solid rgba(145, 184, 255, 0.16)",
                background: "rgba(255, 255, 255, 0.03)",
                color: "var(--text)",
              }}
            >
              {response}
            </pre>
          </section>
        </div>

        <aside style={{ display: "grid", gap: 22 }}>
          <section className="panel" style={{ padding: 24 }}>
            <div className="section-heading">
              <div>
                <p className="panel-kicker">Tasks</p>
                <h3>Progress / Todo</h3>
              </div>
              <span className="section-badge">Placeholder</span>
            </div>

            <div style={{ display: "grid", gap: 12 }}>
              {mockTasks.map((task) => (
                <div key={task.id} className="scope-header-card" style={{ padding: 16 }}>
                  <strong>{task.label}</strong>
                  <span className="project-focus">{task.status}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="panel" style={{ padding: 24 }}>
            <div className="section-heading">
              <div>
                <p className="panel-kicker">Status</p>
                <h3>Status Panel</h3>
              </div>
            </div>

            <div style={{ display: "grid", gap: 12 }}>
              <div className="scope-header-card" style={{ padding: 16 }}>
                <span className="project-focus">Current Project</span>
                <strong>PetPaws</strong>
              </div>
              <div className="scope-header-card" style={{ padding: 16 }}>
                <span className="project-focus">Codebook Mode</span>
                <strong>Client-safe or filtered master</strong>
              </div>
              <div className="scope-header-card" style={{ padding: 16 }}>
                <span className="project-focus">Current State</span>
                <strong>{status}</strong>
              </div>
              <div className="scope-header-card" style={{ padding: 16 }}>
                <span className="project-focus">Last Action</span>
                <strong>{lastAction}</strong>
              </div>
            </div>
          </section>
        </aside>
      </section>
    </div>
  );
}