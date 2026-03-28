import React from 'react'

export default function StatusOutput({ status, result }) {
  return (
    <div className="status-output">
      <div><strong>Status:</strong> {status}</div>
      <div className="result-box">
        <pre>{result ? JSON.stringify(result, null, 2) : 'No output yet'}</pre>
      </div>
    </div>
  )
}
