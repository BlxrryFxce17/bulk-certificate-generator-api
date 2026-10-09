# Bulk Certificate Generator API

High-performance backend service built with **FastAPI** and **SQLite** to generate recipient certificates in bulk using asynchronous background processing.

---

## 🚀 Live Demo & Deployment

The application is deployed live and fully interactive:

* **Live Interactive Tester:** [https://bulk-certificate-generator-api-q2u0.onrender.com/](https://bulk-certificate-generator-api-q2u0.onrender.com/)
* **Live Swagger API Documentation:** [https://bulk-certificate-generator-api-q2u0.onrender.com/docs](https://bulk-certificate-generator-api-q2u0.onrender.com/docs)

*(Note: Free-tier instances may take a few seconds to spin up on initial cold start.)*

---

## Features & Highlights

- **Multiple Input Formats**: Submit jobs via:
  1. **JSON Payload** (`POST /jobs/`)
  2. **CSV File Upload** (`POST /jobs/upload-csv`)
  3. **Pasted CSV / Plain Text** (`POST /jobs/raw-text`)
- **Asynchronous Execution**: Uses FastAPI `BackgroundTasks` to offload image generation so API requests return immediately with HTTP 202 Accepted.
- **Fault-Tolerant & Isolated Failures**: If one recipient has invalid data or fails generation, it does not stop the other certificates in the batch. The job gracefully reports `PARTIAL_SUCCESS`.
- **Status Tracking & Asset Retrieval**: Check job progress via `GET /jobs/{id}` and download finalized JPGs via `GET /certificates/{id}/download`.
- **Interactive UI**: Includes a clean tester at root `/` and standard Swagger documentation at `/docs`.
- **Docker & Cloud Ready**: Fully containerized with a `Dockerfile` and `render.yaml` for instant deployment.

---

## Setup Instructions

### Local Environment
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

4. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Access locally at:
   - Interactive Tester: `http://127.0.0.1:8000/`
   - Swagger Docs: `http://127.0.0.1:8000/docs`

---

### Docker Deployment
Build and run the container locally:
```bash
docker build -t bulk-cert-api .
docker run -p 8000:8000 bulk-cert-api
```

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
- **Containerization**: Standardized container environment via `Dockerfile` ensures consistent execution across cloud providers.
