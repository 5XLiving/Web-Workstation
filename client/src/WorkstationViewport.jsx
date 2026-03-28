import React from 'react'
import { devRoomScope, getFriendlyScopeLabels } from './scopeModel'
import { useWorkstationBridge } from './workstationBridge'

export default function WorkstationViewport() {
  const { activeExecution } = useWorkstationBridge()
  const friendlyScope = { ...getFriendlyScopeLabels(devRoomScope), projectLabel: 'VR Workstation' }

  const executionStatus = activeExecution?.status || 'Idle'
  const executionLabel =
    executionStatus === 'Running'
      ? 'Worker running'
      : executionStatus === 'Completed'
        ? 'Worker replied'
          : executionStatus === 'Failed'
          ? 'Worker failed'
          : executionStatus === 'Dispatched'
            ? 'Sent to shared worker'
          : 'Viewport ready'

  const modules = [
    { name: 'Workspace', state: activeExecution ? 'Connected' : 'Ready' },
    { name: 'Viewport', state: executionLabel },
    { name: 'Commands', state: activeExecution?.parsed?.label || 'Control panel ready' },
  ]

  const notes = [
    activeExecution?.command
      ? `Active command: ${activeExecution.command}`
      : `This central area is prepared for focused workstation activity inside ${friendlyScope.workspaceLabel}.`,
    activeExecution?.parsed?.terrainSize
      ? `Requested terrain size: ${activeExecution.parsed.terrainSize.width} x ${activeExecution.parsed.terrainSize.height}.`
      : `Current project: ${friendlyScope.projectLabel}.`,
    activeExecution?.status
      ? `Shared worker state: ${activeExecution.status}.`
      : `Environment: ${friendlyScope.environmentLabel}.`,
  ]

  const viewportTitle = activeExecution?.command
    ? 'Dev Room request in workspace'
    : 'Central workstation viewport'

  const viewportCopy = activeExecution?.command
    ? `The Dev Room sent "${activeExecution.command}" to the shared 5xLiving worker for ${friendlyScope.projectLabel}.`
    : `A spacious, premium work area designed as the main entrance to the ${friendlyScope.workspaceLabel} experience.`

  const resultDetails = activeExecution?.result
      ? activeExecution.result.preview || activeExecution.result.failureReason || 'Result attached.'
      : null

  return (
    <section className="viewport-shell panel">
      <div className="viewport-head">
        <div>
          <p className="panel-kicker">Primary workspace</p>
          <h2>Main Work Area</h2>
        </div>
        <div className="meta-cluster">
          <span className="status-pill online">System active</span>
          <span className={`status-pill ${executionStatus === 'Failed' ? 'alert' : 'paused'}`}>{executionLabel}</span>
        </div>
      </div>

      <div className="viewport-stage">
        <div className="viewport-overlay">
          <div className="viewport-copy">
            <h3>{viewportTitle}</h3>
            <p>{viewportCopy}</p>
            <p className="viewport-scope-line">{friendlyScope.accountLabel} · {friendlyScope.workspaceLabel} · {friendlyScope.projectLabel} · {friendlyScope.roomLabel}</p>
            {activeExecution && (
              <div className="viewport-request-card">
                <span className="module-name">Execution</span>
                <strong>{activeExecution.status}</strong>
                <span className="module-name">Command</span>
                <strong>{activeExecution.command}</strong>
                {activeExecution.parsed?.terrainSize && (
                  <>
                    <span className="module-name">Terrain Size</span>
                    <strong>{activeExecution.parsed.terrainSize.width} x {activeExecution.parsed.terrainSize.height}</strong>
                  </>
                )}
                {resultDetails && (
                  <>
                    <span className="module-name">Result</span>
                    <strong>{resultDetails}</strong>
                  </>
                )}
              </div>
            )}
          </div>
          <div className="viewport-orbit" />
          <div className="viewport-grid" />
        </div>
      </div>

      <div className="viewport-footer">
        <div className="module-row">
          {modules.map((module) => (
            <div className="module-card" key={module.name}>
              <span className="module-name">{module.name}</span>
              <strong>{module.state}</strong>
            </div>
          ))}
        </div>

        <div className="notes-panel">
          <h3>Workspace Notes</h3>
          <ul className="viewport-notes">
            {notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}