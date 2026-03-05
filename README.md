# PriceIntel - SaaS Price Comparison

A production-ready SaaS application for searching and comparing product prices globally across Amazon India and Flipkart.

## Technology Stack
- **Frontend**: Next.js 14, TailwindCSS, Chart.js, Axios
- **Backend**: Python FastAPI, Celery, PostgreSQL, Redis, Async Playwright
- **Authentication**: JWT Auth

## Prerequisite Services
Ensure you have the following installed and running locally:
1. PostgreSQL (e.g., `postgresql://postgres:postgres@localhost:5432/priceintel`)
2. Redis (e.g., `redis://localhost:6379/0` and `redis://localhost:6379/1`)

## Setup Instructions

### Backend Setup
1. Open a terminal and navigate to exactly `backend/`.
2. Create and activate a Virtual Environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install Playwright browser binaries:
   ```bash
   playwright install chromium
   ```
5. Start the FastAPI development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Open a second terminal and navigate to exactly `frontend/`.
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

### Usage
- Open `http://localhost:3000` to access the PriceIntel UI.
- API documentation is available at `http://localhost:8000/docs`.
- First, register an account on the client side, login, and then use the dashboard to search for products (e.g. `iPhone`).

### Background Tasks (Celery)
To enable the background task functionality via Celery, open a new terminal under `backend/`, activate the venv, and run:
```bash
celery -A core.celery_app worker --loglevel=info
```
