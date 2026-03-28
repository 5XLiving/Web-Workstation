import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

const mockOutputs = [
  {
    id: "petpaws-terrain-001",
    title: "PetPaws Terrain Prototype",
    type: "Build Package",
    state: "draft",
    project: "PetPaws",
    updatedAt: "2026-03-13 09:10",
    summary: "Terrain scale test with starter roads and district markers.",
  },
  {
    id: "vrws-review-014",
    title: "VR Workstation Review Snapshot",
    type: "Preview Export",
    state: "approved",
    project: "VR Workstation",
    updatedAt: "2026-03-13 08:24",
    summary: "Shell validation snapshot for workstation route review.",
  },
  {
    id: "astro-scene-002",
    title: "Astro Sanctuary Test Scene",
    type: "Scene Draft",
    state: "queued",
    project: "Astro Sanctuary",
    updatedAt: "2026-03-12 19:42",
    summary: "First-pass sanctuary scene prepared for internal review.",
  },
];

const mockVersionsByOutput = {
  "petpaws-terrain-001": [
    {
      id: "v2026.03.13-001",
      label: "Version 001",
      state: "draft",
      createdAt: "2026-03-13 09:10",
      note: "Initial terrain package for prototype review.",
    },
    {
      id: "v2026.03.12-004",
      label: "Version 004",
      state: "archived",
      createdAt: "2026-03-12 17:35",
      note: "Prior terrain variant with smaller test area.",
    },
  ],
  "vrws-review-014": [
    {
      id: "v2026.03.13-014",
      label: "Version 014",
      state: "approved",
      createdAt: "2026-03-13 08:24",
      note: "Approved shell snapshot for workstation review lane.",
    },
    {
      id: "v2026.03.12-011",
      label: "Version 011",
      state: "completed",
      createdAt: "2026-03-12 16:10",
      note: "Earlier completed preview state before approval.",
    },
  ],
  "astro-scene-002": [
    {
      id: "v2026.03.12-002",
      label: "Version 002",
      state: "queued",
      createdAt: "2026-03-12 19:42",
      note: "Queued for next internal scene review.",
    },
    {
      id: "v2026.03.11-001",
      label: "Version 001",
      state: "draft",
      createdAt: "2026-03-11 15:06",
      note: "First draft sanctuary scene package.",
    },
  ],
};

function getActionState(action) {
  switch (action) {
    case "approve":
      return "approved";
    case "reject":
      return "failed";
    case "send-back":
      return "draft";
    case "ready-to-push":
      return "ready_to_push";
    default:
      return "draft";
  }
}

