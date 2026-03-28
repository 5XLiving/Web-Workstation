import React from 'react'

export default function SectionCard({ id, label, title, badge, actions, children }) {
  return (
    <section id={id} className="admin-section panel">
      <div className="panel-heading admin-section-heading">
        <div>
          <p className="panel-kicker">{label}</p>
          <h3>{title}</h3>
        </div>
        <div className="admin-section-tools">
          {badge ? <span className="section-badge">{badge}</span> : null}
          {actions}
        </div>
      </div>
      {children}
    </section>
  )
}