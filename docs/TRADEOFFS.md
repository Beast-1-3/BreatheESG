# Technical Tradeoffs & Exclusions

This document outlines intentional design compromises made for this prototype and outlines future production scaling.

## Excluded Features & Rationale

### 1. Asynchronous Queue Workers (Celery & Redis)
- **Tradeoff**: Ingestion runs are processed synchronously in the request-response cycle of the upload endpoints.
- **Why**: The sample datasets are small (under 100 rows). Setting up Celery and Redis containers adds setup overhead for local evaluation. 
- **Production Path**: Large files (e.g. 100k+ rows of SAP journals) should write file metadata, save the file to object storage (S3), and queue a Celery task. The backend would poll or use WebSockets to update the UI once parsing completes.

### 2. Physical File Storage
- **Tradeoff**: Raw CSV file binaries are parsed in-memory from bytes and not written to a permanent disk or storage bucket.
- **Why**: Avoids filesystem permissions issues or AWS credential dependencies during evaluation. 
- **Production Path**: Store incoming uploads in secure cloud storage buckets (e.g. AWS S3 with KMS encryption) prior to execution, linking file paths to `raw_uploads` metadata.

### 3. Cryptographic Ledger for Audit Logs
- **Tradeoff**: Audit logs and lock mechanisms rely on standard relational constraints (`locked_for_audit` boolean, review tables) instead of a blockchain or ledger database (like AWS QLDB).
- **Why**: Keeps database migrations simple and standardizes queries on PostgreSQL.
- **Production Path**: Calculate cryptographic SHA-256 hashes of record contents when approved, chaining hashes together in the audit table (like a Merkle Tree) to mathematically prove the database state has not been modified.

---

## Future Scaling Improvements

1. **Database Partitioning**: Partition `emission_records` by `organization_id` or fiscal year to preserve performance when rows scale into millions.
2. **Dynamic Emission Factors Table**: Build a master table for emission factors with start/end validity dates, enabling auditors to track and audit the exact factors active at the transaction timestamp.
3. **Advanced Anomaly Models**: Replace static 5x averages with statistical calculations (z-score, isolation forests) using background worker pipelines.
