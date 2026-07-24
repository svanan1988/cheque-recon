# Power Pages — Cheque Tracking & Reconciliation

> **Complete blueprint to build the site.**
> Zero-friction design: Admin uploads PDF → Drivers upload proof → Verifier confirms.

---

## 1. Role Model (Managed by Page Admin)

| Role | Permissions | What they see |
|---|---|---|
| **Process Admin** | Upload PDFs, view all jobs, re-import | Full dashboard + Import page + All locations |
| **User** (Driver) | View assigned jobs, upload proof, mark done | Only their location's cheques + camera/upload |
| **Verifier** | View verification queue, approve/reject proofs | Only "Awaiting Verification" jobs + proof viewer |

**Rule:** One person can have **multiple roles**. E.g., a User at a small location can also be the Verifier for that location.

### How roles work in Power Pages

Power Pages uses **Web Roles** assigned to **Contacts**:

```
Contact Record (User)
  ├── Web Role: "Process Admin"  ☑
  ├── Web Role: "User"           ☑  
  └── Web Role: "Verifier"       ☐
```

**Setup by Page Admin:**
1. Go to Power Pages → Admin → Users
2. Find or create the Contact
3. Check which Web Roles they get
4. Done — roles apply immediately on next login

**Available Web Roles to create in Power Pages admin:**
- `Process Admin` — can access `/admin/*` pages
- `User` — can access `/my-jobs` and `/job/*` 
- `Verifier` — can access `/verify/*`

---

## 2. Data Model (Dataverse Tables)

### Table 1: `Cheque Jobs` — Main transaction table

| Column | Type | Purpose |
|---|---|---|
| `cr641_chequejobid` | GUID (PK) | Auto |
| `cr641_name` | Text | Title: `{Terminal}-{ChequeNo}` |
| `cr641_terminal` | Text | e.g., ASTR01 |
| `cr641_location` | Text | e.g., Alor Setar |
| `cr641_batchno` | Text | Collection batch number |
| `cr641_tranno` | Text | Transaction number |
| `cr641_chequeno` | Text | Cheque number |
| `cr641_amount` | Currency | In RM |
| `cr641_bank` | Choice | Maybank, CIMB, Public Bank, etc. |
| `cr641_jobtype` | Choice | `Bank-In`, `Return Rejected` |
| `cr641_rejectreason` | Text | Only for rejected type |
| **`cr641_status`** | **Choice** | **`Pending` → `In Progress` → `Awaiting Verification` → `Verified` → `Closed`** |
| `cr641_assignedto` | Lookup (User) | The driver responsible |
| `cr641_prooffile` | File/Image | Uploaded bank-in slip or return receipt |
| `cr641_proofnotes` | Text | Optional notes from driver |
| `cr641_verifiedby` | Lookup (User) | Verifier who approved |
| `cr641_verifiedat` | Date/Time | |
| `cr641_importbatch` | Text | Links to PDF Import record |
| `cr641_importdate` | Date/Time | Date of import |
| `cr641_notes` | Text | General notes |

### Table 2: `Location Assignment` — Map terminals to drivers

| Column | Type |
|---|---|
| `cr641_terminalcode` | Text (unique) |
| `cr641_locationname` | Text |
| `cr641_assigneduser` | Lookup (Contact/User) |

Page Admin manages this table to control which driver sees which cheques.

### Table 3: `PDF Import Log` — Audit trail

| Column | Type |
|---|---|
| `cr641_filename` | Text |
| `cr641_importdate` | Date/Time |
| `cr641_totalentries` | Number |
| `cr641_totalrejected` | Number |
| `cr641_status` | Choice: `Processing`, `Completed`, `Failed` |

---

## 3. Pages (Power Pages Site)

### Page 1: `/` — Role-Based Dashboard

**Layout:**
```
┌──────────────────────────────────────────────┐
│  📋 Cheque Recon              User: Ali ▼    │
├──────────────────────────────────────────────┤
│  [ Upload PDF ]  ← Only Process Admin sees   │
├──────────────────────────────────────────────┤
│  Total: 833  │  Pending: 450  │  Verified: 380 │
├──────────────────────────────────────────────┤
│                                              │
│  ┌─── IF role=ProcessAdmin ──────────────┐  │
│  │  All Jobs by Location    ▼ filter     │  │
│  │  [ASTR01 - Alor Setar]  (12 pending) │  │
│  │  [BHAU01 - Bahau]       (8 pending)  │  │
│  │  ...                                  │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌─── IF role=User ─────────────────────┐  │
│  │  My Jobs — ASTR01 Alor Setar         │  │
│  │  🟠 Chq#150423  RM90,404  Pending    │  │
│  │  🟠 Chq#150425  RM176    Pending    │  │
│  │  🟡 Chq#158154  RM0      Awaiting   │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌─── IF role=Verifier ────────────────┐  │
│  │  Verification Queue (24 pending)    │  │
│  │  🟡 Chq#000019  RM4,002  View/Verify│  │
│  │  🟡 Chq#934010  RM681   View/Verify│  │
│  └──────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

**Power Fx for conditional visibility:**
```
// Upload button visibility
If(Contains(Roles, "Process Admin"), true, false)

// My Jobs — filter by assigned user
Filter(ChequeJobs, AssignedTo.User = CurrentUser.Email)

