# AEO-Answerable

**"Lighthouse for Answer Engines"** — Audit your website for AI Answer Engine Optimization (AEO).

## 🚀 Quick Start

### 1. Backend Setup (Django)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database Setup
python3 django_app/manage.py migrate

# Start Server
python3 django_app/manage.py runserver
```

### 2. Frontend Setup (React/Vite)

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to start using the dashboard.

## 🛠️ Key Commands

- **Run Scan**: Use the dashboard UI to initiate scans.
- **Crawler Fix**: If you see duplicates, the crawler now auto-normalizes URLs.
- **Theme**: Toggle Light/Dark mode in the navbar.

## 🏗️ Architecture

- **Backend**: Django (API, Database, Crawler Logic)
- **Frontend**: React + Vite + Tailwind CSS (Dashboard, Reports)
- **Crawler**: Custom Python crawler with Playwright support (`rendered` mode).

---
*Built for the age of AI-powered search.*
