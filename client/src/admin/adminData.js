export const adminSections = [
  { id: 'overview', label: 'Overview' },
  { id: 'execution-panel', label: 'Execution Panel' },
  { id: 'codebook', label: 'Codebook' },
  { id: 'projects', label: 'Projects' },
  { id: 'review-room', label: 'Review Room' },
  { id: 'system-health', label: 'System Health' },
  { id: 'settings', label: 'Settings' },
]

export const overviewStats = [
  { label: 'Scoped projects', value: '04', detail: 'PetPaws, Astro Sanctuary, 3D Model Maker, Core Workstation', tone: 'neutral' },
  { label: 'Queued items', value: '12', detail: 'Awaiting approval, preview, or scheduled execution', tone: 'warning' },
  { label: 'Approval gates', value: '05', detail: 'Draft, preview, approve, push, archive checkpoints tracked', tone: 'accent' },
  { label: 'System posture', value: 'Stable', detail: 'Frontend-only admin shell running with no backend dependency', tone: 'success' },
]

export const adminProjects = [
  {
    name: 'VR Workstation',
    module: 'Core platform',
    phase: 'Internal command center',
    status: 'Ready',
    summary: 'Main orchestration shell for routing jobs, approvals, codebook reads, and room-state control across the workstation ecosystem.',
    version: 'v0.9 blackbox',
  },
  {
    name: 'Astro Sanctuary',
    module: 'World presentation',
    phase: 'Preview staging',
    status: 'Queued',
    summary: 'Spatial presentation project parked under Workstation with structured preview, review, and future Unity push readiness.',
    version: 'preview-17',
  },
  {
    name: 'PetPaws',
    module: 'Interactive experience',
    phase: 'Scope validation',
    status: 'In review',
    summary: 'Gameplay and environment planning surface with portable build rules, structured scene data, and modular reuse targets.',
    version: 'scope-12',
  },
  {
    name: '3D Model Maker',
    module: 'Asset pipeline',
    phase: 'Frontend alignment',
    status: 'Monitoring',
    summary: 'Browser-first maker module aligned for future structured export, preview generation, and Workstation review handoff.',
    version: 'maker-08',
  },
]

export const codebookHighlights = [
  'WORKSTATION_MASTER_CODEBOOK.md is the local source of truth for this shell.',
  'Every request is scoped by company, project, and module before execution.',
  'Preview, approve, and push remain locked gates with new job ids and version ids per push.',
  'Trade-secret orchestration, simulation, generation, and export logic stay backend-side and black-boxed.',
  'Workstation remains the main platform, while the Blackbox admin route stays internal-only.',
]

export const reviewItems = [
  {
    name: 'Astro Sanctuary Preview Set B',
    status: 'Awaiting approval',
    owner: 'Design review',
    note: 'Compare atmosphere, camera preset, and world silhouette before push.',
  },
  {
    name: 'PetPaws Layout Revision 12',
    status: 'Returned for edit',
    owner: 'Gameplay scope',
    note: 'Needs perimeter and detail mode separation before version lock.',
  },
]

export const queuedJobs = [
  {
    id: 'job-20260315-0907',
    project: 'VR Workstation',
    module: 'admin-shell',
    stage: 'completed',
    version: 'admin-v1',
    updatedAt: '2026-03-15 09:07',
  },
  {
    id: 'job-20260315-0831',
    project: 'Astro Sanctuary',
    module: 'preview-room',
    stage: 'approved',
    version: 'astro-preview-17',
    updatedAt: '2026-03-15 08:31',
  },
  {
    id: 'job-20260314-2244',
    project: 'PetPaws',
    module: 'terrain-plan',
    stage: 'draft',
    version: 'petpaws-scope-12',
    updatedAt: '2026-03-14 22:44',
  },
  {
    id: 'job-20260314-2130',
    project: '3D Model Maker',
    module: 'export-map',
    stage: 'queued',
    version: 'maker-08',
    updatedAt: '2026-03-14 21:30',
  },
]

export const executionPanels = [
  {
    title: 'Execution staging',
    status: 'Standby',
    detail: 'Mock execution lanes are visible, but no worker, backend, or AI call is allowed from this shell yet.',
  },
  {
    title: 'Approval discipline',
    status: 'Locked',
    detail: 'Preview, approve, and push checkpoints remain visible so future reconnect work preserves the gate order.',
  },
  {
    title: 'Reconnect boundary',
    status: 'Placeholder',
    detail: 'Later API reconnect work is limited to health, ping, codebook, and execute endpoints in that exact order.',
  },
]

export const reconnectOrder = [
  '/health',
  '/admin/ping',
  '/admin/codebook',
  '/admin/execute',
]

export const healthSignals = [
  { label: 'Frontend shell', value: 'Online', tone: 'success', detail: 'Static route, local state, and mock control surfaces are active.' },
  { label: 'Backend bridge', value: 'Detached', tone: 'warning', detail: 'Intentionally disconnected while admin shell is staged frontend-only.' },
  { label: 'Worker mesh', value: 'Offline', tone: 'neutral', detail: 'No API workers or queue dependencies are required in this mode.' },
  { label: 'Audit posture', value: 'Prepared', tone: 'accent', detail: 'UI is structured for future job ids, versions, timestamps, and operator logs.' },
]

export const settingsGroups = [
  {
    title: 'Admin shell mode',
    items: [
      { label: 'Hidden route exposure', value: '/admin only' },
      { label: 'Temporary gate', value: 'Frontend password' },
      { label: 'Public nav visibility', value: 'Disabled' },
    ],
  },
  {
    title: 'Future connections',
    items: [
      { label: 'Job queue provider', value: 'Pending backend adapter' },
      { label: 'Codebook source', value: 'WORKSTATION_MASTER_CODEBOOK.md' },
      { label: 'Reconnect order', value: '/health -> /admin/ping -> /admin/codebook -> /admin/execute' },
    ],
  },
]