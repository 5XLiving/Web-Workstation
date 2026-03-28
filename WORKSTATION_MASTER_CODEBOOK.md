# Workstation Master Codebook

Source of truth for the hidden `/admin` Blackbox shell and workstation operating rules.

## 0. Current staging lock

- Do not change the live public homepage setup during this staging pass.
- workstation.5xliving.com remains the public Workstation homepage.
- The hidden admin surface is `/admin` only and must stay out of the public navigation.

## 1. Master platform identity

- 5xLiving is the main company brand.
- The VR Workstation / Workstation is the main business and main platform.
- Astro Sanctuary, PetPaws, 3D Model Maker, and future apps are projects/modules under the Workstation ecosystem.
- Treat every project as a real app/application by default unless you explicitly approve otherwise.

## 2. Domain and public structure

- Main public direction:
- 5xliving.com = company / workstation business landing direction
- workstation.5xliving.com = main workstation app/home
- astro.5xliving.com is no longer the preferred main front door. Astro is parked under Workstation.
- Keep subdomains modular for future apps.

## 3. Workstation architecture

- Architecture is:
- web 3D workstation frontend
- backend/orchestrator
- Unity Editor automation
- Main customer-facing layer is the web 3D / workstation UI
- Unity is mainly for:
- asset/scene building
- preview generation
- structured scene application
- Dev Room is the internal command center, not the public client product UI.

## 4. AI role split

- 5xLiving AI / workstation AI is reserved for internal workstation/dev room control.
- Client-facing users must use a separate lighter mini AI.
- Mini AI may:
- guide client
- collect inputs
- read codebook/project memory
- do mock runs / gap checks
- Mini AI may not:
- perform master admin actions directly
- run internal workstation-only actions
- switch production infra on its own
- change domains/DNS by itself

## 5. Memory model

- Use room-side codebook memory, not long-term AI session memory, as the main persistent control system.
- Each room/project owns its own persistent memory/codebook.
- AI should read:
- room codebook
- project scope
- current task
before acting.
- AI session memory should be temporary.

## 6. Execution flow

Every request/job must include:

- company
- project
- module

Standard job states:

- draft
- approved
- queued
- running
- completed
- failed
- archived

There must be an approval gate:

- preview
- approve
- push

Every push should create:

- new job id
- version id
- timestamp

Do not overwrite by default.

## 7. Failure/return format

All failed jobs must return a standard result:

- ok/fail
- job id
- failed stage
- readable error
- logs path

## 8. Worker split

Conceptual worker groups:

- web/UI workers
- AI workers
- queue/orchestrator
- Unity workers
- export/render workers

## 9. Output and storage rules

Outputs must be project-scoped:

- company/project/output
- company/project/logs

Client/company assets and data must support:

- local drive storage
- cloud storage
- later private/company-controlled storage

Use workspace/project permissions properly.

## 10. Security lock

Real system must stay server-side/cloud-hosted.
The VR workstation is only the client/control room interface.

Required protections:

- workspace isolation
- project isolation
- role-based access
- output segregation
- audit logging
- hidden admin routes
- HTTPS / server-side secrets
- request validation
- rate limits
- IP/session monitoring

Trade-secret logic must remain backend black-box:

- AI orchestration
- simulator logic
- generation pipeline
- export pipeline
- quotas/pricing logic
- internal prompts

Do not ship full trade-secret logic to client machines.

## 11. Easy mode / Expert mode

- Single app default = Easy Mode
- Higher tiers unlock:
- Easy Mode
- Expert Mode

## 12. Editing / selection model

Selection/editing modes must support:

- Object mode
- Group/Module mode
- Zone/Perimeter mode
- Detail mode

Default precise selector:

- a dot

Selection behavior:

- subtle outline appears after selection
- whole object vs perimeter/detail is mode-based

## 13. Spatial / hologram workflow

Desired workflow:

- Hologram / spatial-first
- user confirms look/view first
- then chooses output type

Main output path:

Hologram / Spatial editing
-> Unity
-> AutoCAD
-> Presentation output

Web 3D/spatial mode must support structured edits:

- object transforms
- terrain sculpt operations
- zone/region editing

All edits must be:

- stored as structured data
- versioned

No full rescan needed for normal in-app edits.
Rescan only for true external-source changes.

SketchUp-like interaction/tool feel is desired.

## 14. Build order lock

Preferred build order:

1. plain-language prompt
2. backend job translation
3. Unity preview generation
4. web 3D showroom
5. 2D draw-over edits
6. optional VR editing/inspection

## 15. Unity bridge lock

Use one main fast-lane web workflow with push to Unity.

Unity should use a prebuilt structured assembly system:

- scene templates
- mesh templates
- material slots
- lighting presets
- camera/export presets
- spawn/anchor points
- manager scripts

Web updates structured parameters like:

- template choice
- XYZ position
- scale
- colors/materials
- lighting preset
- scene preset

Unity reads a fixed structured build package schema and applies it.

## 16. Mock run / gap analysis rule

Before executing a job, AI should do two mock runs:

System execution mock run

Determine:

- what files are needed
- what systems/routes are needed
- what workers are needed

Build/execution mock run

Determine:

- how the job itself should be carried out

Then AI converts missing pieces into a queued to-do list and marks tasks done one by one.

Progress must persist so the client can return later and continue where they stopped.

## 17. Review Room rules

Review Room must support:

- compare outputs
- inspect version history
- approve/reject
- send back for edit
- push approved builds

## 18. Platform direction after launch

Once live:

- Workstation is the main control system
- Dev Room is internal command center
- AI/worker layer is execution backbone
- Copilot is not part of the live operating model

## 19. Product / pricing lock

Monthly-first pricing direction:

- simple 3D creator: about US$15/month
- indie workstation tier: about US$49/month
- corporate 3D tier: starts about US$199/month

Keep:

- usage caps
- credits
- storage/export limits

Do not promise unlimited heavy AI/3D generation on cheapest tier.

## 20. Product tiers concept

- Mass-market simple creator
- Indie serious workstation
- Corporate tier with:
- multi-seat shared workspace
- access locks
- shared workflow
- approvals
- audit logs

## 21. Dev Station AI Simulator lock

Simulations run on the Dev Station backend, not in the live client.
Frontend is just the control panel.

Simulation targets include:

- economy sim
- guild AI
- SvS war sim
- district/monopoly sim
- troop balance tests

## 22. Universal client-build rules

Client AI should build with portable structured systems:

- zone-based terrain planner
- modular city builder
- tagged gameplay object placer
- preset-based material/light system
- structured scene serializer

Everything should be stored in a portable structured format for reuse across projects and Unity/XYZ workflows.

## 23. Current live infra direction

- GitHub = source of truth for code
- Cloudflare Pages = live frontend hosting
- Cloudflare / backend services = app/backend path
- npm run dev = local workshop mode only
- live command center should not depend on npm run dev

## 24. Current immediate public setup

- Cloudflare Pages project created for workstation
- current preview:
- workstation-bgs.pages.dev
- target custom domain:
- workstation.5xliving.com
- DNS currently propagating

## 25. Launch requirement

Before launch:

- do a 100% full-system check
- minor issues do not require immediate change now
- but full-system verification is a locked launch requirement