// Verification Queue
Filter(ChequeJobs, Status = "Awaiting Verification")
```

### Page 2: `/job/{id}` — Single Job

| Section | What it shows |
|---|---|
| Top | Cheque details (number, amount, bank, location) |
| Middle | Status badge + workflow step indicator |
| **Driver actions** | 📎 Upload bank-in slip / return receipt + Notes |
| **Verifier actions** | 👁 View uploaded proof + ✅ Confirm + ❌ Reject |
| Bottom | Audit trail (created, imported, verified dates) |

**Flow of status updates:**

```
User action:                    Verifier action:
┌─────────────┐                ┌──────────────┐
│ Upload Proof│──→ Awaiting ──→│ ✅ Confirm   │──→ Verified → Closed
│ + Mark Done │    Verification│ ❌ Reject    │──→ In Progress (re-opened)
└─────────────┘                └──────────────┘
```

### Page 3: `/admin/import` — Import History (Process Admin only)

- Table showing all uploaded PDFs with date, entry count, status
- Click to view what was imported
- Re-import button (replaces batch)

### Page 4: `/admin/users` — Role Assignment (Page Admin only)

- Simple table: Contact | Process Admin ☐ | User ☐ | Verifier ☐
- Save = immediate effect

---

## 4. Key Automation (Power Automate Flows)

### Flow 1: Parse PDF on Upload (Triggered when file added to SharePoint)

```
Trigger: When a file is created in /cheque-pdfs/ folder
Steps:
  1. Get file content
  2. Run Python script (via Azure Function or on-prem gateway)
     → Parses Bank-In or Rejected PDF
     → Returns JSON array
  3. Create record in Cheque Jobs for each entry
     → Status = "Pending"
     → Look up AssignedTo from Location Assignment table
  4. Create record in PDF Import Log
  Notify: "Imported 833 cheques from 16/07/2026 report"
```

### Flow 2: Auto-Close (Scheduled nightly)

```
Trigger: Recurrence (daily midnight)
Steps:
  1. Get all jobs where Status = "Verified" and older than 24h
  2. Set Status = "Closed"
```

### Flow 3: Reminder for Stale Jobs (Optional)

```
Trigger: Recurrence (daily 9am)
Steps:
  1. Get jobs where Status = "Pending" and ImportDate > 3 days
  2. Email assigned driver: "You have 12 cheques pending at Alor Setar"
```

---

## 5. Power Pages Setup Steps (Build in ~45 min)

### Step 1: Provision Power Pages site
- Go to https://make.powerapps.com → Power Pages
- Create new site (use "Blank page" template, not Dataverse starter)
- Name: "Cheque Recon" → choose URL → Create

### Step 2: Create Dataverse tables
- Go to Data workspace → Tables → Create new
- Create `Cheque Jobs`, `Location Assignment`, `PDF Import Log`
- Add columns as specified above

### Step 3: Create Web Roles
- Go to Admin → Users → Web Roles
- Create: `Process Admin`, `User`, `Verifier`

### Step 4: Create pages
- `/` — Dashboard page with filtered lists
- `/job/` — Detail page with forms
- `/admin/import` — Import history
- `/admin/users` — Role assignment

### Step 5: Set page permissions
- `/admin/*` — Only `Process Admin` role
- `/job/*` — `User` and `Verifier` roles
- `/` — All authenticated roles

### Step 6: Set up PDF parser
- Option A: Deploy `parse_cheque_pdf.py` as Azure Function
- Option B: Use Power Automate Desktop (on-prem gateway)
- Option C: Manual JSON upload (skip PDF parsing, admin pastes JSON)

### Step 7: Test with sample data
- Import the sample PDF → verify 833 entries appear
- Log in as driver → see only ASTR01 jobs
- Upload a test image → verify it appears in verification queue
- Log in as verifier → confirm → verify status updates

### Step 8: Publish
- Click "Sync" in Power Pages Studio
- Share URL with team

---

## 6. Key Design Decisions

| Decision | Why |
|---|---|
| **Power Pages over Canvas App** | Desktop-first web access, no app install, works on any device |
| **Dataverse over SharePoint** | Better for Power Pages, supports file/image columns, relationships |
| **3 roles, not 2** | Separation of duties: uploader ≠ executor ≠ verifier |
| **Status workflow with 5 states** | Clear visibility of where each job is in the pipeline |
| **Auto-assign by location** | No manual assignment needed — driver knows their location |
| **Proof upload in-line** | Driver takes photo from phone, uploads in 2 taps |
| **Verification queue** | Prevents fraud — someone else confirms the proof is real |

---

## 7. Permission Matrix (Page Permissions)

| Page/Component | Process Admin | User | Verifier | Unauthenticated |
|---|---|---|---|---|
| Upload PDF | ✅ | ❌ | ❌ | ❌ |
| View all jobs | ✅ | ❌ | ❌ | ❌ |
| View my jobs | ✅ | ✅ | ✅ | ❌ |
| View verification queue | ✅ | ❌ | ✅ | ❌ |
| Upload proof | ❌ | ✅ | ❌ | ❌ |
| Confirm/Reject proof | ❌ | ❌ | ✅ | ❌ |
| Import history | ✅ | ❌ | ❌ | ❌ |
| User role mgmt | Page Admin only | ❌ | ❌ | ❌ |
