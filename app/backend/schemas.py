from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


# ---------- Customer ----------
class CustomerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None


class CustomerOut(CustomerCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Job ----------
class JobCreate(BaseModel):
    customer_id: int
    title: str
    status: str = "open"
    job_date: date


class JobOut(JobCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Material ----------
class MaterialCreate(BaseModel):
    name: str
    purchase_price: float


class MaterialOut(MaterialCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- JobMaterial ----------
class JobMaterialCreate(BaseModel):
    job_id: int
    material_id: int
    quantity: float


class JobMaterialOut(JobMaterialCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Invoice ----------
class InvoiceCreate(BaseModel):
    job_id: int
    amount: float
    payment_status: str = "unpaid"


class InvoiceOut(InvoiceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Profit report ----------
class JobProfitOut(BaseModel):
    job_id: int
    title: str
    invoice_amount: float
    material_cost: float
    profit: float