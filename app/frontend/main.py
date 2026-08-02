import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = ""
API_KEY = ""


class HandwerkerKasseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HandwerkerKasse")
        self.geometry("650x500")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (ConnectScreen, MainScreen, JobFormScreen, InvoiceScreen):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(ConnectScreen)

    def show_frame(self, screen_class):
        frame = self.frames[screen_class]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()


# ============================================================
# Screen 1: Connect
# ============================================================
class ConnectScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Connect to Server", font=("Arial", 16, "bold")).pack(pady=30)

        tk.Label(self, text="API URL").pack()
        self.url_entry = tk.Entry(self, width=40)
        self.url_entry.insert(0, "http://127.0.0.1:8000")
        self.url_entry.pack(pady=5)

        tk.Label(self, text="X-API-Key").pack()
        self.key_entry = tk.Entry(self, width=40, show="*")
        self.key_entry.pack(pady=5)

        tk.Button(self, text="Connect", command=self.connect, bg="#2c7", fg="white").pack(pady=20)
        self.status_label = tk.Label(self, text="", fg="red")
        self.status_label.pack()

    def connect(self):
        global API_URL, API_KEY
        url = self.url_entry.get().strip()
        key = self.key_entry.get().strip()

        try:
            response = requests.get(f"{url}/customers", timeout=5)
            if response.status_code == 200:
                API_URL = url
                API_KEY = key
                self.controller.show_frame(MainScreen)
            else:
                self.status_label.config(text=f"Connection failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.status_label.config(text=f"Could not connect: {e}")


# ============================================================
# Screen 2: Main (Jobs Overview with Profit)
# ============================================================
class MainScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Jobs Overview", font=("Arial", 16, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("title", "invoice", "material", "profit"), show="headings")
        self.tree.heading("title", text="Job")
        self.tree.heading("invoice", text="Invoice")
        self.tree.heading("material", text="Material Cost")
        self.tree.heading("profit", text="Profit")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Refresh", command=self.load_profit).pack(side="left", padx=5)
        tk.Button(btn_frame, text="+ New Job", command=lambda: controller.show_frame(JobFormScreen)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="+ Invoice", command=lambda: controller.show_frame(InvoiceScreen)).pack(side="left", padx=5)

    def on_show(self):
        self.load_profit()

    def load_profit(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            response = requests.get(f"{API_URL}/jobs/profit", timeout=5)
            for job in response.json():
                tag = "loss" if job["profit"] < 0 else "profit"
                self.tree.insert("", "end", values=(
                    job["title"],
                    f"{job['invoice_amount']:.2f} EUR",
                    f"{job['material_cost']:.2f} EUR",
                    f"{job['profit']:.2f} EUR",
                ), tags=(tag,))
            self.tree.tag_configure("loss", foreground="red")
            self.tree.tag_configure("profit", foreground="green")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", str(e))


# ============================================================
# Screen 3: New Job + Material
# ============================================================
class JobFormScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="New Job", font=("Arial", 16, "bold")).pack(pady=10)

        form = tk.Frame(self)
        form.pack(pady=10)

        tk.Label(form, text="Customer ID:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.customer_id = tk.Entry(form)
        self.customer_id.grid(row=0, column=1, pady=5)

        tk.Label(form, text="Title:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.title_entry = tk.Entry(form)
        self.title_entry.grid(row=1, column=1, pady=5)

        tk.Label(form, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.date_entry = tk.Entry(form)
        self.date_entry.insert(0, "2026-08-02")
        self.date_entry.grid(row=2, column=1, pady=5)

        tk.Button(self, text="Save Job", command=self.save_job, bg="#2c7", fg="white").pack(pady=10)

        tk.Label(self, text="Add Material to Job", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        mat_form = tk.Frame(self)
        mat_form.pack()

        tk.Label(mat_form, text="Job ID:").grid(row=0, column=0, sticky="e", padx=5)
        self.mat_job_id = tk.Entry(mat_form)
        self.mat_job_id.grid(row=0, column=1)

        tk.Label(mat_form, text="Material ID:").grid(row=1, column=0, sticky="e", padx=5)
        self.material_id = tk.Entry(mat_form)
        self.material_id.grid(row=1, column=1)

        tk.Label(mat_form, text="Quantity:").grid(row=2, column=0, sticky="e", padx=5)
        self.quantity = tk.Entry(mat_form)
        self.quantity.grid(row=2, column=1)

        tk.Button(self, text="Add Material", command=self.add_material).pack(pady=10)
        tk.Button(self, text="Back to Overview", command=lambda: controller.show_frame(MainScreen)).pack(pady=10)

    def save_job(self):
        payload = {
            "customer_id": int(self.customer_id.get()),
            "title": self.title_entry.get(),
            "status": "open",
            "job_date": self.date_entry.get(),
        }
        headers = {"X-API-Key": API_KEY}
        response = requests.post(f"{API_URL}/jobs", json=payload, headers=headers)
        if response.status_code == 200:
            messagebox.showinfo("Success", f"Job created with ID {response.json()['id']}")
        else:
            messagebox.showerror("Error", response.text)

    def add_material(self):
        payload = {
            "job_id": int(self.mat_job_id.get()),
            "material_id": int(self.material_id.get()),
            "quantity": float(self.quantity.get()),
        }
        headers = {"X-API-Key": API_KEY}
        response = requests.post(f"{API_URL}/job_materials", json=payload, headers=headers)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Material added to job")
        else:
            messagebox.showerror("Error", response.text)


# ============================================================
# Screen 4: Invoice
# ============================================================
class InvoiceScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Invoice", font=("Arial", 16, "bold")).pack(pady=10)

        form = tk.Frame(self)
        form.pack(pady=10)

        tk.Label(form, text="Job ID:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.job_id = tk.Entry(form)
        self.job_id.grid(row=0, column=1, pady=5)

        tk.Label(form, text="Amount:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.amount = tk.Entry(form)
        self.amount.grid(row=1, column=1, pady=5)

        tk.Label(form, text="Payment Status:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.status_var = tk.StringVar(value="unpaid")
        ttk.Combobox(form, textvariable=self.status_var, values=["unpaid", "paid", "overdue"]).grid(row=2, column=1, pady=5)

        tk.Button(self, text="Create Invoice", command=self.create_invoice, bg="#2c7", fg="white").pack(pady=15)
        tk.Button(self, text="Back to Overview", command=lambda: controller.show_frame(MainScreen)).pack(pady=5)

    def create_invoice(self):
        payload = {
            "job_id": int(self.job_id.get()),
            "amount": float(self.amount.get()),
            "payment_status": self.status_var.get(),
        }
        headers = {"X-API-Key": API_KEY}
        response = requests.post(f"{API_URL}/invoices", json=payload, headers=headers)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Invoice created")
            self.controller.show_frame(MainScreen)
        else:
            messagebox.showerror("Error", response.text)


if __name__ == "__main__":
    app = HandwerkerKasseApp()
    app.mainloop()