import React from 'react'
import { Link } from 'react-router-dom'

const platformApps = [
  {
    name: 'Astro Sanctuary',
    summary: 'Cinematic world-building, review staging, and presentation-ready environmental previews inside the Workstation platform.',
    focus: 'World presentation app',
    state: 'Preview staging',
  },
  {
    name: 'PetPaws',
    summary: 'Interactive planning surface for pet-focused scenes, gameplay scope, layouts, and reusable build structure.',
    focus: 'Experience planning app',
    state: 'Scope validation',
  },
  {
    name: '3D Model Maker',
    summary: 'Browser-first asset creation, review, and export preparation for downstream workstation and Unity workflows.',
    focus: 'Asset creation app',
    state: 'Frontend aligned',
  },
  {
    name: 'Future Apps',
    summary: 'Reserved launch lane for additional project tools, client spaces, and premium workstation modules as the platform expands.',
    focus: 'Modular expansion lane',
    state: 'Ready for routing',
  },
]

const capabilityPillars = [
  {
    title: 'Platform launcher',
    detail: 'One public front door for the Workstation brand, app discovery, and later login routing without changing the landing structure.',
  },
  {
    title: 'Frontend-only deployment',
    detail: 'Static and deployable in the current setup with no worker dependency, backend requirement, or API fetches.',
  },
  {
    title: 'Structured app ecosystem',
    detail: 'Apps such as Astro Sanctuary, PetPaws, and 3D Model Maker sit under one Workstation platform direction.',
  },
  {
    title: 'Future-ready routing',
    detail: 'Clean section boundaries leave room for sign-in, workspace access, and app launch flows later.',
  },
]

const platformStats = [
  { label: 'Public route', value: 'workstation.5xliving.com' },
  { label: 'Current mode', value: 'Static frontend shell' },
  { label: 'Launch surface', value: '/workstation app entry' },
]

export default function HomePage() {
  return (
    <div className="public-shell public-homepage">
      <header className="public-site-topbar panel">
        <div className="public-site-brand">
          <p className="eyebrow">5xLiving</p>
          <strong>Workstation</strong>
        </div>

        <nav className="public-site-nav" aria-label="Primary">
          <a className="secondary-link" href="#platform">Platform</a>
          <a className="secondary-link" href="#apps">Apps</a>
          <a className="secondary-link" href="#capabilities">Capabilities</a>
          <Link className="primary-link public-gold-button" to="/workstation">Open Workstation</Link>
        </nav>
      </header>

      <header className="hero-section public-hero-panel">
        <div className="hero-copy">
          <p className="eyebrow">Public Platform Homepage</p>
          <h1>5xLiving Workstation is the main launch surface for the platform.</h1>
          <p className="hero-text">
            A premium browser-based front door for opening Workstation apps, presenting active products, and introducing the 5xLiving platform without exposing internal admin tooling.
          </p>
          <div className="hero-actions">
            <Link className="primary-link public-gold-button" to="/workstation">Launch Workstation</Link>
            <a className="secondary-link public-gold-outline" href="#apps">Explore Apps</a>
          </div>

          <div className="public-stat-row">
            {platformStats.map((item) => (
              <article key={item.label} className="public-stat-card">
                <span className="panel-label">{item.label}</span>
                <strong>{item.value}</strong>
              </article>
            ))}
          </div>
        </div>

        <div className="hero-panel">
          <span className="panel-label">Platform Profile</span>
          <strong>Product homepage first</strong>
          <p>
            The public experience is positioned as a real platform homepage and app launcher, with a clean split between public routes and internal control surfaces.
          </p>

          <div className="public-hero-list">
            <div className="public-hero-list-item">
              <span className="section-badge">Public</span>
              <p>Brand-facing homepage for workstation.5xliving.com</p>
            </div>
            <div className="public-hero-list-item">
              <span className="section-badge">Apps</span>
              <p>Launcher direction for Astro Sanctuary, PetPaws, 3D Model Maker, and future modules</p>
            </div>
            <div className="public-hero-list-item">
              <span className="section-badge">Static</span>
              <p>Deployable now with no backend coupling required</p>
            </div>
          </div>
        </div>
      </header>

      <main className="content-grid">
        <section className="overview-card public-story-card" id="platform">
          <p className="section-label">What Is 5xLiving Workstation</p>
          <h2>The platform layer for launching, organizing, and presenting 5xLiving apps.</h2>
          <p>
            5xLiving Workstation is the public platform homepage for the ecosystem. It introduces the platform, frames the available apps, and provides a clean path into the browser-based workstation surface while keeping internal admin tooling hidden.
          </p>

          <div className="highlight-list public-story-grid">
            <article className="highlight-card public-story-block">
              <span className="panel-label">Platform direction</span>
              <strong>One homepage, multiple apps</strong>
              <p>The site now reads as the main Workstation product homepage instead of a single-project showcase.</p>
            </article>
            <article className="highlight-card public-story-block">
              <span className="panel-label">Public routing</span>
              <strong>Admin remains hidden</strong>
              <p>Only public-facing platform routes are presented here. Internal admin and Dev Room surfaces stay out of public navigation.</p>
            </article>
            <article className="highlight-card public-story-block">
              <span className="panel-label">Ready for expansion</span>
              <strong>Login and launch later</strong>
              <p>The page structure leaves room for account access, workspace routing, and app launching without another homepage rewrite.</p>
            </article>
          </div>
        </section>

        <section className="projects-card public-apps-card" id="apps">
          <div className="section-heading">
            <div>
              <p className="section-label">Project / App Cards</p>
              <h2>Apps inside the 5xLiving Workstation platform</h2>
            </div>
            <span className="section-badge">4 launch lanes</span>
          </div>

          <div className="project-grid public-app-grid">
            {platformApps.map((project, index) => (
              <article key={project.name} className="project-card public-app-card">
                <span className="project-index">0{index + 1}</span>
                <h3>{project.name}</h3>
                <span className="project-focus">{project.focus}</span>
                <span className="public-app-state">{project.state}</span>
                <p>{project.summary}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="readiness-card public-capability-card" id="capabilities">
          <div className="section-heading">
            <div>
              <p className="section-label">Core Capabilities</p>
              <h2>Built to behave like a platform homepage now, with app routing later.</h2>
            </div>
            <span className="section-badge">Frontend-only</span>
          </div>

          <div className="route-grid public-capability-grid">
            {capabilityPillars.map((pillar) => (
              <article key={pillar.title} className="route-card public-capability-block">
                <h3>{pillar.title}</h3>
                <p>{pillar.detail}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="projects-card public-cta-card" id="launch">
          <div className="section-heading">
            <div>
              <p className="section-label">Simple CTA</p>
              <h2>Enter the browser-based Workstation platform.</h2>
            </div>
          </div>

          <p className="hero-text public-cta-copy">
            This homepage stays static and deployable in the current setup, while the workstation route remains ready for app access and future login flows.
          </p>

          <div className="hero-actions">
            <Link className="primary-link public-gold-button" to="/workstation">Open Workstation</Link>
            <a className="secondary-link public-gold-outline" href="#platform">Read Platform Overview</a>
          </div>
        </section>
      </main>

      <footer className="public-footer">
        <p className="section-label">5xLiving Workstation</p>
        <p className="footer-copy">Public platform homepage for launching apps, presenting the ecosystem, and routing users into the browser-based workstation.</p>
      </footer>
    </div>
  )
}