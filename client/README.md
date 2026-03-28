# 5xLiving VR Workstation Public Shell

This app is the public, company-facing front shell for 5xLiving VR Workstation. It is built as a static Vite deployment target and currently promotes three project lines:

- PetPaws
- Astro Sanctuary
- 3D Model Maker

Current deployment posture:

- Public shell only
- No backend or API dependency required
- No public Dev Room route exposed
- Cloudflare Pages compatible

Local development:

1. cd web-workstation
2. npm install
3. npm run dev

Production build:

1. cd web-workstation
2. npm run build

Build output:

- Command: `npm run build`
- Output folder: `dist`
- Vite config empties `dist` before each production build

Cloudflare Pages:

- Build command: `npm run build`
- Build output directory: `dist`
- Static route posture: `/`, `/#projects`, and `/#deployment`
- A branded `404.html` is included so unknown paths do not expose any hidden tool surface
