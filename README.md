# Academic Deadline & Assignment Aggregator

A Django web application that aggregates deadlines from Canvas and Blackboard into a unified student dashboard with smart prioritization, workload warnings, grade prediction, and an in-app study planner.

## Features

- Django authentication with student signup/login
- Canvas and Blackboard connection setup with demo or live modes
- Demo-backed LMS sync pipeline for grading and presentation
- Unified dashboard for imported and manual academic tasks
- Urgency scoring based on due date, weight, difficulty, and time required
- Workload heat warnings for busy days and weeks
- What-if grade prediction
- Study planning from weekly availability windows

## Local Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

## Demo Flow

1. Sign up for an account.
2. Add a Canvas connection in `demo` mode.
3. Add a Blackboard connection in `demo` mode.
4. Sync both providers.
5. Review the dashboard, add a manual task, configure study availability, and generate a study plan.

## Live Integration Notes

The provider layer includes live-mode validation and API client scaffolding for Canvas and Blackboard. Demo mode is enabled by default so the project remains fully testable without institutional credentials.
