import os
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from dotenv import load_dotenv
from typing import List

import models
import schemas
from database import engine, get_db, Base

load_dotenv(dotenv_path="../.env")
API_KEY = os.getenv("API_KEY")

# Create tables if they don't exist yet (schema.sql already does this via Docker init,
# this is a safety net for local dev without Docker)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HandwerkerKasse API", version="1.0.0")


# ---------- X-API-Key security dependency ----------
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


# ============================================================
# Customers
# ============================================================
@app.get("/customers", response_model=List[schemas.CustomerOut])
def get_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()


@app.post("/customers", response_model=schemas.CustomerOut, dependencies=[Depends(verify_api_key)])
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = models.Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


# ============================================================
# Jobs
# ============================================================
@app.get("/jobs", response_model=List[schemas.JobOut])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(models.Job).all()


@app.post("/jobs", response_model=schemas.JobOut, dependencies=[Depends(verify_api_key)])
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == job.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="customer_id does not exist")
    db_job = models.Job(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@app.put("/jobs/{job_id}", response_model=schemas.JobOut, dependencies=[Depends(verify_api_key)])
def update_job(job_id: int, job: schemas.JobCreate, db: Session = Depends(get_db)):
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    for key, value in job.model_dump().items():
        setattr(db_job, key, value)
    db.commit()
    db.refresh(db_job)
    return db_job


@app.delete("/jobs/{job_id}", dependencies=[Depends(verify_api_key)])
def delete_job(job_id: int, db: Session = Depends(get_db)):
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(db_job)
    db.commit()
    return {"detail": f"Job {job_id} deleted"}


# ============================================================
# Materials
# ============================================================
@app.get("/materials", response_model=List[schemas.MaterialOut])
def get_materials(db: Session = Depends(get_db)):
    return db.query(models.Material).all()


@app.post("/materials", response_model=schemas.MaterialOut, dependencies=[Depends(verify_api_key)])
def create_material(material: schemas.MaterialCreate, db: Session = Depends(get_db)):
    db_material = models.Material(**material.model_dump())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material


# ============================================================
# Job-Materials
# ============================================================
@app.post("/job_materials", response_model=schemas.JobMaterialOut, dependencies=[Depends(verify_api_key)])
def add_job_material(jm: schemas.JobMaterialCreate, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == jm.job_id).first()
    material = db.query(models.Material).filter(models.Material.id == jm.material_id).first()
    if not job or not material:
        raise HTTPException(status_code=400, detail="job_id or material_id does not exist")
    db_jm = models.JobMaterial(**jm.model_dump())
    db.add(db_jm)
    db.commit()
    db.refresh(db_jm)
    return db_jm


# ============================================================
# Invoices
# ============================================================
@app.get("/invoices", response_model=List[schemas.InvoiceOut])
def get_invoices(db: Session = Depends(get_db)):
    return db.query(models.Invoice).all()


@app.post("/invoices", response_model=schemas.InvoiceOut, dependencies=[Depends(verify_api_key)])
def create_invoice(invoice: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == invoice.job_id).first()
    if not job:
        raise HTTPException(status_code=400, detail="job_id does not exist")
    db_invoice = models.Invoice(**invoice.model_dump())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


# ============================================================
# Profit report — the highlight endpoint (JOIN + aggregation)
# ============================================================
@app.get("/jobs/profit", response_model=List[schemas.JobProfitOut])
def get_jobs_profit(db: Session = Depends(get_db)):
    material_cost_subq = (
        db.query(
            models.JobMaterial.job_id.label("job_id"),
            func.sum(models.JobMaterial.quantity * models.Material.purchase_price).label("material_cost"),
        )
        .join(models.Material, models.JobMaterial.material_id == models.Material.id)
        .group_by(models.JobMaterial.job_id)
        .subquery()
    )

    results = (
        db.query(
            models.Job.id.label("job_id"),
            models.Job.title.label("title"),
            models.Invoice.amount.label("invoice_amount"),
            func.coalesce(material_cost_subq.c.material_cost, 0).label("material_cost"),
        )
        .join(models.Invoice, models.Invoice.job_id == models.Job.id)
        .outerjoin(material_cost_subq, material_cost_subq.c.job_id == models.Job.id)
        .all()
    )

    return [
        schemas.JobProfitOut(
            job_id=r.job_id,
            title=r.title,
            invoice_amount=float(r.invoice_amount),
            material_cost=float(r.material_cost),
            profit=float(r.invoice_amount) - float(r.material_cost),
        )
        for r in results
    ]