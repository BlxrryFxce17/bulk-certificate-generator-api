from sqlalchemy.orm import Session
from . import models, utils, database

def create_and_dispatch_job(recipients: list, background_tasks, db: Session) -> models.Job:
    """
    Creates a new Job, sets up initial Certificate records,
    and enqueues the background processing task.
    """
    db_job = models.Job(status=models.JobStatus.PENDING)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    for rec in recipients:
        name = rec.name if hasattr(rec, "name") else rec.get("name", "")
        course = rec.course if hasattr(rec, "course") else rec.get("course", "")

        db_cert = models.Certificate(
            job_id=db_job.id,
            recipient_name=name.strip() if name else "",
            course_name=course.strip() if course else ""
        )
        db.add(db_cert)

    db.commit()
    db.refresh(db_job)

    background_tasks.add_task(process_job_background, db_job.id, database.SessionLocal())
    return db_job

def process_job_background(job_id: int, db: Session):
    try:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            return

        job.status = models.JobStatus.PROCESSING
        db.commit()

        success_count = 0
        fail_count = 0

        for cert in job.certificates:
            # Validate input data for individual certificate
            if not cert.recipient_name or not cert.course_name:
                cert.status = models.CertificateStatus.FAILED
                cert.error_message = "Recipient name or course name cannot be blank."
                fail_count += 1
                db.commit()
                continue

            try:
                file_path = utils.generate_certificate_image(cert.recipient_name, cert.course_name)
                cert.file_path = file_path
                cert.status = models.CertificateStatus.SUCCESS
                success_count += 1
            except Exception as e:
                cert.status = models.CertificateStatus.FAILED
                cert.error_message = str(e)
                fail_count += 1

            # Commit individually so progress is saved incrementally
            db.commit()

        if fail_count == 0 and success_count > 0:
            job.status = models.JobStatus.COMPLETED
        elif success_count == 0:
            job.status = models.JobStatus.FAILED
        else:
            job.status = models.JobStatus.PARTIAL_SUCCESS

        db.commit()
    finally:
        db.close()
