# AI-Based Smart Allocation Engine for PM Internship Scheme
### Academic Prototype for B.Tech AI & Data Science Capstone Project

> **Academic Notice:** This software is an academic engineering prototype developed for demonstration, evaluation, and viva presentation. It simulates the internship recommendation, skill gap analysis, and seat allocation mechanisms of the PM Internship Scheme using synthetic data and explainable machine learning models. It is not officially affiliated with the Government of India.

---

## 1. System Architecture

```
                                  Client Browser
                       (React 18 + TypeScript + Vite + Tailwind CSS)
                                         │
                                         ▼ REST / JSON (JWT Bearer)
                        FastAPI Web API Gateway (Port 8000)
              ┌──────────────────────────┼──────────────────────────┐
              ▼                          ▼                          ▼
      Authentication & RBAC     Student & Resume Parser     Internship & Catalog
        • Bcrypt Password         • pypdf Stream Extraction   • Search & Filter
        • PyJWT HS256 Token       • Pattern-Matching NLP      • Seat Capacity
              │                          │                          │
              └──────────────────────────┼──────────────────────────┘
                                         │
                                         ▼
                 Explainable AI Matching & Allocation Engine
             ┌────────────────────────────────────────────────────────┐
             │ • TF-IDF Vectorizer & Cosine Similarity (Scikit-Learn) │
             │ • Discrete Set Overlap (70%) + Semantic Match (30%)    │
             │ • Multi-Criteria Preferences (Education, Loc, Ind)     │
             │ • Atomic Row-Locked Seat Allocation (with_for_update)  │
             │ • Duplicate Assignment Prevention                      │
             │ • Curriculum Skill Gap Diagnoser                       │
             └───────────────────────────┬────────────────────────────┘
                                         │
                                         ▼
                          Relational Database Schema
                       (PostgreSQL / SQLite + SQLAlchemy)
                     11 Normalized Tables & Alembic Migrations
```

---

## 2. Technology Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts, React Router v6, Axios.
- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy ORM, Alembic migrations, PyJWT, Native Bcrypt, pypdf.
- **AI/ML:** Scikit-learn (TF-IDF vectorizer, Cosine Similarity), NLP regex dictionary matcher, explainable scoring heuristics.
- **Database:** PostgreSQL (with SQLite zero-configuration local fallback).
- **Testing:** pytest (31 automated unit and integration tests passing).
- **Advanced Algorithms:** Gale-Shapley Student-Proposing Deferred Acceptance Algorithm (Stable Marriage with 0 blocking pairs).
- **Report Generation:** Downloadable CSV allocation registry export & automated viva walkthrough CLI script.

---

## 3. Seeded Demo Accounts for Viva / Evaluation

The database is pre-seeded with realistic scenarios:

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **System Super Admin** | `admin@pm-internship.edu.in` | `AdminSecurePass@2026` | Full administrative control, allocation engine trigger, analytics dashboard. |
| **Student 1 (Backend/Cloud)** | `rahul.sharma@pm-internship.edu.in` | `StudentPass@2026` | B.Tech CSE (CGPA 8.7), skills: Python, FastAPI, SQL, Docker. |
| **Student 2 (AI/Data Science)**| `sneha.patel@pm-internship.edu.in` | `StudentPass@2026` | B.Tech AI & DS (CGPA 9.3), skills: Python, ML, NLP, Pandas, SQL. |
| **Student 3 (Frontend)** | `aman.verma@pm-internship.edu.in` | `StudentPass@2026` | BCA (CGPA 7.6), skills: React, JavaScript, HTML5, CSS3. |

---

## 4. How to Run the Application on Windows 11

### Step 1: Start the Backend (Terminal 1)

```powershell
cd "C:\Users\Prashant Singh\.gemini\antigravity\scratch\pm-internship-allocation\backend"

# Activate Python Virtual Environment
.\venv\Scripts\Activate.ps1

# Run the FastAPI server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- **Backend Swagger UI:** Open `http://127.0.0.1:8000/docs` in your browser.

### Step 2: Start the Frontend (Terminal 2)

```powershell
cd "C:\Users\Prashant Singh\.gemini\antigravity\scratch\pm-internship-allocation\frontend"

# Install frontend dependencies (run once outside restricted environments)
npm install

# Start Vite Development Server
npm run dev
```
- **Frontend Application:** Open `http://localhost:5173` in your browser.

---

## 5. Automated Test Suite & Live Viva Walkthrough Script

### A. Run Automated Unit & Integration Tests (31 Test Cases)
```powershell
cd "C:\Users\Prashant Singh\.gemini\antigravity\scratch\pm-internship-allocation\backend"
python -m pytest -v
```
**Result:** `31 passed in 10.40s (100% green)`

### B. Run Live Interactive Demo Walkthrough
For oral examination / viva evaluation where the panel wants an automated end-to-end demonstration across all 10 modules:
```powershell
cd "C:\Users\Prashant Singh\.gemini\antigravity\scratch\pm-internship-allocation\backend"
python demo_walkthrough.py
```
This runs an 8-step live defense simulation demonstrating student profile evaluation, explainable AI recommendations, skill-gap curricula generation, duplicate application guards, atomic row-locked allocations, Gale-Shapley stability verification, and CSV export.

---

## 6. Project Directory Map

```
pm-internship-allocation/
├── README.md                              # System architecture manual & setup guide
├── run_project.bat                        # Double-click launcher for Windows 11
├── run_project.ps1                        # PowerShell launcher with ExecutionPolicy bypass
├── presentation_slides.html               # 12-slide interactive viva presentation deck
├── pm_internship_api_collection.json      # Postman API Collection (v2.1)
├── VIVA_PRESENTATION_GUIDE.md             # 3NF proofs, math equations & examiner Q&A
├── PROJECT_REPORT.md                      # Complete IEEE-style thesis report
├── PRESENTATION_SLIDES_OUTLINE.md         # PowerPoint slides structural outline
├── docker-compose.yml                     # Multi-container production orchestration
├── backend/
│   ├── .env
│   ├── requirements.txt
│   ├── seed_demo_data.py                  # Seeds 5 companies, 5 internships, 4 students
│   ├── demo_walkthrough.py                # 8-step live terminal viva simulator
│   ├── sample_resumes/                    # Test candidate PDF resumes
│   ├── app/
│   │   ├── main.py                        # FastAPI gateway with 9 mounted routers
│   │   ├── models/                        # 11 Normalized SQLAlchemy ORM models
│   │   ├── schemas/                       # Pydantic v2 validation DTOs
│   │   ├── services/                      # AI Matching, Gale-Shapley, Allocations, Resume NLP
│   │   └── routers/                       # 9 REST API endpoint modules
│   ├── migrations/                        # Alembic schema versioning
│   └── tests/                             # 31 automated pytest cases (100% green)
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── App.tsx                        # 20 Client routes with RBAC guards
        ├── services/api.ts                # Typed Axios API client
        ├── context/                       # AuthContext & ToastContext
        ├── components/                    # AppLayout, Navbar, Sidebar, StatusBadge
        └── pages/                         # 20 complete views (Student, Admin, Catalog, Analytics)
```
