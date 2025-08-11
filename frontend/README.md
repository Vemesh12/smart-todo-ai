# Smart Todo AI

Full‑stack Smart Todo List with AI‑powered prioritization, deadlines, and context‑aware enhancements.

## Features
- tasks: create/list/update with priority score, deadline, status, categories
- categories: simple tagging with usage counts
- context: capture daily notes/emails/WhatsApp with derived insights (keywords, sentiment)
- AI pipeline:
  - Priority scoring from task/context
  - Deadline suggestion with workload awareness
  - Smart category suggestion
  - Description enhancement from context
  - Optional LM Studio integration for richer text
- Frontend: modern minimal UI (NextJS + Tailwind) with priority indicators, filters, AI suggest/apply

## Tech Stack
- Backend: Django 5 + Django REST Framework
- Database: PostgreSQL (recommended; required for submission). SQLite fallback for local dev only
- Frontend: Next.js + React + Tailwind CSS
- AI: Heuristic pipeline + optional LM Studio local LLM

## Prerequisites
- Python 3.11+ (3.13 supported)
- Node 20+
- PostgreSQL 13+
- (Optional) LM Studio running locally if you want enhanced AI text

## Backend Setup (PostgreSQL)
Create DB and user (in psql as superuser `postgres`). If you already have a DB/user, skip to env.

```sql
CREATE DATABASE smarttodo;
CREATE USER smarttodo_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE smarttodo TO smarttodo_user;
```

Create `backend/.env`:
```
POSTGRES_DB=smarttodo
POSTGRES_USER=smarttodo_user
POSTGRES_PASSWORD=strong_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Install deps, migrate, load sample data, run server (Windows PowerShell):
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixtures\sample_data.json  # optional
python manage.py runserver 0.0.0.0:8000
```

Troubleshooting Postgres permissions
If you see “permission denied for schema public” or missing tables after switching from SQLite, fix ownership/privileges and re-run migrate:
```sql
ALTER DATABASE smarttodo OWNER TO smarttodo_user;
\c smarttodo
ALTER SCHEMA public OWNER TO smarttodo_user;
GRANT ALL ON SCHEMA public TO smarttodo_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO smarttodo_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO smarttodo_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO smarttodo_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO smarttodo_user;
```
Then:
```powershell
python manage.py migrate
```

## Frontend Setup
```powershell
cd frontend
npm install
npm run dev
# open http://localhost:3000
```
Optional: set `frontend/.env.local` if your API base differs:
```
NEXT_PUBLIC_API_BASE=http://localhost:8000/api
```

## API Overview (Base: http://localhost:8000/api)
- GET `/tasks/` — list tasks (filters: `status`, `category`, `min_priority`, `search`)
- POST `/tasks/` — create task
- POST `/tasks/{id}/ai-refresh/` — recompute priority/deadline/category from latest context
- GET/POST `/categories/` — list/create categories
- GET `/context/`, `/context/latest/` — list context entries / latest 10
- POST `/context/` — add context
- POST `/ai/suggest/` — AI suggestions

Example create task body:
```json
{
  "title": "Prepare weekly report",
  "description": "Summarize KPIs",
  "category": 1,
  "priority_score": 0.8,
  "deadline": "2025-08-15T10:00:00Z",
  "status": "todo"
}
```

## Data Model
- `tasks_task`: title, description, category, priority_score, deadline, status, created_at, updated_at
- `tasks_category`: name (unique), description, usage_count, created_at, updated_at
- `context_contextentry`: content, source_type, processed_insights (JSON), created_at, updated_at

## AI Integration
- Heuristics (default): keyword urgency + context influence, sentiment/keywords, complexity, category hints, description enrichment
- LM Studio (optional):
  - Set env vars then restart Django:
    ```
    AI_PROVIDER=lm_studio
    LM_STUDIO_BASE_URL=http://localhost:1234/v1
    LM_STUDIO_MODEL=qwen2.5:latest
    ```

## Sample Data
- Backend fixtures: `backend/fixtures/sample_data.json`
  - Load with `python manage.py loaddata fixtures/sample_data.json`


## Example AI Suggestions
Input: "Prepare weekly report" with context about urgent client meeting  
Output:
- Priority Score: 0.92 (High)
- Suggested Deadline: 2025-08-12 17:00
- Suggested Category: Reports
- Enhanced Description: "Prepare detailed weekly report with KPIs and key insights for client meeting."


#screenshots
Screenshot (7).png
Screenshot (8).png
<img width="1920" height="1080" alt="Screenshot (7)" src="https://github.com/user-attachments/assets/323ddd41-743d-4bec-a6c3-0bb2070db409" />
