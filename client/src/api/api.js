// Dev Room API helper: forwards scoped requests to the shared 5xLiving worker bridge.
export default async function sendWorkerCommand(payload) {
  try {
    const res = await fetch('/api/dev/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const errorBody = await res.json().catch(() => null)
      const msg = errorBody?.error || `Shared worker bridge responded with status ${res.status}`
      const err = new Error(msg)
      err.status = res.status
      throw err
    }

    const data = await res.json().catch(() => null)
    return data
  } catch (err) {
    const e = err instanceof Error ? err : new Error(String(err))
    console.error('sendWorkerCommand error:', e)
    throw new Error(e.message || 'Shared worker not connected')
  }
}
