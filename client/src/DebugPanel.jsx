import React from 'react'

export default function DebugPanel({ visible, items = [], events = [] }) {
  if (!visible) {
    return null
  }

  return (
    <section className="panel debug-panel">
      <div className="panel-heading compact">
        <div>
          <p className="panel-kicker">Status rail</p>
          <h2>System Status</h2>
        </div>
        <span className="status-pill online">System available</span>
      </div>

      <p className="panel-copy">A calm overview of the current workstation session and interface readiness.</p>

      <div className="debug-grid">
        {items.map((item) => (
          <div className="debug-item" key={item.label}>
            <span className="debug-label">{item.label}</span>
            <strong>{item.value}</strong>
          </div>
        ))}
      </div>

      <div className="debug-event-log">
        <h3>Execution Event Log</h3>
        <div className="devroom-list compact">
          {events.length ? events.slice(0, 6).map((event) => (
            <article className="devroom-row" key={event.id}>
              <div className="devroom-row-title">{event.stage}</div>
              <div className="devroom-row-copy">{event.message}</div>
              <div className="devroom-row-meta">{event.time}</div>
            </article>
          )) : <div className="devroom-empty">No execution events yet.</div>}
        </div>
      </div>
    </section>
  )
}