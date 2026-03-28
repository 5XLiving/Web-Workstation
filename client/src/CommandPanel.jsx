import React, { useState } from 'react'
import { devRoomScope, getFriendlyScopeLabels, getScopeBindings } from './scopeModel'
import { useWorkstationBridge } from './workstationBridge'

export default function CommandPanel({ activeExecution, clientFlowState, onToggleDebug, showDebug }) {
  const [draft, setDraft] = useState('')
  const { submitClientRequest } = useWorkstationBridge()
  const friendlyScope = { ...getFriendlyScopeLabels(devRoomScope), projectLabel: 'VR Workstation' }
  const scopeBindings = getScopeBindings(devRoomScope)

  async function handleSubmit() {
    const command = draft.trim()
    if (!command) {
      return
    }

    await submitClientRequest({
      command,
      targetContext: devRoomScope,
      localState: {
        activeExecutionStatus: activeExecution?.status || 'Idle',
        lastResult: activeExecution?.result?.artifactType || activeExecution?.result?.failureReason || null,
        currentSession: clientFlowState.status || 'Idle',
        scopeBinding: {
          accountId: scopeBindings.accountId,
          workspaceId: scopeBindings.workspaceId,
          projectId: scopeBindings.projectId,
          roomId: scopeBindings.roomId,
          roomType: scopeBindings.roomType,
          environmentId: scopeBindings.environmentId,
          sectorId: scopeBindings.sectorId,
          codebookId: scopeBindings.codebookId,
          packId: scopeBindings.packId,
          packagePlan: scopeBindings.packagePlan,
        },
      },
    })
    setDraft('')
  }

  return (
    <section className="panel command-panel">
      <div className="panel-heading">
        <div>
          <p className="panel-kicker">Control rail</p>
          <h2>Command Panel</h2>
        </div>
        <span className="status-pill paused">Dev Room ready</span>
      </div>

      <p className="panel-copy">Use this area to send scoped Dev Room instructions for {friendlyScope.projectLabel} through the shared 5xLiving worker.</p>

      <div className="chip-row scope-chip-row">
        <span className="mode-chip active">{friendlyScope.accountLabel}</span>
        <span className="mode-chip">{friendlyScope.workspaceLabel}</span>
        <span className="mode-chip">{friendlyScope.projectLabel}</span>
        <span className="mode-chip">{friendlyScope.environmentLabel}</span>
      </div>

      <div className="stack-block">
        <label className="field-label" htmlFor="workspace-command">Workspace prompt</label>
        <textarea
          id="workspace-command"
          className="field-input field-textarea"
          placeholder="Enter a workspace prompt or planning note."
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
        />
        <div className="panel-actions">
          <button className="button" type="button" onClick={handleSubmit}>
            Send request
          </button>
        </div>
      </div>

      <div className="stack-block">
        <div className="mini-header">
          <h3>Modes</h3>
          <span className="mini-note">Available</span>
        </div>
        <div className="chip-row">
          <span className="mode-chip active">Workstation</span>
          <span className="mode-chip">Inspect</span>
          <span className="mode-chip">Review</span>
        </div>
      </div>

      <div className="stack-block">
        <div className="mini-header">
          <h3>Readiness</h3>
        </div>
        <ul className="command-list">
          <li>Workstation AI is reserved for internal Dev Room use.</li>
          <li>Bound room: {friendlyScope.roomLabel}.</li>
          <li>{activeExecution ? `Current command: ${activeExecution.command}` : 'Environment active with a clear command layout.'}</li>
          <li>{activeExecution ? `Execution state: ${activeExecution.status}` : 'Status panel available for quick reference.'}</li>
          <li>{activeExecution?.result ? `Attached result: ${activeExecution.result.artifactType || 'available'}` : 'Awaiting attached result.'}</li>
          <li>{clientFlowState?.failureReason ? `Worker status: ${clientFlowState.failureReason}` : 'Shared 5xLiving worker is active for Dev Room requests.'}</li>
        </ul>
      </div>

      <div className="stack-block">
        <div className="mini-header">
          <h3>Worker Reply</h3>
          <span className="mini-note">Latest</span>
        </div>
        <p className="panel-copy">{activeExecution?.result?.reply || activeExecution?.result?.preview || 'No worker reply yet.'}</p>
      </div>

      <div className="panel-actions vertical">
        <button className="button" type="button" onClick={onToggleDebug}>
          {showDebug ? 'Hide status panel' : 'Show status panel'}
        </button>
        <button className="button ghost" type="button" disabled>
          Environment active
        </button>
      </div>
    </section>
  )
}