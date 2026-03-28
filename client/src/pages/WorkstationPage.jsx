import React, { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import CommandPanel from '../CommandPanel'
import DebugPanel from '../DebugPanel'
import TopBar from '../TopBar'
import WorkstationViewport from '../WorkstationViewport'
import ThreeScene from '../components/ThreeScene'
import { WorkstationBridgeProvider, useWorkstationBridge } from '../workstationBridge'

function WorkstationPageContent() {
  const [showDebug, setShowDebug] = useState(false)
  const { activeExecution, clientFlowState, executionEvents } = useWorkstationBridge()

  const debugItems = useMemo(() => ([
    { label: 'Room', value: '3D Preview Active' },
    { label: 'Execution', value: activeExecution?.status || 'Idle' },
    { label: 'Request', value: activeExecution?.parsed?.label || 'Awaiting input' },
    { label: 'Client flow', value: clientFlowState?.status || 'Idle' },
  ]), [activeExecution, clientFlowState])

  const sceneRequest = activeExecution
    ? {
        command: activeExecution.command,
        result: activeExecution.result,
        error: activeExecution.result?.failureReason || null,
        mode: activeExecution.status,
      }
    : null

  return (
    <div className="workstation-shell">
      <TopBar />

      <div className="workstation-route-actions">
        <Link className="secondary-link" to="/">Back to Home</Link>
      </div>

      <section className="workstation-layout">
        <div className="workstation-main-column">
          <section className="panel workstation-scene-card">
            <div className="panel-heading compact">
              <div>
                <p className="panel-kicker">3D Preview Room</p>
                <h2>Web 3D Workstation</h2>
              </div>
              <span className="status-pill online">Canvas connected</span>
            </div>
            <p className="panel-copy">The workstation route restores the live 3D preview canvas as a separate browser surface.</p>
            <ThreeScene onMonitorClick={() => {}} sceneRequest={sceneRequest} />
          </section>

          <WorkstationViewport />
        </div>

        <aside className="workstation-side-column">
          <CommandPanel
            activeExecution={activeExecution}
            clientFlowState={clientFlowState}
            onToggleDebug={() => setShowDebug((current) => !current)}
            showDebug={showDebug}
          />
          <DebugPanel visible={showDebug} items={debugItems} events={executionEvents} />
        </aside>
      </section>
    </div>
  )
}

export default function WorkstationPage() {
  return (
    <WorkstationBridgeProvider>
      <WorkstationPageContent />
    </WorkstationBridgeProvider>
  )
}