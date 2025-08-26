Always show details
# Create a Markdown recovery plan file for the user to download
content = r"""# OurLibrary — Disaster Recovery & Modernization Plan

**Date:** 2025-08-26  
**Prepared by:** Navi (with Herb)  
**Context:** Clean repo reset completed; goal is to restore the intended multi‑page flow (landing → register → consent → device setup → library app), remove historical drift, and harden the stack for GitHub Pages + privacy‑strict browsers.

---

## 0) Objectives (what “done” looks like)

- ✅ Canonical user journey restored:
  `index.html → welcome.html → setup-consent.html → Set Up Your Personal Library - OurLibrary.html → library.html (enhanced desktop)`.
- ✅ Tailwind no longer loaded via browser CDN; precompiled static CSS is served.
- ✅ Vendored libs present & correctly wired: `JS/lib/sql-wasm.js`, `JS/lib/sql-wasm.wasm`, `JS/lib/pdf.js`, `JS/lib/pdf.worker.js`.
- ✅ File Manager runs during setup (saves persistent directory handle); Library page gracefully guards and redirects when handle is missing.
- ✅ DB bootstrap stable (`initSqlJs` with `locateFile`), seed DB downloaded only when absent.
- ✅ Git hygiene: `.gitignore` blocks local/state/secret content; `..Exclude/` is local-only; secrets redacted from public docs.
- ✅ Pages deployment green; smoke tests clean in Chrome/Firefox/Tor.

---

## 1) Canonical Flow (source of truth)

1. **index.html** – Landing/redirect page (may redirect to `welcome.html` after brief splash).
2. **welcome.html** – Intro + CTA (“Get Started” → registration or consent).
3. **setup-consent.html** – Terms, data use, storage location explanation. On accept → continue.
4. **Set Up Your Personal Library - OurLibrary.html** – Device bootstrap:
   - Call `OurLibraryFileManager.initialize()` (prompts for base folder or restores handle from IndexedDB).
   - Create subdirs (`/Books`, `/Downloads`, `/Database`, `/Covers`, etc.) if missing.
   - When ready → `location.href = './library.html'`.
5. **library.html** – The app:
   - On load: guard for file‑manager readiness; if missing, show message & redirect back to `setup-consent.html`.
   - DB init (`initSqlJs`), load categories/subjects/books; render grid; open PDFs via pdf.js.

> **Routing rule:** Only `index.html` is an entry point. All deep links to `library.html` should still work, but if no directory handle is present, library page must bounce to consent/setup with a friendly message.

---

## 2) Tailwind migration (remove browser warning)

**One‑time setup (already prepared in last session; safe to re-run):**
```bash
npm i -D tailwindcss postcss autoprefixer
npx tailwindcss init -p


tailwind.config.js

Always show details
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./**/*.html", "./JS/**/*.js"],
  theme: { extend: {} },
  plugins: [],
};


assets/css/input.css

Always show details
@tailwind base;
@tailwind components;
@tailwind utilities;


Build CSS

Always show details
npx tailwindcss -i ./assets/css/input.css -o ./assets/css/tailwind.css --minify


HTML changes (all pages that used CDN Tailwind):

Always show details
<!-- remove the CDN <script src="https://cdn.tailwindcss.com"> -->
<link rel="stylesheet" href="./assets/css/tailwind.css">


package.json convenience script:

Always show details
"scripts": {
  "build:css": "tailwindcss -i ./assets/css/input.css -o ./assets/css/tailwind.css --minify"
}

3) Vendored libraries (SQLite + PDF)

Files to keep in repo (static):

Always show details
JS/lib/sql-wasm.js
JS/lib/sql-wasm.wasm
JS/lib/pdf.js
JS/lib/pdf.worker.js


Include in HTML (order matters):

Always show details
<script src="./JS/lib/sql-wasm.js"></script>
<script src="./JS/lib/pdf.js"></script>
<script>
  // pdf.js worker wiring
  pdfjsLib.GlobalWorkerOptions.workerSrc = './JS/lib/pdf.worker.js';
</script>
<!-- Then your app scripts -->
<script src="./JS/filesystem-library-manager.js"></script>
<script src="./JS/database.js"></script>
<script src="./JS/gdrive.js"></script>


database.js (robust wasm resolution):

Always show details
const SQL = await initSqlJs({
  locateFile: f => new URL(`./JS/lib/${f}`, window.location.href).href
});

4) Page‑by‑page wiring
4.1 index.html

Minimal splash (or static banner).

Either present CTA → welcome.html, or auto‑redirect with <meta http-equiv="refresh"> after ~0.5–1s.

Include compiled Tailwind via <link>.

4.2 welcome.html

CTA buttons:

“Get Started” → setup-consent.html

“I already have an account” → your auth entry (or same flow if registration handled elsewhere).

4.3 setup-consent.html

Show ToS / storage explainer.

On accept:

location.href = './Set Up Your Personal Library - OurLibrary.html' (directory picker on that page).

(Alternative: run picker here, then go straight to library.html).

4.4 Set Up Your Personal Library - OurLibrary.html

On CTA (“Choose your library folder”):

Always show details
const ok = await window.OurLibraryFileManager?.initialize();
if (ok) location.href = './library.html';
else /* show friendly message & stay on page */;


Show progress states (created folders, write test, IndexedDB saved, etc.).

4.5 library.html

On DOMContentLoaded:

Always show details
if (!window.OurLibraryFileManager || typeof OurLibraryFileManager.initialize !== 'function') {
  // script didn’t load → friendly error, suggest refresh
}
const ready = await OurLibraryFileManager.initialize();
if (!ready) {
  // show message then after a short delay:
  location.href = './setup-consent.html';
  return;
}
// proceed: init DB, load catalogs, render grid


Image fallback for covers:

Always show details
<img src="..." onerror="this.onerror=null;this.src='./assets/images/default-book.png'">

5) GitHub Pages specifics

Keep .nojekyll at repo root.

Prefer relative paths (./assets/..., ./JS/...) not absolute (/assets/...), due to Pages subpath (/OurLibrary/).

Avoid symlinks in the published tree.

PHP/serverside (api/) won’t run on Pages — keep backend assets in a different repo or local only.

6) E2E testing (Playwright)

Auth flow (already scaffolded):

Navigate to landing → open registration → submit → capture code from console (dev/demo mode) → verify → land in library page.

Navigation flow (add tests):

index → welcome → consent → setup → library.

Assert specific DOM elements at each step (e.g., consent text, directory picker CTA, first book card).

Run (headed):

Always show details
npm run test:headed
# or
npx playwright test --headed

7) Smoke test checklist (manual)

Open: https://callmechewy.github.io/OurLibrary/

In DevTools Console (private window, extensions off):

Always show details
typeof initSqlJs      // "function"
typeof pdfjsLib       // "object"
pdfjsLib.version      // "4.x.x"


Walk flow: welcome → consent → setup (choose folder) → library.

Confirm: covers render (fallback works), search/filter, open a PDF (worker loads, no errors).

8) Disaster‑Recovery playbook (if drift recurs)

Freeze + Snapshot – git branch backup/pre-reset-$(date +%Y%m%d-%H%M%S)

Orphan reset – git checkout --orphan clean-main

Untrack local/secret dirs – git rm -r --cached --ignore-unmatch archive installers node_modules .venv .playwright-mcp test-results playwright-report Data library_web.db ..Exclude website api

Rebuild Tailwind – npm run build:css

Commit – “Initial clean import (history reset; local-only artifacts untracked)”

Force push – git branch -M clean-main main && git push --force-with-lease origin main

Pages check – Settings → Pages → main /(root) → hard refresh live site.

9) Open items / decisions

Where to host the directory picker?

Option A: setup-consent.html (one step fewer)

Option B: Set Up Your Personal Library – OurLibrary.html (clearer separation of consent vs setup) ← recommended

Auth backend – If registration is mocked on Pages, production auth should be flipped to Firebase (or your backend) with email delivery out of band. Keep dev-mode console code capture only in non-production builds.

GDrive file map – If assets/data/gdrive_file_map.json contains public file IDs by design, OK. If sensitive, generate it at runtime or fetch from Sheets via public API with a token‑free read‑only view.

10) Ready‑made commit plan (what to push next)

Ensure pages exist & linked:

Always show details
index.html
welcome.html
setup-consent.html
Set Up Your Personal Library - OurLibrary.html
library.html
assets/images/default-book.png
JS/lib/{sql-wasm.js,sql-wasm.wasm,pdf.js,pdf.worker.js}
JS/{filesystem-library-manager.js,database.js,gdrive.js,environment.js,SheetsAnalytics.js}
assets/css/tailwind.css  (compiled)
.nojekyll


Replace Tailwind CDN with <link rel="stylesheet" href="./assets/css/tailwind.css"> in all pages.

Verify database.js uses locateFile as given.

Push & deploy; run smoke tests.

Appendix A — Minimal redirects (optional convenience)

index.html (fast redirect to welcome):

Always show details
<!doctype html><meta charset="utf-8">
<title>OurLibrary</title>
<meta http-equiv="refresh" content="0; url=./welcome.html">
<link rel="canonical" href="./welcome.html">
<p>Redirecting to <a href="./welcome.html">welcome</a>…</p>


404.html (route stray deep links to app):

Always show details
<!doctype html><meta charset="utf-8">
<title>Not Found</title>
<meta http-equiv="refresh" content="0; url=./welcome.html">
<link rel="canonical" href="./welcome.html">
<p>Not found. Redirecting to <a href="./welcome.html">welcome</a>…</p>


End of plan.
