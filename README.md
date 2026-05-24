# Breathe ESG Ingestion & Audit Platform Prototype

A production-quality ESG data ingestion and analyst auditing dashboard built with **FastAPI**, **React (Vite)**, and **PostgreSQL/SQLite**.

---

## Key Features

1. **Multi-Source Ingestion**:
   - **SAP Fuel Export**: CSV upload with German/English columns, unit normalization, and value parsing.
   - **Utility Electricity Logs**: CSV upload featuring meter lookup and overlap warnings.
   - **Corporate Travel REST API**: Mocked sync parser checking flights, hotel nights, land travel, and computing flight distances using geodesic Haversine algorithms.
2. **GHG Scope Normalization**: Maps inputs into Scope 1, 2, and 3 classifications using standard emission factors.
3. **Analyst Review Console**: Features comments, approvals, rejections, and audit locks. Approved records become immutable.
4. **Validation Engine**: Automated warnings for negative values, duplicates, overlapping billing cycles, and anomalies.
5. **System Audit Logs**: Records all user actions and database state changes.
6. **Premium Dark UI**: Built with React, Tailwind CSS, and Recharts.

---

## File Structure

```text
breathe-esg-platform/
├── backend/
│   ├── app/
│   │   ├── api/          # Routers and endpoints (auth, uploads, records, reviews, audits, dashboard)
│   │   ├── core/         # DB config, dependencies, JWT security, ESG constants
│   │   ├── models/       # SQLAlchemy models (Organization, User, EmissionRecord, AuditLog, etc.)
│   │   ├── schemas/      # Pydantic validation schemas
│   │   ├── services/     # Ingestion parsers, normalization rules, validation engine
│   │   ├── utils/        # CSV parser, Haversine, unit conversion utilities
│   │   └── tests/        # Automated test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/          # Axios configurations and endpoints mapping
│   │   ├── components/   # Common layout shell, header, sidebar
│   │   ├── pages/        # Dashboard, Upload center, Review page, Detail comparison, Audit logs
│   │   └── App.jsx       # Routing configurations
│   ├── index.html
│   ├── tailwind.config.js
│   └── package.json
├── sample-data/          # Mock SAP, Utility, and Travel data
└── docs/                 # MODEL.md, DECISIONS.md, TRADEOFFS.md, SOURCES.md
```

---

## Running the Application

### 1. Pre-requisites
- **Python**: 3.9+
- **Node.js**: 16+

### 2. Backend Setup
```bash
cd backend

# Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server (default: starts on http://localhost:8000 and auto-migrates SQLite database)
uvicorn app.main:app --reload
```

### 3. Running Automated Tests
```bash
cd backend
source venv/bin/activate
python3 -m pytest app/tests/test_flow.py
```

### 4. Frontend Setup
```bash
cd frontend

# Install Node modules
npm install

# Run Vite dev server (starts on http://localhost:5173 with API proxying to backend)
npm run dev
```

---

## Credentials for Testing
You can register a new organization directly on the Login screen, or use the form to sign in. The registration automatically generates default active DataSources for your tenant.
- **Demo Server Address**: `http://localhost:5173`
- **Default Database**: Local file `esg_platform.db` (SQLite) or external via `DATABASE_URL`.
