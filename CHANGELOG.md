# ChequeSense — Change Log

> Reference document. Each version lists: reported issues → what was fixed.
> Latest first. **Version scheme: 0.x.x-alpha (pre-release).**

---

## v0.4.0-alpha — 2026-08-02 (IndexedDB Storage Migration)

**Issue:** localStorage ~5MB quota caps data volume — thousands of cheques + receipts (esp. PDFs) eventually crash saves.

**Fixed:**
- Storage layer migrated from localStorage → **IndexedDB** (disk-backed, ~100×+ capacity, 12MB+ tested).
- `saveDB()` snapshots synchronously (write-order safe) → async IndexedDB write; falls back to localStorage for small DBs.
- **Automatic migration** — existing localStorage data is copied to IndexedDB on first load; app code untouched (single storage module).
- Verified: 2,000 cheques persist across reload; Dashboard renders 2,000 batches in 20ms; 12MB single write OK.

---

## v0.3.2-alpha — 2026-08-02 (Storage Quota Crash + Receipt Viewer)

**Issues reported:**
1. Reconcile flow: upload receipt → freeze; partial submissions vanish; verify unresponsive.
2. No popup viewer for uploaded documents.

**Fixed:**
- **Root cause:** `localStorage.setItem` threw uncaught `QuotaExceededError` once receipts (multi-MB base64) exceeded the ~5MB origin quota → uploads/verifies appeared frozen, saves silently failed.
- Receipts are now **compressed on upload** (max 1600px JPEG @ 0.7 + 200px thumbnail) — a 5MB photo becomes ~100–300KB, ~20–50× more receipts fit.
- `saveDB()` wrapped in try/catch with a clear "Storage full" toast.
- **Receipt viewer popup** — click any receipt: image or PDF shown full-size in a modal (was `window.open`).
- **Checkbox default fix** — reopening a partially-submitted batch no longer pre-checks already-submitted cheques.

---

## v0.3.1-alpha — 2026-08-01 (Settings TDZ Fix + Type Filter)

**Issues reported:**
1. Job Profiling loads → click Customer Profiling → empty → Job Profiling again still empty.
2. No way to filter Reconcile Cheques by cheque type; reject cheques invisible.

**Fixed:**
- **Root cause:** JS Temporal Dead Zone bug in `renderSettingsCustomers()` — `const terms=terms.filter(...)` shadowed the outer `terms` variable → `ReferenceError: Cannot access 'terms' before initialization` whenever ≥1 customer existed → poisoned all settings pages.
- Cheque **type filter** added (All / 🏦 Bank In / 🔴 Return / 🔀 Mixed) in Reconcile Cheques.
- Batch type detection now recognizes **mixed** batches (previously any batch with a mix of bank-in + rejected was labeled Bank-In, hiding rejects).

---

## v0.3.0-alpha — 2026-07-31 (Perf Fix + Per-Cheque Verify)

**Issues reported:**
1. Document upload at Reconciliation "freezes" — nothing seems to happen, but repeated clicks duplicate receipts.
2. Verification cannot verify/reject individual cheques — whole batch only.
3. Confirm in Verification seems unresponsive — after refresh the batch shows confirmed.

**Fixed:**
- **Root cause (all 3):** every receipt upload / verify action rebuilt the ENTIRE modal → heavy, froze visually, and duplicated on retry.
- Receipt upload now updates **only the receipt section in place** (`renderReceiptList`) — cheque checkboxes and focus preserved, no modal rebuild.
- Verification modal now shows per-cheque checkboxes with **✅ Verify Selected / ❌ Reject Selected** — accept/reject individual entries.
- Version label shown in sidebar (`ChequeSense v0.3.0-alpha`).

---

## v0.2.0-alpha — 2026-07-29 (Incident Workflow + Cheque Timeline)

**Issues reported:**
1. Settings pages (User Admin / Customer Profile / Job Profile) appear empty.
2. Incident has no workflow — one "Resolve" button only. No accept/assign/investigate/resolve, no timeline, no remarks.
3. Reconcile Cheques flow broken: cheque selection resets after document upload; submit rejects the just-uploaded document.
4. No way to answer customer queries about a cheque's status.

