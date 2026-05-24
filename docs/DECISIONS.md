# Architectural Decisions & Assumptions

This document lists the major technical decisions, assumptions, and resolutions during development of the Breathe ESG platform prototype.

## Ingestion Architecture

### 1. CSV Parsers over heavy data frameworks
- **Decision**: Used Python's built-in `csv` module with robust character detection and separator sniffing rather than pulling in massive frameworks like `pandas`.
- **Rationale**: For a prototype, native libraries start immediately and avoid memory bloat. Standard file uploads are parsed row-by-row inside database transactions. In a larger production environment, this is easily transitioned to a queue-based ingestion worker (e.g. Celery).

### 2. Mocking Corporate Travel API
- **Decision**: Built a sync endpoint `/api/uploads/travel/sync` that processes travel bookings stored in a structured JSON file inside the platform.
- **Rationale**: Simulates navan/concur feed ingestion by loading realistic JSON records (including flights, hotel nights, taxis, and trains), performing the exact same validation and database logging as the CSV channels.

---

## Ambiguities Resolved

### 1. Handling Inconsistent Date Formats
- **Ambiguity**: SAP exports can have mixed formats (e.g., German dot notation `15.05.2026`, slash notation `12/05/2026`, or standard ISO `2026-05-01`).
- **Resolution**: Implemented a multi-format date parser checking common formats sequentially. If parsing fails, the transaction date defaults to the current day, and the record's confidence score is penalized by 20%.

### 2. Overlapping Billing Periods for Utility Meters
- **Ambiguity**: If multiple utility bills overlap on dates for the same meter, should the row fail to load?
- **Resolution**: The row is successfully ingested and normalized, but a `validation_issue` with type `overlapping_cycle` is logged as a warning. This highlights the issue to the analyst while ensuring the data isn't dropped.

### 3. Missing Flight Distance Calculations
- **Ambiguity**: Corporate travel payloads often contain airport travel codes (e.g. "LHR" to "JFK") but no distance value.
- **Resolution**: Integrated an in-memory database of major airport latitude and longitude coordinates. If a flight distance is missing, the system automatically computes the geodesic distance (Haversine formula). If an airport code is invalid (e.g. "XYZ"), it logs an error flag.

---

## Key Assumptions

1. **All Demo Users are Analysts**: For testing simplicity, any user registration defaults to an "analyst" role, granting immediate access to upload and approve tools.
2. **PostgreSQL as Primary Database**: Models are written to align with SQL standards, using SQLite for local development and test runs while ensuring seamless migrations when pushing to a cloud-managed PostgreSQL instance.
3. **No Retroactive Factor Updates**: Emission factors are maintained in application memory (`app/core/constants.py`). In a production setting, these factors would be stored in a dedicated database table with version tracking to support retroactive computations.
