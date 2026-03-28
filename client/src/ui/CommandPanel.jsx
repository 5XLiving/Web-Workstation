import React, { useState } from 'react'
import runJob from '../api/api'
import StatusOutput from './StatusOutput'

export default function CommandPanel({ visible, onClose, context, debug, onRunResult }) {
  const [project, setProject] = useState('Default Project')
  const [command, setCommand] = useState('')
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])

  if (!visible) return null

  async function handleRun() {
    setStatus('running')
    setResult(null)
    const entryBase = { time: new Date().toISOString(), command, project }
    if (debug && debug.pushLog) debug.pushLog({ ...entryBase, stage: 'ui', level: 'info', message: 'Submit command' })

    try {
      const res = await runJob({ project, command })
      setResult(res)
      setHistory(h => [{ time: Date.now(), project, command, res }, ...h])
      setStatus('done')
      if (debug && debug.pushLog) debug.pushLog({ ...entryBase, stage: 'runner', level: 'info', message: 'Runner returned', details: { res } })
      if (onRunResult) onRunResult({ command, result: res, mode: 'real' })
    } catch (err) {
      const msg = err && err.message ? err.message : String(err)
      setResult({ error: msg })
      setStatus('error')
      if (debug && debug.pushLog) debug.pushLog({ ...entryBase, stage: 'runner', level: 'error', message: 'Runner failed', details: { error: msg } })
      // Inform parent about failure so it can decide to attempt local preview/build.
      if (onRunResult) onRunResult({ command, error: msg, mode: 'missing' })
    }
  }

  return (
    <aside className="right-panel">
      <div className="panel-header">
        <h3>Workstation Console</h3>
        <button onClick={onClose}>Close</button>
      </div>

      <div className="panel-body">
        <label>Project</label>
        <select value={project} onChange={e => setProject(e.target.value)}>
          <option>Default Project</option>
          <option>Scene Build</option>
          <option>Test Job</option>
        </select>

        <label>Command</label>
        <input value={command} onChange={e => setCommand(e.target.value)} placeholder="e.g. build scene" />

        <div className="panel-actions">
          <button className="run" onClick={handleRun}>Run</button>
        </div>

        <StatusOutput status={status} result={result} />

        <div className="history">
          <h4>History</h4>
          <ul>
            {history.map((h, i) => (
              <li key={i}>{new Date(h.time).toLocaleTimeString()} — {h.command}</li>
            ))}
          </ul>
        </div>
      </div>
    </aside>
  )
}
