import React from 'react'
import { Link } from 'react-router-dom'

export default function AdminTopbar({ onLock }) {
  return (
    <header className="admin-topbar panel">
      <div className="admin-topbar-copy">
        <div className="meta-cluster">
          <span className="status-pill alert">Internal Admin Mode</span>
          <span className="status-pill online">Frontend shell active</span>
          <span className="status-pill paused">Backend detached</span>
        </div>
        <div>
          <p className="panel-kicker">Dev Room</p>
          <h2>Hidden Workstation control layer</h2>
          <p className="panel-copy">
            Premium blackbox shell for operator oversight, codebook control, review staging, and future backend integration points.
          </p>
        </div>
      </div>

      <div className="admin-topbar-actions">
        <div className="meta-cluster scope-meta">
          <span className="mode-chip active">5xLiving</span>
          <span className="mode-chip">VR Workstation</span>
          <span className="mode-chip">Admin Shell</span>
        </div>
        <div className="panel-actions">
          <Link className="secondary-link" to="/workstation">Open Workstation</Link>
          <button type="button" className="button ghost" onClick={onLock}>Lock Admin</button>
        </div>
      </div>
    </header>
  )
}