import React from 'react'

export default function AdminSidebar({ sections, activeSectionId, onSectionSelect }) {
  return (
    <aside className="admin-sidebar panel">
      <div className="admin-sidebar-brand">
        <p className="panel-kicker">5xLiving</p>
        <h1>Workstation Blackbox</h1>
        <p className="panel-copy">
          Internal command surface for scoped projects, codebook review, approvals, and future orchestration wiring.
        </p>
      </div>

      <div className="admin-sidebar-section">
        <span className="admin-sidebar-label">Admin Sections</span>
        <nav className="admin-sidebar-nav" aria-label="Internal admin sections">
          {sections.map((section) => {
            const active = section.id === activeSectionId

            return (
              <button
                key={section.id}
                type="button"
                className={`admin-nav-button${active ? ' active' : ''}`}
                onClick={() => onSectionSelect(section.id)}
              >
                <span>{section.label}</span>
              </button>
            )
          })}
        </nav>
      </div>

      <div className="admin-sidebar-section admin-sidebar-meta">
        <span className="admin-sidebar-label">Shell State</span>
        <div className="admin-meta-card">
          <strong>Frontend-only</strong>
          <p>No API fetches, worker calls, or backend dependencies are required in this mode.</p>
        </div>
        <div className="admin-meta-card">
          <strong>Internal Admin Mode</strong>
          <p>Hidden route with temporary client-side gate while the backend bridge is paused.</p>
        </div>
      </div>
    </aside>
  )
}