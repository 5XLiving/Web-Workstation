import React from 'react'

export default function ProjectCard({ project }) {
  return (
    <article className="admin-project-card">
      <div className="admin-project-meta">
        <span className="admin-project-module">{project.module}</span>
        <span className="admin-project-status">{project.status}</span>
      </div>
      <h4>{project.name}</h4>
      <span className="admin-project-phase">{project.phase}</span>
      <p>{project.summary}</p>
      <div className="admin-project-footer">
        <span className="info-pill">{project.version}</span>
      </div>
    </article>
  )
}