# Study Atlas — Academic Deadline & Assignment Aggregator

A full-stack Django web application that pulls assignments, exams, and deadlines from Canvas and Blackboard into a single intelligent dashboard. It goes beyond passive listing by computing urgency scores, visualising weekly crunch periods, projecting course grades, and auto-generating personalised study sessions.

---

## Features

### Unified Dashboard
- Aggregated view of every task across all connected LMS platforms and manual entries
- Live stat cards: upcoming tasks, due today, high-priority open, overdue, and projected grade
- Overall completion progress bar

### Smart Prioritisation (Urgency Score)
Each task is scored out of 100 using four components:
| Component | Weight | Logic |
|---|---|---|
| Due date proximity | up to 45 pts | Linear decay over 14 days; overdue tasks cap at 45 |
| Assignment weight | up to 30 pts | Direct percentage of final grade |
| Estimated time required | up to 10 pts | Hours × 2, capped at 10 |
| Difficulty | 5 / 10 / 15 pts | Easy / Medium / Hard |

### Task Explorer
- Search by task title or course name
- Filter chips: All · High Priority · Due Soon · Exam & Quiz · Manual · Open Only
- Instant AJAX completion toggle (no page reload) — updates the pill, row style, and filter count live
- Edit / Delete shortcut links on manually created tasks

### Workload Radar
- 7-day intensity bar chart with colour-coded levels (low / medium / high)
- Automatic high-intensity day warnings

### Grade Prediction (What-If Calculator)
- Enter hypothetical scores for any open task
- Instant weighted projection per course and overall GPA estimate
- Filter by individual course

### Automated Study Planner
- Set recurring weekly availability windows (any day, any start/end time)
- One-click plan generation that slots 1-hour study blocks before each deadline
- Respects a daily 4-hour study cap to prevent over-scheduling
- Remove individual availability slots without clearing the whole schedule

### LMS Integration
- Canvas and Blackboard providers with **demo mode** (built-in fixture data) and **live mode** (real API credentials)
- Token and OAuth2 authentication types supported
- Per-connection sync with full sync log history (status, item count, timestamps)
- Manage connections page: view health, sync individually, or delete with cascade removal of all imported data

### Profile & Preferences
- Set timezone, preferred daily study hours, and a course load note
- Preferences feed into planner slot generation

### Auth & Security
- Django built-in authentication (signup, login, logout)
- Auto-created `StudentProfile` via signal on user registration
- All views protected with `@login_required`
- Environment-variable-driven production hardening (HSTS, SSL redirect, secure cookies)
- Light / Dark theme toggle with `localStorage` persistence

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13 · Django 6.0 |
| Database | SQLite (dev) · PostgreSQL-compatible |
| Frontend | HTML5 · CSS3 (custom design system) · Vanilla JavaScript (ES2020) |
| HTTP client | `requests` (live LMS API calls) |
| Auth | Django built-in + OAuth2 credential scaffolding |

---

## Project Structure

```
.
├── academics/          # Course, GradeComponent, Task models + manual task CRUD
├── accounts/           # StudentProfile, signup, login, profile settings
├── analytics_app/      # Urgency scoring, workload summary, grade projection services
├── config/             # Django settings, root URL conf, WSGI/ASGI
├── dashboard/          # Main dashboard view + dashboard_extras templatetag
├── integrations/       # LMSConnection, SyncLog, Canvas/Blackboard providers, sync service
├── planner/            # StudyAvailability, StudySession, study plan generator
├── static/
│   ├── css/styles.css  # Full custom design system (light + dark themes)
│   └── js/app.js       # Theme toggle, scroll reveals, task explorer, AJAX toggle
├── templates/
│   ├── base.html
│   ├── academics/      # Manual task form, edit form, delete confirmation
│   ├── accounts/       # Signup, login, profile
│   ├── analytics_app/  # Grade prediction / what-if calculator
│   ├── dashboard/      # Main dashboard home
│   ├── integrations/   # Add connection, manage connections, delete confirmation
│   └── planner/        # Availability slots page
├── integrations/
│   ├── demo_data/      # canvas_demo.json · blackboard_demo.json
│   └── providers/      # BaseLMSProvider, CanvasProvider, BlackboardProvider
├── manage.py
└── requirements.txt
```

