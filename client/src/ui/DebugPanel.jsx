import React from 'react'

export default function DebugPanel({ debug, lastCommand, logs = [], runnerMode }) {
  function copyDebug() {
    const payload = {
      time: new Date().toISOString(),
      runnerMode,
      lastCommand,
      logs: logs.slice(0, 50),
    }
    navigator.clipboard.writeText(JSON.stringify(payload, null, 2)).catch(() => {})
  }

  function clearLogs() {
    if (debug && debug.clearLogs) debug.clearLogs()
  }

  return (
    <aside className="debug-panel">
      <div className="debug-header">
        <strong>Debug / Error Panel</strong>
        <div className="debug-actions">
          <button onClick={copyDebug}>Copy Debug Info</button>
          <button onClick={clearLogs}>Clear Log</button>
        </div>
      </div>

      <div className="debug-body">
        <div><strong>Runner mode:</strong> {runnerMode}</div>
        <div><strong>Last command:</strong> {lastCommand || '—'}</div>
        <div className="debug-list">
          {logs.map((l, i) => (
            <div key={i} className={`debug-entry ${l.level}`}>
              <div className="time">{new Date(l.time).toLocaleTimeString()}</div>
              <div className="msg">[{l.stage}] {l.message}</div>
              {l.details && <pre className="details">{JSON.stringify(l.details, null, 2)}</pre>}
            </div>
          ))}
        </div>
      </div>
    </aside>
  )
}
