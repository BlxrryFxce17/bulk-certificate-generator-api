# Bulk Certificate Generator API

High-performance backend service built with **FastAPI** and **SQLite** to generate recipient certificates in bulk using asynchronous background processing.

---

## Features & Highlights

- **Multiple Input Formats**: Submit jobs via:
  1. **JSON Payload** (`POST /jobs/`)
  2. **CSV File Upload** (`POST /jobs/upload-csv`)
  3. **Pasted CSV / Plain Text** (`POST /jobs/raw-text`)
- **Asynchronous Execution**: Uses FastAPI `BackgroundTasks` to offload image generation so API requests return immediately with HTTP 202 Accepted.
- **Fault-Tolerant & Isolated Failures**: If one recipient has invalid data or fails generation, it does not stop the other certificates in the batch. The job gracefully reports `PARTIAL_SUCCESS`.
- **Status Tracking & Asset Retrieval**: Check job progress via `GET /jobs/{id}` and download finalized JPGs via `GET /certificates/{id}/download`.
- **Interactive UI**: Includes a clean tester at `http://127.0.0.1:8000/` and standard Swagger documentation at `/docs`.

---

## Setup Instructions

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up assets (generates template image & font):**
   ```bash
   python setup_assets.py
   ```

---

## Running the Application

```bash
uvicorn app.main:app --reload
```
- **Interactive Tester:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Running Automated Tests

Run the test suite verifying input validation, bulk generation, CSV uploads, error isolation, and downloads:
```bash
python -m pytest tests/test_api.py
```

---

## API Endpoints

### 1. Create a Generation Job

#### Option A: JSON Payload
`POST /jobs/`
```json
{
  "recipients": [
    { "name": "Bruce Wayne", "course": "Advanced Stealth" },
    { "name": "Clark Kent", "course": "Flight Mechanics" }
  ]
}
```

#### Option B: Upload CSV File
`POST /jobs/upload-csv`
Upload any `.csv` file containing `name` and `course` headers or comma-separated rows.

#### Option C: Paste Raw CSV Text
`POST /jobs/raw-text`
```json
{
  "text": "Diana Prince, Ancient Warfare\nBarry Allen, Quantum Speed"
}
```

### 2. Check Job Status & Progress
`GET /jobs/{job_id}`

**Response:**
```json
{
  "id": 1,
  "status": "COMPLETED",
  "certificates": [
    {
      "id": 1,
      "recipient_name": "Bruce Wayne",
      "course_name": "Advanced Stealth",
      "status": "SUCCESS",
      "file_path": "output/....jpg",
      "error_message": null
    }
  ]
}
```

### 3. Download Certificate
`GET /certificates/{cert_id}/download`  
Returns the generated certificate image (`image/jpeg`).

---

## Design Decisions

- **FastAPI + BackgroundTasks**: Offers high concurrency for I/O operations without the overhead of external message brokers (like Celery/RabbitMQ) for single-node deployments.
- **SQLite (SQLAlchemy ORM)**: Provides reliable relational data persistence with zero setup friction for evaluators.
- **Pillow (PIL)**: Lightweight, high-speed image processing for dynamic text placement and typography.