export default function ReviewRoomPage() {
  const [selectedOutputId, setSelectedOutputId] = useState(mockOutputs[0].id);
  const versions = useMemo(
    () => mockVersionsByOutput[selectedOutputId] || [],
    [selectedOutputId],
  );
  const [selectedVersionId, setSelectedVersionId] = useState(versions[0]?.id || "");
  const [currentState, setCurrentState] = useState(versions[0]?.state || mockOutputs[0].state);

  const selectedOutput = useMemo(
    () => mockOutputs.find((output) => output.id === selectedOutputId) || mockOutputs[0],
    [selectedOutputId],
  );

  const selectedVersion = useMemo(
    () => versions.find((version) => version.id === selectedVersionId) || versions[0],
    [selectedVersionId, versions],
  );

  function handleSelectOutput(outputId) {
    const nextVersions = mockVersionsByOutput[outputId] || [];
    setSelectedOutputId(outputId);
    setSelectedVersionId(nextVersions[0]?.id || "");
    setCurrentState(nextVersions[0]?.state || mockOutputs.find((output) => output.id === outputId)?.state || "draft");
  }

  function handleSelectVersion(versionId) {
    const version = versions.find((item) => item.id === versionId);
    setSelectedVersionId(versionId);
    if (version) {
      setCurrentState(version.state);
    }
  }

  function handleAction(action) {
    setCurrentState(getActionState(action));
  }

  return (
    <div className="workstation-shell">
      <div className="panel reviewroom-panel">
        <div className="panel-heading compact">
          <div>
            <p className="panel-kicker">Internal Review Lane</p>
            <h2>Review Room</h2>
          </div>
          <div className="meta-cluster">
            <span className="status-pill online">Mock Data Only</span>
            <Link className="secondary-link" to="/workstation">
              Back to Workstation
            </Link>
            <Link className="secondary-link" to="/dev-room">
              Open Dev Room
            </Link>
          </div>
        </div>

        <div className="reviewroom-meta">
          <div className="scope-header-card reviewroom-status-card">
            <p className="panel-label">Project</p>
            <strong className="reviewroom-status-value">{selectedOutput.project}</strong>
            <span className="reviewroom-status-label">Current review context</span>
          </div>
        </div>
      </div>

      <section className="reviewroom-layout">
        <div className="reviewroom-main">
          <div className="reviewroom-columns">
            <section className="panel reviewroom-panel">
              <div className="section-heading">
                <div>
                  <p className="panel-kicker">Outputs</p>
                  <h3>Output List</h3>
                </div>
                <span className="section-badge">{mockOutputs.length} items</span>
              </div>

              <ul className="reviewroom-list">
                {mockOutputs.map((output) => (
                  <li key={output.id}>
                    <button
                      className={output.id === selectedOutputId ? "active" : ""}
                      onClick={() => handleSelectOutput(output.id)}
                      type="button"
                    >
                      <strong>{output.title}</strong>
                      <span>{output.type} · {output.updatedAt}</span>
                      <span>{output.summary}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </section>

            <section className="panel reviewroom-panel">
              <div className="section-heading">
                <div>
                  <p className="panel-kicker">History</p>
                  <h3>Version History</h3>
                </div>
                <span className="section-badge">{versions.length} versions</span>
              </div>

              <ul className="reviewroom-list">
                {versions.map((version) => (
                  <li key={version.id}>
                    <button
                      className={version.id === selectedVersion?.id ? "active" : ""}
                      onClick={() => handleSelectVersion(version.id)}
                      type="button"
                    >
                      <strong>{version.label}</strong>
                      <span>{version.state} · {version.createdAt}</span>
                      <span>{version.note}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          </div>

          <section className="panel reviewroom-panel reviewroom-preview">
            <div className="section-heading">
              <div>
                <p className="panel-kicker">Compare</p>
                <h3>Compare / Preview</h3>
              </div>
              <span className="section-badge">Placeholder</span>
            </div>

            <div className="reviewroom-preview-box">
              <div>
                <strong className="reviewroom-preview-title">Preview surface reserved for output compare and inspection.</strong>
                <p className="reviewroom-preview-copy">
                  Attach export/output gateway previews, diff snapshots, and later Unity push readiness checks here.
                </p>
              </div>
            </div>
          </section>
        </div>

        <aside className="reviewroom-side">
          <section className="panel reviewroom-panel">
            <div className="section-heading">
              <div>
                <p className="panel-kicker">Actions</p>
                <h3>Review Actions</h3>
              </div>
            </div>

            <div className="reviewroom-actions">
              <button className="button" onClick={() => handleAction("approve")} type="button">Approve</button>
              <button className="button ghost" onClick={() => handleAction("reject")} type="button">Reject</button>
              <button className="button ghost" onClick={() => handleAction("send-back")} type="button">Send Back for Edit</button>
              <button className="button" onClick={() => handleAction("ready-to-push")} type="button">Mark Ready to Push</button>
            </div>
          </section>

          <section className="panel reviewroom-panel">
            <div className="section-heading">
              <div>
                <p className="panel-kicker">Status</p>
                <h3>Status Panel</h3>
              </div>
            </div>

            <div className="reviewroom-status-grid">
              <div className="scope-header-card reviewroom-status-card">
                <span className="reviewroom-status-label">Current Project</span>
                <strong className="reviewroom-status-value">{selectedOutput.project}</strong>
              </div>

              <div className="scope-header-card reviewroom-status-card">
                <span className="reviewroom-status-label">Selected Output / Version</span>
                <strong className="reviewroom-status-value">
                  {selectedOutput.id} / {selectedVersion?.id || "none"}
                </strong>
              </div>

              <div className="scope-header-card reviewroom-status-card">
                <span className="reviewroom-status-label">Current State</span>
                <strong className="reviewroom-status-value">{currentState}</strong>
              </div>
            </div>
          </section>
        </aside>
      </section>
    </div>
  );
}