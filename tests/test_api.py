import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_input_validation_empty_recipients():
    response = client.post("/jobs/", json={"recipients": []})
    assert response.status_code == 400
    assert response.json()["detail"] == "Recipients list cannot be empty."

def test_input_validation_invalid_schema():
    response = client.post("/jobs/", json={"recipients": [{"name": "Only Name"}]})
    assert response.status_code == 422

def test_create_job_via_json_and_retrieve_certificate():
    response = client.post("/jobs/", json={
        "recipients": [
            {"name": "Valid User", "course": "Valid Course"}
        ]
    })
    assert response.status_code == 202
    job_id = response.json()["id"]

    status_response = client.get(f"/jobs/{job_id}")
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["status"] == "COMPLETED"
    assert len(data["certificates"]) == 1

    cert = data["certificates"][0]
    assert cert["status"] == "SUCCESS"
    assert cert["recipient_name"] == "Valid User"

    cert_id = cert["id"]
    download_response = client.get(f"/certificates/{cert_id}/download")
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "image/jpeg"

def test_create_job_via_csv_upload():
    csv_content = "name,course\nAlice Cooper,Rock History\nBob Dylan,Folk Music"
    file_tuple = ("recipients.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")

    response = client.post("/jobs/upload-csv", files={"file": file_tuple})
    assert response.status_code == 202
    job_id = response.json()["id"]

    status_response = client.get(f"/jobs/{job_id}")
    assert status_response.status_code == 200
    data = status_response.json()
    assert len(data["certificates"]) == 2
    assert data["status"] == "COMPLETED"

def test_create_job_via_raw_text():
    text_data = "Diana Prince, Ancient Warfare\nBarry Allen, Quantum Speed"
    response = client.post("/jobs/raw-text", json={"text": text_data})
    assert response.status_code == 202
    job_id = response.json()["id"]

    status_response = client.get(f"/jobs/{job_id}")
    assert status_response.status_code == 200
    data = status_response.json()
    assert len(data["certificates"]) == 2
    assert data["status"] == "COMPLETED"

def test_individual_certificate_failure():
    with patch("app.utils.generate_certificate_image") as mock_generate:
        def side_effect(name, course):
            if name == "Fail User":
                raise Exception("Forced failure")
            return "dummy_path.jpg"

        mock_generate.side_effect = side_effect

        response = client.post("/jobs/", json={
            "recipients": [
                {"name": "Success User", "course": "Test"},
                {"name": "Fail User", "course": "Test"}
            ]
        })
        assert response.status_code == 202
        job_id = response.json()["id"]

        status_response = client.get(f"/jobs/{job_id}")
        data = status_response.json()

        assert data["status"] == "PARTIAL_SUCCESS"
        certs = {c["recipient_name"]: c for c in data["certificates"]}
        assert certs["Success User"]["status"] == "SUCCESS"
        assert certs["Fail User"]["status"] == "FAILED"
        assert certs["Fail User"]["error_message"] == "Forced failure"
