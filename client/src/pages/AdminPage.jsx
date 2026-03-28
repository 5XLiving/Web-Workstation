import React, { useMemo, useState } from 'react'
import AdminSidebar from '../components/admin/AdminSidebar'
import AdminTopbar from '../components/admin/AdminTopbar'
import SectionCard from '../components/admin/SectionCard'
import StatusCard from '../components/admin/StatusCard'
import ProjectCard from '../components/admin/ProjectCard'
import {
  adminProjects,
  adminSections,
  codebookHighlights,
  executionPanels,
  healthSignals,
  overviewStats,
  queuedJobs,
  reconnectOrder,
  reviewItems,
  settingsGroups,
} from '../admin/adminData'
import {
  codebookSections,
  codebookSource,
  codebookTitle,
} from '../admin/codebookContent'

const ADMIN_SESSION_KEY = 'workstation-admin-unlocked'
const TEMP_PASSWORD = import.meta.env.VITE_WORKSTATION_ADMIN_PASSWORD || 'blackbox'

function renderCodebookBlock(block) {
  if (block.type === 'unordered') {
    return (
      <ul className="admin-codebook-list">
        {block.items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    )
  }

  if (block.type === 'ordered') {
    return (
      <ol className="admin-codebook-ordered-list">
        {block.items.map((item) => (
          <li key={`${item.index}-${item.text}`} value={Number(item.index)}>{item.text}</li>
        ))}
      </ol>
    )
  }

  return <p className="admin-codebook-paragraph">{block.content}</p>
}

function PasswordGate({ passwordInput, error, onChange, onSubmit }) {
  return (
    <div className="admin-gate-shell">
      <div className="admin-gate-card panel">
        <p className="panel-kicker">5xLiving Internal</p>
        <h1>Admin Blackbox Access</h1>
        <p className="panel-copy">
          This is a temporary frontend password gate for the hidden admin route while backend auth remains disconnected.
        </p>

        <form className="admin-gate-form" onSubmit={onSubmit}>
          <label className="field-label" htmlFor="admin-password">Temporary access key</label>
          <input
            id="admin-password"
            className="field-input"
            type="password"
            value={passwordInput}
            onChange={(event) => onChange(event.target.value)}
            placeholder="Enter internal admin password"
            autoComplete="current-password"
          />
          {error ? <p className="admin-gate-error">{error}</p> : null}
          <div className="panel-actions">
            <button type="submit" className="button">Unlock Admin Mode</button>
          </div>
        </form>

        <div className="admin-gate-note">
          <span className="status-pill alert">Internal Admin Mode</span>
          <span className="status-pill paused">Frontend-only gate</span>
        </div>
      </div>
    </div>
  )
}

export default function AdminPage() {
  const [passwordInput, setPasswordInput] = useState('')
  const [error, setError] = useState('')
  const [isUnlocked, setIsUnlocked] = useState(() => {
    if (typeof window === 'undefined') {
      return false
    }

    return window.sessionStorage.getItem(ADMIN_SESSION_KEY) === 'true'
  })
  const [activeSectionId, setActiveSectionId] = useState(adminSections[0].id)

  const commandLog = useMemo(() => ([
    'System execution mock run: files, routes, and workers mapped before action.',
    'Build execution mock run: task path staged, missing pieces converted into queue items.',
    'Admin shell mode: backend bridge intentionally detached, frontend placeholders active.',
  ]), [])

  function handleUnlock(event) {
    event.preventDefault()

    if (passwordInput !== TEMP_PASSWORD) {
      setError('Incorrect temporary admin password.')
      return
    }

    window.sessionStorage.setItem(ADMIN_SESSION_KEY, 'true')
    setIsUnlocked(true)
    setError('')
    setPasswordInput('')
  }

  function handleLock() {
    window.sessionStorage.removeItem(ADMIN_SESSION_KEY)
    setIsUnlocked(false)
    setActiveSectionId(adminSections[0].id)
  }

  function handleSectionSelect(sectionId) {
    setActiveSectionId(sectionId)
    const element = document.getElementById(sectionId)

    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  if (!isUnlocked) {
    return (
      <PasswordGate
        passwordInput={passwordInput}
        error={error}
        onChange={setPasswordInput}
        onSubmit={handleUnlock}
      />
    )
  }

  return (
    <div className="admin-shell">
      <div className="admin-layout">
        <AdminSidebar
          sections={adminSections}
          activeSectionId={activeSectionId}
          onSectionSelect={handleSectionSelect}
        />

        <main className="admin-main">
          <AdminTopbar onLock={handleLock} />

          <SectionCard id="overview" label="Overview" title="Internal command center snapshot" badge="Blackbox shell online">
            <div className="admin-status-grid">
              {overviewStats.map((item) => (
                <StatusCard key={item.label} {...item} />
              ))}
            </div>

            <div className="admin-callout-grid">
              <article className="admin-callout-card">
                <span className="panel-label">Operating model</span>
                <strong>Workstation is the public platform. Admin mode stays internal.</strong>
                <p>
                  This shell is staged as the hidden Dev Room command center while public routes remain brand-safe and workstation-facing.
                </p>
              </article>
              <article className="admin-callout-card accent">
                <span className="panel-label">Current mode</span>
                <strong>No backend dependency</strong>
                <p>
                  All surfaces below are static placeholders with clean component boundaries for future API and worker integration.
                </p>
              </article>
            </div>
          </SectionCard>

          <SectionCard id="execution-panel" label="Execution Panel" title="Frontend-only execution staging" badge="No backend or worker calls">
            <div className="admin-two-column-grid">
              <div className="admin-control-grid">
                {executionPanels.map((panel) => (
                  <article key={panel.title} className="admin-control-card">
                    <div className="admin-review-head">
                      <strong>{panel.title}</strong>
                      <span className="section-badge">{panel.status}</span>
                    </div>
                    <p>{panel.detail}</p>
                  </article>
                ))}
              </div>

              <div className="admin-list-card">
                <span className="panel-label">Later reconnect order</span>
                <div className="admin-sequence-list">
                  {reconnectOrder.map((route, index) => (
                    <div key={route} className="admin-sequence-item">
                      <strong>{index + 1}. {route}</strong>
                      <p>{index === 0 ? 'First backend reconnect target after the shell is complete.' : 'Kept deferred until the shell-only pass is finished.'}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="admin-two-column-grid">
              <div className="admin-list-card">
                <span className="panel-label">Mock run log</span>
                <div className="admin-command-log">
                  {commandLog.map((entry) => (
                    <div key={entry} className="admin-command-line">{entry}</div>
                  ))}
                </div>
              </div>

              <div className="admin-list-card">
                <span className="panel-label">Queued execution placeholders</span>
                <div className="admin-table-wrap">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Job ID</th>
                        <th>Project</th>
                        <th>Module</th>
                        <th>Stage</th>
                        <th>Version</th>
                        <th>Updated</th>
                      </tr>
                    </thead>
                    <tbody>
                      {queuedJobs.map((job) => (
                        <tr key={job.id}>
                          <td>{job.id}</td>
                          <td>{job.project}</td>
                          <td>{job.module}</td>
                          <td>{job.stage}</td>
                          <td>{job.version}</td>
                          <td>{job.updatedAt}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </SectionCard>

          <SectionCard id="codebook" label="Codebook" title="Locked operating rules" badge="Persistent room memory">
            <div className="admin-codebook-meta-grid">
              <article className="admin-list-card">
                <span className="panel-label">Source of truth</span>
                <strong>{codebookSource}</strong>
                <p>The admin Codebook tab imports this local repo file directly and stays frontend-only for now.</p>
              </article>
              <article className="admin-list-card">
                <span className="panel-label">Latest directives</span>
                <ul className="admin-bullet-list">
                  {codebookHighlights.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
            </div>

            <article className="admin-codebook-document">
              <div className="admin-codebook-document-head">
                <div>
                  <span className="panel-label">Imported document</span>
                  <h4>{codebookTitle}</h4>
                </div>
                <span className="section-badge">Local file import</span>
              </div>

              <div className="admin-codebook-sections">
                {codebookSections.map((section) => (
                  <section key={section.id} className="admin-codebook-section">
                    <h4>{section.title}</h4>
                    <div className="admin-codebook-blocks">
                      {section.blocks.map((block, index) => (
                        <div key={`${section.id}-${block.type}-${index}`} className="admin-codebook-block">
                          {renderCodebookBlock(block)}
                        </div>
                      ))}
                    </div>
                  </section>
                ))}
              </div>
            </article>
          </SectionCard>

          <SectionCard id="projects" label="Projects" title="Scoped workstation projects" badge={`${adminProjects.length} tracked`}>
            <div className="admin-project-grid">
              {adminProjects.map((project) => (
                <ProjectCard key={project.name} project={project} />
              ))}
            </div>
          </SectionCard>

          <SectionCard id="review-room" label="Review Room" title="Approval and version staging" badge="Compare • approve • push">
            <div className="admin-two-column-grid">
              <div className="admin-list-card">
                <span className="panel-label">Pending review sets</span>
                <div className="admin-review-list">
                  {reviewItems.map((item) => (
                    <article key={item.name} className="admin-review-card">
                      <div className="admin-review-head">
                        <strong>{item.name}</strong>
                        <span className="status-pill paused">{item.status}</span>
                      </div>
                      <span className="admin-review-owner">{item.owner}</span>
                      <p>{item.note}</p>
                    </article>
                  ))}
                </div>
              </div>
              <div className="admin-list-card">
                <span className="panel-label">Version compare placeholder</span>
                <div className="admin-compare-box">
                  <strong>Preview A / Preview B</strong>
                  <p>Future visual diff, approval notes, and push controls can mount here without changing the surrounding shell.</p>
                  <div className="pill-row">
                    <span className="info-pill">Version history</span>
                    <span className="info-pill">Approve / reject</span>
                    <span className="info-pill">Send back for edit</span>
                  </div>
                </div>
              </div>
            </div>
          </SectionCard>

          <SectionCard id="system-health" label="System Health" title="Operational posture" badge="Prepared for audit logging">
            <div className="admin-status-grid">
              {healthSignals.map((signal) => (
                <StatusCard key={signal.label} {...signal} />
              ))}
            </div>
          </SectionCard>

          <SectionCard id="settings" label="Settings" title="Shell configuration placeholders" badge="Frontend state only">
            <div className="admin-settings-grid">
              {settingsGroups.map((group) => (
                <article key={group.title} className="admin-list-card">
                  <span className="panel-label">{group.title}</span>
                  <div className="admin-settings-list">
                    {group.items.map((item) => (
                      <div key={item.label} className="admin-settings-item">
                        <strong>{item.label}</strong>
                        <span>{item.value}</span>
                      </div>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </SectionCard>
        </main>
      </div>
    </div>
  )
}