---

## Local Setup

```bash
# 1. Clone the repo and enter the project directory
git clone <repo-url>
cd "boss ka project"

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Create your account (or use the signup page)
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

---

## Environment Variables

The project reads optional environment variables so development and production share the same codebase.

```bash
# Required in production — use a long random value
DJANGO_SECRET_KEY="replace-with-a-50-char-random-string"

# Set to "false" in production
DJANGO_DEBUG="true"

# Comma-separated list of hostnames
DJANGO_ALLOWED_HOSTS="127.0.0.1,localhost"

# Required if you serve behind a proxy or use HTTPS
DJANGO_CSRF_TRUSTED_ORIGINS="http://127.0.0.1:8000"
```

For a production-like deployment:

```bash
DJANGO_DEBUG="false"
DJANGO_SECURE_SSL_REDIRECT="true"
DJANGO_SECURE_HSTS_SECONDS="31536000"
```

---

## Demo Flow (No LMS Credentials Required)

1. **Sign up** at `/accounts/signup/`.
2. Navigate to **LMS** in the top nav → **Add connection**.
3. Create a connection: provider `Canvas`, mode `Demo`, any display name. Save.
4. Create a second connection: provider `Blackboard`, mode `Demo`. Save.
5. Click **Sync all** — the app imports 4 courses and 8 tasks with realistic due dates.
6. Return to the **Dashboard** to see priority scores, workload radar, and grade projection.
7. Open **Grades** (top nav) and enter hypothetical scores in the what-if calculator.
8. Go to **Planner** → add a few weekly availability slots (e.g. Monday 09:00–17:00).
9. Click **Generate study plan** on the dashboard — sessions are scheduled automatically.
10. Toggle individual tasks as done directly from the dashboard using the **Done** button.

---

## Live LMS Integration

The provider layer normalises raw JSON from each LMS into the same internal `Course` / `Task` schema, so urgency scores, grade prediction, and the study planner work identically for live and demo data.

---

### Canvas — Personal Access Token (Recommended)

Canvas personal access tokens work on any Canvas instance including the free **canvas.instructure.com** accounts. No admin approval is needed.

#### Step 1 — Generate your token on the Canvas website

1. Log in to your Canvas instance (e.g. `https://canvas.instructure.com`).
2. Click your profile picture (top-left) → **Account → Settings**.
3. Scroll down to **Approved Integrations**.
4. Click **+ New Access Token**.
5. Give it a purpose (e.g. *Study Atlas*) and an optional expiry date.
6. Click **Generate Token** and copy the token — it is shown only once.

> **Your Canvas base URL** is the root of the site you logged in to, e.g. `https://canvas.instructure.com`. Do not append any path.

#### Step 2 — Add the connection in Study Atlas

1. Go to **LMS → Add connection**.
2. Fill in the form:

