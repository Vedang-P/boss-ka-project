# Study Atlas

Study Atlas is a Django-based academic workload dashboard built for students who need one place to track assignments, exams, deadlines, grade impact, and study planning. It combines imported LMS data with manual tasks, then turns that data into a priority-ranked dashboard, workload warnings, grade predictions, and auto-generated study sessions.

The project is intentionally built as a classic server-rendered Django application:

- Backend: Python + Django
- Frontend: Django templates + custom CSS + vanilla JavaScript
- Database: SQLite locally, PostgreSQL in production
- Deployment target: Vercel (Python runtime)

## What the app does

- Aggregates coursework from Canvas and Blackboard through a shared LMS integration layer
- Supports demo-backed LMS connections for showcase and grading use, even without real institutional access
- Lets students add manual tasks that behave exactly like imported ones inside the dashboard, planner, and analytics
- Scores each task using due date, weight, difficulty, and estimated effort
- Warns users when specific days become overloaded
- Predicts grades with a what-if calculator
- Generates study sessions from recurring weekly availability

## Core features

### Unified dashboard

- Upcoming tasks across all connected LMS sources and manual entries
- Counts for due today, overdue, high-priority, completion percentage, and predicted grade
- Workload heatmap for the next two weeks
- Task explorer with search, filters, and completion toggles
- Upcoming study sessions and sync/health visibility

### Smart prioritization

Each task gets an urgency score out of 100 using:

- Due date proximity
- Weight toward the final grade
- Estimated hours required
- Difficulty level

This score drives task ordering, dashboard emphasis, and planning behavior.

### Grade prediction

- Per-course projected grade
- Overall projected grade
- Support for hypothetical future scores on open tasks
- Uses explicit task weights first, then grade component weights where needed

### Study planner

- Weekly recurring availability slots
- Automatic study block generation before deadlines
- Generated sessions stored in Django models so they can be displayed and updated later

### LMS integration

- Canvas provider
- Blackboard provider
- Demo mode for both providers using realistic JSON fixtures
- Live mode scaffolding with token/OAuth credential support
- Sync logs with success/failure tracking

## Django architecture

This is a multi-app Django project. Each app owns one slice of the product.

### `/accounts`

Responsible for user-facing identity and preferences.

- Signup flow
- Profile editing
- `StudentProfile` model
- Showcase user seed command

Important model:

- `StudentProfile`
  - timezone
  - preferred daily study hours
  - course load note

### `/academics`

Responsible for the academic domain model and manual task CRUD.

Important models:

- `Course`
- `GradeComponent`
- `Task`

Important responsibilities:

- manual task create/edit/delete
- task completion toggling
- priority score persistence on save

### `/integrations`

Responsible for LMS connections and imports.

Important models:

- `LMSConnection`
- `SyncLog`

Important responsibilities:

- connection creation and management
- demo/live mode switching
- provider abstraction
- payload normalization into local Django models
- sync on login for due connections

### `/analytics_app`

Responsible for analytical logic.

Important services:

- urgency score calculation
- workload summary generation
- per-course grade projection
- overall grade projection

### `/planner`

Responsible for study scheduling.

Important models:

- `StudyAvailability`
- `StudySession`

Important responsibilities:

- saving weekly availability
- generating study sessions from task urgency and free time
- updating session status

### `/dashboard`

Responsible for the main authenticated homepage.

Important responsibilities:

- gathering data from academics, analytics, integrations, and planner
- rendering the main showcase view
- surfacing empty states and top-level metrics

## Data flow

The project follows a clear server-side flow:

1. A user creates an LMS connection
2. The connection syncs through a provider
3. Provider payloads are normalized into local Django models
4. Dashboard, planner, and analytics read only from local models
5. This keeps the app fast, deterministic, and demo-friendly

That design is important because the app does not depend on live LMS availability to render the dashboard.

## Demo-backed integrations

Real institutional Canvas/Blackboard access is not required for the project to work.

The demo mode uses fixture payloads stored in:

- `/Users/vedang/boss ka project/integrations/demo_data/canvas_demo.json`
- `/Users/vedang/boss ka project/integrations/demo_data/blackboard_demo.json`

These fixtures are passed through the same sync pipeline as live data, so the rest of the app does not care whether the source is demo or live.

## Showcase account

The repo includes a built-in demo account for presentation and evaluation.

- Name: `Sarvesh Kumar`
- Username: `sarvesh`
- Password: `StudyAtlas@123`

This account is seeded through a Django management command:

```bash
python manage.py seed_showcase_user
```

The seed command:

- creates or refreshes the user
- syncs demo Canvas and Blackboard connections
- adds manual tasks
- adds weekly study availability
- generates study sessions

The same command is run automatically in the Vercel build script so the showcase account exists on deployed builds too.

## Tech stack

### Backend

- Python
- Django
- Django ORM
- WhiteNoise
- dj-database-url
- psycopg (for PostgreSQL in production)

### Frontend

- Django templates
- custom CSS design system
- vanilla JavaScript

### Database

- SQLite for local development
- PostgreSQL via `DATABASE_URL` in production

### Deployment

- Vercel Python runtime

## Local development

### 1. Create a virtual environment

```bash
cd "/Users/vedang/boss ka project"
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Seed the showcase account

```bash
python manage.py seed_showcase_user
```

### 5. Start the development server

```bash
python manage.py runserver
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/accounts/login/`

## Production configuration

The project is configured to use environment variables for production behavior.

Required variables:

```bash
DJANGO_SECRET_KEY="replace-with-a-long-random-secret"
DJANGO_DEBUG="false"
DJANGO_ALLOWED_HOSTS=".vercel.app"
DJANGO_CSRF_TRUSTED_ORIGINS="https://your-project.vercel.app"
DATABASE_URL="postgresql://..."
```

Optional secure-production toggles:

```bash
DJANGO_SECURE_SSL_REDIRECT="true"
DJANGO_SECURE_HSTS_SECONDS="31536000"
```

## Vercel deployment

The repository includes the files needed for Django on Vercel:

- `/Users/vedang/boss ka project/vercel.json`
- `/Users/vedang/boss ka project/api/index.py`
- `/Users/vedang/boss ka project/build_files.sh`

Build behavior:

1. `migrate`
2. `seed_showcase_user`
3. `collectstatic`

That means the production deployment automatically:

- applies schema updates
- seeds the showcase user
- prepares static files

## Testing

Run the full suite with:

```bash
python manage.py test
```

The test suite currently covers:

- signup and profile flows
- showcase seeding
- manual task CRUD
- dashboard rendering
- integration sync behavior
- planner generation behavior
- deployment-related configuration checks

## Manual showcase flow

For a presentation, log in as the seeded demo user:

- Username: `sarvesh`
- Password: `StudyAtlas@123`

Then walk through:

1. Dashboard metrics and upcoming tasks
2. Imported LMS coursework from Canvas and Blackboard demo connections
3. Manual tasks mixed into the same dashboard
4. Grade prediction page
5. Study availability page
6. Generated study sessions

## Why Django was the right choice here

This project benefits from Django because it needs:

- relational data modeling
- secure authentication
- strong admin/debuggability
- fast server-rendered dashboards
- form handling and validation
- a clean separation between domain apps

For an academic management tool with several interacting modules, Django gives a stable backend foundation without forcing unnecessary frontend complexity.
