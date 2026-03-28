import React from 'react'
import { clientRoomScope, getFriendlyScopeLabels } from './scopeModel'

export default function TopBar() {
  const friendlyScope = getFriendlyScopeLabels(clientRoomScope)

  return (
    <header className="topbar panel">
      <div className="brand-block">
        <p className="panel-kicker">5xLiving</p>
        <div>
          <h1>5xLiving Workstation</h1>
          <p className="topbar-copy">A refined workspace entrance for planning, review, and guided workstation sessions across {friendlyScope.workspaceLabel}.</p>
        </div>
      </div>

      <div className="topbar-meta">
        <div className="meta-cluster">
          <span className="status-pill online">Workspace ready</span>
          <span className="status-pill paused">Session active</span>
        </div>
        <div className="meta-cluster scope-meta">
          <span className="mode-chip active">{friendlyScope.accountLabel}</span>
          <span className="mode-chip">{friendlyScope.workspaceLabel}</span>
          <span className="mode-chip">{friendlyScope.projectLabel}</span>
          <span className="mode-chip">{friendlyScope.environmentLabel}</span>
        </div>
        <div className="topbar-nav" aria-label="Primary">
          <span className="nav-link active">Workstation</span>
        </div>
      </div>
    </header>
  )
}