| Field | Value |
|---|---|
| Display name | Canvas Live (or any label) |
| Provider | Canvas |
| Mode | **Live** |
| Auth type | **Token** |
| Base URL | `https://canvas.instructure.com` (or your institution's URL) |
| Access token | the token you copied in Step 1 |

3. Click **Save connection**, then **Sync** to import your real courses and assignments.

---

### Blackboard — OAuth2 Application (Client Credentials)

Blackboard uses OAuth2 instead of personal tokens. You need to register an application in the **Anthology Developer Portal** to get a Client ID and Secret.

#### Step 1 — Register your application (one-time)

1. Go to **[developer.anthology.com](https://developer.anthology.com)** and sign in (or create a free account).
2. Navigate to **My Applications → Register**.
3. Fill in the application name, description, and domain.
4. Under **API Access**, select the scopes you need:
   - `Course: Read` — to list enrolled courses
   - `Gradebook: Read` — to list gradebook columns / assessments
5. Submit. Once approved, the portal shows you:
   - **Application Key** — this is your **Client ID**
   - **Secret** — this is your **Client Secret**
   - **Application ID** — internal identifier (not needed in Study Atlas)

> **Important:** You also need a Blackboard Learn instance URL to point the app at. Anthology provides developer sandbox instances — check your developer portal account for the sandbox URL assigned to your application (format: `https://[sandbox-id].blackboard.com`).

#### Step 2 — Authorise your application on the Blackboard instance

1. Log in to your Blackboard instance as an administrator (or use the developer sandbox admin).
2. Go to **System Admin → REST API Integrations**.
3. Click **Create Integration**.
4. Paste your **Application ID** into the *Application ID* field.
5. Set *Learn User* to an account with course-read permissions (your own account works on a sandbox).
6. Set *End User Access* to **Yes** and *Authorised to Act as User* to **Service Default (Yes)**.
7. Click **Submit**.

#### Step 3 — Add the connection in Study Atlas

1. Go to **LMS → Add connection**.
2. Fill in the form:

| Field | Value |
|---|---|
| Display name | Blackboard Live (or any label) |
| Provider | Blackboard |
| Mode | **Live** |
| Auth type | **OAuth** |
| Base URL | your Blackboard instance URL (e.g. `https://[sandbox-id].blackboard.com`) |
| Client ID | your Application Key |
| Client secret | your Secret |

3. Click **Save connection**, then **Sync**.

> **How it works under the hood:** On sync, Study Atlas POSTs to `{base_url}/learn/api/public/v1/oauth2/token` with `grant_type=client_credentials` and Basic auth to obtain a short-lived Bearer token, then uses that token for all subsequent API calls. The token is never stored permanently.

---

### Credentials Security Note

- Tokens and secrets are stored only in the local SQLite database and masked in the UI (shown as `****`).
- Never commit `db.sqlite3` to version control — it is already listed in `.gitignore`.
- For a production deployment, rotate credentials regularly and use environment variables for `DJANGO_SECRET_KEY`.

---

## URL Reference

| URL | View | Description |
|---|---|---|
| `/` | `dashboard:home` | Main dashboard |
| `/accounts/signup/` | `accounts:signup` | Register |
| `/accounts/login/` | `login` | Login |
| `/accounts/profile/` | `accounts:profile` | Profile & preferences |
| `/integrations/manage/` | `integrations:manage` | List / manage all LMS connections |
| `/integrations/connect/` | `integrations:connection_create` | Add new LMS connection |
| `/integrations/<pk>/sync/` | `integrations:connection_sync` | Sync one connection |
| `/integrations/sync-all/` | `integrations:connection_sync_all` | Sync all connections |
| `/integrations/<pk>/delete/` | `integrations:connection_delete` | Remove connection |
| `/academics/manual/new/` | `academics:manual_task_create` | Add manual task |
| `/academics/task/<pk>/edit/` | `academics:task_edit` | Edit manual task |
| `/academics/task/<pk>/delete/` | `academics:task_delete` | Delete manual task |
| `/academics/task/<pk>/toggle/` | `academics:task_toggle_complete` | Toggle done (JSON) |
| `/planner/availability/` | `planner:availability` | Manage availability slots |
| `/planner/slot/<pk>/delete/` | `planner:slot_delete` | Remove availability slot |
| `/planner/generate/` | `planner:generate` | Generate study sessions |
| `/planner/session/<pk>/status/` | `planner:session_update_status` | Update session status (JSON) |
| `/analytics/grade-prediction/` | `analytics_app:grade_prediction` | What-if grade calculator |

---

## Implementation Phases

| Phase | Scope | Status |
|---|---|---|
| 1 | Requirements analysis and database schema design | ✅ Complete |
| 2 | LMS API integration and demo data sync pipeline | ✅ Complete |
| 3 | Frontend dashboard, task explorer, and all page templates | ✅ Complete |
| 4 | Grade prediction, urgency scoring, and study planner logic | ✅ Complete |
| 5 | Full CRUD (edit/delete tasks, manage connections, availability slots), AJAX interactions, profile settings, UI refinement | ✅ Complete |
```

Now let me commit everything: