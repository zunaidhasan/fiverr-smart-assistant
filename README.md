# Freelancer Context Assistant 🎯

> Internal operating system for Fiverr freelancers — analyzes project history, matches buyer messages, and optimizes proposals.

## Features

### 1. 🤖 Smart Reply Generator
- Input a buyer's message + optional situation type
- Auto-detects project type (urgent, technical, creative, etc.)
- Generates a personalized draft reply using similar past projects
- Suggests tone, questions to ask, and estimated quote range

### 2. 🔍 Project Similarity Search
- Paste a new client's brief
- TF-IDF powered search finds the most similar past projects
- Shows match percentage, budgets, ratings, and outcomes

### 3. 📝 Proposal Optimizer
- Full proposal structure recommendations
- Best portfolio examples to mention from your history
- Risk signals and questions to ask
- Timeline and budget estimates

### 4. ⚠️ Risk Detector
- Analyzes buyer messages for red flags
- Detects: vague requirements, urgency pressure, scope creep signals, budget mismatches
- Provides actionable recommendations

### 5. 📊 Deal Intelligence Dashboard
- KPIs: total revenue, avg budget, completion time, repeat rate
- Charts: budget by category, monthly revenue, revenue distribution
- Best paying niches and fastest project types

### 6. 📋 CRM for Fiverr
- Track all buyers, projects, and proposal statuses
- Close probability estimates
- Pipeline value tracking
- Risk flag indicators and follow-up management

## Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 18+

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
# Server runs on http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# App runs on http://localhost:3000
```

### Using Your Own Data
Upload your Fiverr project CSV via the app UI. Expected columns:
`project_id, title, category, subcategory, buyer_name, buyer_message, budget, currency, timeline_days, status, completion_time_days, revisions_count, rating, review_text, reply_template_used, was_repeat_client, start_date, end_date, notes`

A sample CSV with 30 projects is included at `sample_data/fiverr_projects.csv`.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/csv/status` | GET | Check CSV load status |
| `/api/csv/upload` | POST | Upload CSV file |
| `/api/reply/generate` | POST | Generate smart reply |
| `/api/reply/detect-situation` | POST | Auto-detect situation type |
| `/api/reply/templates` | GET | List all reply templates |
| `/api/similarity/search` | POST | Find similar projects |
| `/api/proposal/optimize` | POST | Optimize proposal structure |
| `/api/risk/analyze` | POST | Analyze message risks |
| `/api/dashboard/metrics` | GET | Dashboard KPIs |
| `/api/crm` | GET | CRM data |
| `/api/projects` | GET | List all projects |

## Tech Stack

- **Backend**: Python, FastAPI, scikit-learn, pandas
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Recharts
- **AI**: TF-IDF + cosine similarity for project matching
