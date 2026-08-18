import requests

BASE_URL = "http://127.0.0.1:8000"
HEADERS = {}


def get_customers():
    r = requests.get(f"{BASE_URL}/customers", timeout=5)
    r.raise_for_status()
    return r.json()


def get_jobs_profit():
    r = requests.get(f"{BASE_URL}/jobs/profit", timeout=5)
    r.raise_for_status()
    return r.json()


def create_job(customer_id: int, title: str, status: str, job_date: str):
    payload = {
        "customer_id": customer_id,
        "title": title,
        "status": status,
        "job_date": job_date,
    }
    r = requests.post(f"{BASE_URL}/jobs", json=payload, headers=HEADERS, timeout=5)
    r.raise_for_status()
    return r.json()


def add_job_material(job_id: int, material_id: int, quantity: float):
    payload = {"job_id": job_id, "material_id": material_id, "quantity": quantity}
    r = requests.post(f"{BASE_URL}/job_materials", json=payload, headers=HEADERS, timeout=5)
    r.raise_for_status()
    return r.json()


def create_invoice(job_id: int, amount: float, payment_status: str):
    payload = {"job_id": job_id, "amount": amount, "payment_status": payment_status}
    r = requests.post(f"{BASE_URL}/invoices", json=payload, headers=HEADERS, timeout=5)
    r.raise_for_status()
    return r.json()
