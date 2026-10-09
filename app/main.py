from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from . import models, schemas, database, services, utils
import os

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Bulk Certificate Generator API",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "tryItOutEnabled": True
    }
)

HTML_UI = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Certificate API Tester</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f8fafc;
      color: #0f172a;
      padding: 32px 16px;
      display: flex;
      justify-content: center;
    }
    .wrapper {
      width: 100%;
      max-width: 760px;
    }
    header {
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    h1 {
      font-size: 20px;
      font-weight: 600;
      color: #0f172a;
    }
    .tag {
      font-size: 12px;
      background: #e2e8f0;
      color: #475569;
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 500;
    }
    .accordion {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .card-header {
      padding: 12px 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      user-select: none;
      background: #ffffff;
      transition: background 0.15s;
    }
    .card-header:hover { background: #f8fafc; }
    .badge {
      font-size: 11px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 4px;
      letter-spacing: 0.5px;
    }
    .badge-post { background: #dcfce7; color: #15803d; }
    .badge-get { background: #e0f2fe; color: #0369a1; }
    .endpoint-path {
      font-family: monospace;
      font-size: 14px;
      font-weight: 600;
      color: #1e293b;
    }
    .endpoint-desc {
      font-size: 13px;
      color: #64748b;
      margin-left: auto;
    }
    .chevron {
      font-size: 12px;
      color: #94a3b8;
      transition: transform 0.2s;
    }
    .card.open .chevron { transform: rotate(180deg); }
    .card-body {
      display: none;
      padding: 16px;
      border-top: 1px solid #e2e8f0;
      background: #fcfcfd;
    }
    .card.open .card-body { display: block; }
    .tabs {
      display: flex;
      gap: 8px;
      margin-bottom: 14px;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 8px;
    }
    .tab-btn {
      background: none;
      border: 1px solid transparent;
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 600;
      color: #64748b;
      border-radius: 4px;
      cursor: pointer;
    }
    .tab-btn.active {
      background: #e2e8f0;
      color: #0f172a;
    }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    label {
      display: block;
      font-size: 11px;
      font-weight: 600;
      color: #475569;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    textarea, input[type="number"], input[type="text"], input[type="file"] {
      width: 100%;
      padding: 8px 12px;
      font-family: monospace;
      font-size: 13px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      background: #ffffff;
      color: #0f172a;
      margin-bottom: 12px;
    }
    input[type="file"] {
      font-family: inherit;
      padding: 6px;
    }
    textarea:focus, input:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 2px rgba(59,130,246,0.15);
    }
    textarea { height: 110px; resize: vertical; }
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 8px 16px;
      font-size: 13px;
      font-weight: 600;
      border-radius: 6px;
      border: none;
      cursor: pointer;
      transition: background 0.15s;
    }
    .btn-primary { background: #2563eb; color: #fff; }
    .btn-primary:hover { background: #1d4ed8; }
    .btn-secondary { background: #0284c7; color: #fff; }
    .btn-secondary:hover { background: #0369a1; }
    .result-box {
      margin-top: 14px;
      background: #0f172a;
      color: #f8fafc;
      border-radius: 6px;
      padding: 12px;
      font-family: monospace;
      font-size: 12px;
      overflow-x: auto;
      max-height: 240px;
      white-space: pre-wrap;
      word-break: break-all;
    }
    .status-line {
      font-size: 12px;
      font-weight: 600;
      margin-top: 10px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .cert-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      margin-top: 8px;
      font-size: 13px;
    }
    .download-link {
      font-size: 12px;
      font-weight: 600;
      color: #2563eb;
      text-decoration: none;
    }
    .download-link:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="wrapper">
    <header>
      <h1>Bulk Certificate Generator API</h1>
    </header>

    <div class="accordion">
      <!-- 1. POST Job Creation Card (Supports JSON, CSV File, Raw Text) -->
      <div class="card open" id="card-post">
        <div class="card-header" onclick="toggleCard('card-post')">
          <span class="badge badge-post">POST</span>
          <span class="endpoint-path">/jobs/</span>
          <span class="endpoint-desc">Create Job (JSON / CSV / Raw Text)</span>
          <span class="chevron">&#9660;</span>
        </div>
        <div class="card-body">
          <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('tab-json')">1. JSON Payload</button>
            <button class="tab-btn" onclick="switchTab('tab-csv-file')">2. Upload CSV File</button>
            <button class="tab-btn" onclick="switchTab('tab-raw-text')">3. Paste CSV / Text</button>
          </div>

          <!-- Tab 1: JSON -->
          <div class="tab-content active" id="tab-json">
            <label>Recipients JSON</label>
            <textarea id="jsonPayload">{
  "recipients": [
    {
      "name": "Bruce Wayne",
      "course": "Advanced Stealth"
    },
    {
      "name": "Clark Kent",
      "course": "Flight Mechanics"
    }
  ]
}</textarea>
            <button class="btn btn-primary" onclick="submitJsonJob()">Execute (JSON)</button>
          </div>

          <!-- Tab 2: Upload CSV File -->
          <div class="tab-content" id="tab-csv-file">
            <label>Select CSV File (.csv)</label>
            <input type="file" id="csvFileInput" accept=".csv,.txt">
            <button class="btn btn-primary" onclick="submitCsvFileJob()">Upload & Execute (CSV)</button>
          </div>

          <!-- Tab 3: Paste CSV/Text -->
          <div class="tab-content" id="tab-raw-text">
            <label>Paste CSV Lines (Name, Course)</label>
            <textarea id="rawTextPayload">Diana Prince, Ancient Warfare
Barry Allen, Quantum Speed
Arthur Curry, Marine Biology</textarea>
            <button class="btn btn-primary" onclick="submitRawTextJob()">Execute (Text)</button>
          </div>

          <div id="postResult"></div>
        </div>
      </div>

      <!-- 2. GET /jobs/{job_id} -->
      <div class="card open" id="card-get-job">
        <div class="card-header" onclick="toggleCard('card-get-job')">
          <span class="badge badge-get">GET</span>
          <span class="endpoint-path">/jobs/{job_id}</span>
          <span class="endpoint-desc">Check Job Status</span>
          <span class="chevron">&#9660;</span>
        </div>
        <div class="card-body">
          <label>Job ID</label>
          <input type="number" id="jobIdInput" placeholder="Enter Job ID (e.g. 1)" value="1">
          <button class="btn btn-secondary" onclick="checkJob()">Execute</button>
          <div id="jobResult"></div>
        </div>
      </div>

      <!-- 3. GET /certificates/{cert_id}/download -->
      <div class="card open" id="card-download">
        <div class="card-header" onclick="toggleCard('card-download')">
          <span class="badge badge-get">GET</span>
          <span class="endpoint-path">/certificates/{cert_id}/download</span>
          <span class="endpoint-desc">Download Certificate</span>
          <span class="chevron">&#9660;</span>
        </div>
        <div class="card-body">
          <label>Certificate ID</label>
          <input type="number" id="certIdInput" placeholder="Enter Certificate ID (e.g. 1)" value="1">
          <button class="btn btn-secondary" onclick="downloadCert()">Download</button>
          <div id="downloadResult"></div>
        </div>
      </div>
    </div>
  </div>

  <script>
    function toggleCard(id) {
      document.getElementById(id).classList.toggle('open');
    }

    function switchTab(tabId) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById(tabId).classList.add('active');
    }

    function handleJobResponse(res, data) {
      const resContainer = document.getElementById('postResult');
      resContainer.innerHTML = `
        <div class="status-line">Status: ${res.status} ${res.statusText}</div>
        <div class="result-box">${JSON.stringify(data, null, 2)}</div>
      `;
      if (data.id) {
        document.getElementById('jobIdInput').value = data.id;
      }
    }

    async function submitJsonJob() {
      const resContainer = document.getElementById('postResult');
      resContainer.innerHTML = '<div class="status-line">Submitting JSON job...</div>';
      try {
        const payload = JSON.parse(document.getElementById('jsonPayload').value);
        const res = await fetch('/jobs/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        handleJobResponse(res, data);
      } catch (err) {
        resContainer.innerHTML = `<div class="status-line" style="color: #ef4444;">Error: ${err.message}</div>`;
      }
    }

    async function submitCsvFileJob() {
      const fileInput = document.getElementById('csvFileInput');
      const resContainer = document.getElementById('postResult');
      if (!fileInput.files.length) return alert("Please select a .csv file.");
      
      resContainer.innerHTML = '<div class="status-line">Uploading CSV file...</div>';
      const formData = new FormData();
      formData.append('file', fileInput.files[0]);

      try {
        const res = await fetch('/jobs/upload-csv', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        handleJobResponse(res, data);
      } catch (err) {
        resContainer.innerHTML = `<div class="status-line" style="color: #ef4444;">Error: ${err.message}</div>`;
      }
    }

    async function submitRawTextJob() {
      const text = document.getElementById('rawTextPayload').value.trim();
      const resContainer = document.getElementById('postResult');
      if (!text) return alert("Please enter recipient lines.");
      resContainer.innerHTML = '<div class="status-line">Submitting raw text...</div>';
      try {
        const res = await fetch('/jobs/raw-text', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        });
        const data = await res.json();
        handleJobResponse(res, data);
      } catch (err) {
        resContainer.innerHTML = `<div class="status-line" style="color: #ef4444;">Error: ${err.message}</div>`;
      }
    }

    async function checkJob() {
      const id = document.getElementById('jobIdInput').value.trim();
      const resContainer = document.getElementById('jobResult');
      if (!id) return alert("Please enter a Job ID");
      resContainer.innerHTML = '<div class="status-line">Fetching status...</div>';
      try {
        const res = await fetch(`/jobs/${id}`);
        const data = await res.json();
        let certsHtml = '';
        if (data.certificates && data.certificates.length) {
          certsHtml = data.certificates.map(c => `
            <div class="cert-item">
              <div>
                <strong>${c.recipient_name || 'N/A'}</strong> - <span>${c.course_name || 'N/A'}</span> 
                <small style="color: ${c.status === 'SUCCESS' ? '#16a34a' : '#dc2626'}; font-weight:600;">[${c.status}]</small>
                ${c.error_message ? `<div style="color:#ef4444; font-size:11px;">${c.error_message}</div>` : ''}
              </div>
              ${c.status === 'SUCCESS' ? `<a class="download-link" href="/certificates/${c.id}/download" target="_blank">Download</a>` : ''}
            </div>
          `).join('');
        }
        resContainer.innerHTML = `
          <div class="status-line">Status: ${res.status} ${res.statusText} (${data.status})</div>
          <div class="result-box">${JSON.stringify(data, null, 2)}</div>
          ${certsHtml ? '<div style="margin-top:10px;">' + certsHtml + '</div>' : ''}
        `;
      } catch (err) {
        resContainer.innerHTML = `<div class="status-line" style="color: #ef4444;">Error: ${err.message}</div>`;
      }
    }

    function downloadCert() {
      const id = document.getElementById('certIdInput').value.trim();
      if (!id) return alert("Please enter a Certificate ID");
      window.open(`/certificates/${id}/download`, '_blank');
    }
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_compact_ui():
    """Serves clean, simple, compact interactive API tester with multiple input modes."""
    return HTML_UI

# 1. JSON Endpoint
@app.post("/jobs/", response_model=schemas.JobResponse, status_code=202, summary="Create Job via JSON")
def create_generation_job(job_req: schemas.JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    if not job_req.recipients:
        raise HTTPException(status_code=400, detail="Recipients list cannot be empty.")
    return services.create_and_dispatch_job(job_req.recipients, background_tasks, db)

# 2. CSV File Upload Endpoint
@app.post("/jobs/upload-csv", response_model=schemas.JobResponse, status_code=202, summary="Create Job via CSV File Upload")
async def create_job_from_csv(
    file: UploadFile = File(..., description="CSV file with name and course columns"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(database.get_db)
):
    if not file.filename.lower().endswith((".csv", ".txt")):
        raise HTTPException(status_code=400, detail="Only .csv and .txt files are supported.")

    content = await file.read()
    try:
        csv_text = content.decode("utf-8")
    except UnicodeDecodeError:
        csv_text = content.decode("latin-1")

    recipients = utils.parse_csv_content(csv_text)
    if not recipients:
        raise HTTPException(status_code=400, detail="No valid recipient rows found in the CSV file.")

    return services.create_and_dispatch_job(recipients, background_tasks, db)

# 3. Raw CSV / Plain Text Endpoint
@app.post("/jobs/raw-text", response_model=schemas.JobResponse, status_code=202, summary="Create Job via Raw CSV Text")
def create_job_from_raw_text(
    payload: schemas.RawTextJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db)
):
    recipients = utils.parse_csv_content(payload.text)
    if not recipients:
        raise HTTPException(status_code=400, detail="No valid recipient rows found in provided text.")

    return services.create_and_dispatch_job(recipients, background_tasks, db)

# Status Check
@app.get("/jobs/{job_id}", response_model=schemas.JobResponse, summary="Get Job Status and Certificates")
def get_job_status(job_id: int, db: Session = Depends(database.get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# Certificate Download
@app.get("/certificates/{cert_id}/download", summary="Download Single Certificate File")
def download_certificate(cert_id: int, db: Session = Depends(database.get_db)):
    cert = db.query(models.Certificate).filter(models.Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if cert.status != models.CertificateStatus.SUCCESS or not cert.file_path:
        raise HTTPException(status_code=400, detail="Certificate is not ready or failed to generate")

    if not os.path.exists(cert.file_path):
        raise HTTPException(status_code=404, detail="File on disk not found")

    return FileResponse(cert.file_path, media_type="image/jpeg", filename=f"{cert.recipient_name.replace(' ', '_')}_Certificate.jpg")
