# ChequeSense — Change Log

> Reference document. Each version lists: reported issues → what was fixed.
> Latest first.

---

## v2.6 — 2026-07-29 (Incident Workflow + Cheque Timeline)

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
