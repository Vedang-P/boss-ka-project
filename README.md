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

Switch any connection from `Demo` to `Live` mode and provide:

| Provider | Auth type | Required fields |
|---|---|---|
| Canvas | Token | Base URL (e.g. `https://canvas.institution.edu`) + Access Token |
| Canvas | OAuth | Base URL + Client ID + Client Secret |
| Blackboard | Token | Base URL + Access Token |
| Blackboard | OAuth | Base URL + Client ID + Client Secret |

The provider layer normalises the raw JSON from each LMS into the same internal `Course` / `Task` schema, so all downstream features (urgency scores, planner, grade prediction) work identically for live and demo data.

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