**Fixed:**
- Settings pages verified working — empty pages were caused by stale browser cache of a previous broken version. Hard refresh resolves.
- Incident workflow rebuilt: **Report (auto) → Accept (Process Admin) → Assign (investigator) → Investigate (notes) → Resolve (outcome)**. Every step logged to a timestamped timeline shown on the incident card.
- Receipt upload now **preserves checkbox selection** and keeps `_receiptUploaded` flag true after re-render — submit accepts the uploaded document.
- New **Cheque Timeline** page (🔍 sidebar): search by cheque number / location / batch / customer. Shows collection date, upload date, action taken + who updated/verified, action date, and closed/pending status.

---

## v2.5 — 2026-07-29 (Settings UX + Verification Filters)

**Issues reported:**
1. Top tabs still appear for User Admin / Customer Profiling / Job Profiling — sidebar menu is sufficient.
2. Customer Profiling not working.
3. Verification page needs the same filters as Reconcile Cheques.
4. Action (Bank In / Return) needs a date to be logged with the cheque.
5. Partial submit allows "Return to Customer" without a document upload — document must be mandatory for Bank In / Return.

**Fixed:**
- Removed top tab bar from Settings; sidebar items now switch content directly.
- Customer Profiling: added safety defaults for `DB.customers` / `DB.customerMap`.
- Verification page: added search, branch filter, and date range filters.
- Added **Action Date** picker in batch modal (defaults to today); saved as `actionDate` on each cheque.
- Each Bank In / Return submission now requires a **fresh receipt upload** (old receipts don't count).

---

## v2.4 — 2026-07-29 (Branch Deletion Guard)

**Issues reported:**
1. Branch card ✕ button could accidentally unassign all terminals under a branch.

**Fixed:**
- Branch deletion now requires typing **"UNASSIGN BRANCH"** in a confirmation modal before the Delete button enables.

---

## v2.3 — 2026-07-29 (Cards + Login Hotfix)

**Issues reported:**
1. Login stopped working (admin / admin123).
2. Reconcile Cheques cards single-column; cards not clickable.

**Fixed:**
- Removed an extra `}` (patch artifact) that broke the whole script — login restored.
- Removed nested `.batch-grid` wrapper — cards are now direct children → multi-column grid.
- Fixed stale `receiptData` reference in `openBatchModal` (renamed to `receiptArr`) — cards now open the modal.

---

## v2.2 — 2026-07-29 (Sidebar + Filters)

**Issues reported:**
1. Collapsed sidebar can't reopen; page goes behind sidebar.
2. Reconcile Cheques cards not split by type; need action selection; collection date not shown.
3. Multiple status selection needed; Closed off by default; cards need cleaner stacking.

**Fixed:**
- Sidebar made static (no collapse).
- Multi-select status pills (Closed off by default); unified card grid with type badges.
- Action dropdown (Bank In / Return / Missing / Others) before receipt upload.
- Collection date shown on cards, modal header, verification cards, history table.

---

## v2.1 — 2026-07-29 (Settings Fix)

**Issues reported:**
1. Settings sub-tabs empty (User Admin, Customer Profiling, Job Profiling).

**Fixed:**
- Root cause: `switchPage()` routed settings-* inside `if(page)` but no `page-settings-users` div exists → block skipped. Moved settings routing outside the page check.

---

## v2.0 — 2026-07-28 (Theme + Logo + Report Builder)

**Issues reported:**
1. Logo colours wrong; Settings not a dropdown; password change needs old password; admin must see passwords; LLM report builder wanted.

**Fixed:**
- Corporate RED/BLACK/WHITE theme; "CHEQUE" red + "Sense" white.
- Settings as sidebar dropdown with 3 sub-items.
- Change Password modal with old-password validation; admin sees current passwords.
- Report Builder (template-based, no LLM) with date range + customer filter.

---

## v1.0 — 2026-07-27 (Initial Launch)

- First deploy: login, dashboard, import PDF, batch cards, verification, history.
- GitHub Pages: https://svanan1988.github.io/cheque-recon/
