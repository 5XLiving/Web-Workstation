import React from 'react'

export default function StatusCard({ label, value, detail, tone = 'neutral' }) {
  return (
    <article className={`admin-status-card ${tone}`}>
      <span className="admin-status-label">{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  )
}