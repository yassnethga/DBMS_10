import tkinter as tk
from tkinter import ttk, messagebox
import api


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HandwerkerKasse")
        self.geometry("650x500")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainScreen, JobFormScreen, InvoiceScreen):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainScreen)

    def show_frame(self, screen_class):
        frame = self.frames[screen_class]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()


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
            for job in api.get_jobs_profit():
                tag = "loss" if job["profit"] < 0 else "profit"
                self.tree.insert("", "end", values=(
                    job["title"],
                    f"{job['invoice_amount']:.2f} EUR",
                    f"{job['material_cost']:.2f} EUR",
                    f"{job['profit']:.2f} EUR",
                ), tags=(tag,))
            self.tree.tag_configure("loss", foreground="red")
            self.tree.tag_configure("profit", foreground="green")
        except Exception as e:
            messagebox.showerror("Error", str(e))


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
        try:
            result = api.create_job(
                int(self.customer_id.get()),
                self.title_entry.get(),
                "open",
                self.date_entry.get(),
            )
            messagebox.showinfo("Success", f"Job created with ID {result['id']}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_material(self):
        try:
            api.add_job_material(
                int(self.mat_job_id.get()),
                int(self.material_id.get()),
                float(self.quantity.get()),
            )
            messagebox.showinfo("Success", "Material added to job")
        except Exception as e:
            messagebox.showerror("Error", str(e))


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
        try:
            api.create_invoice(
                int(self.job_id.get()),
                float(self.amount.get()),
                self.status_var.get(),
            )
            messagebox.showinfo("Success", "Invoice created")
            self.controller.show_frame(MainScreen)
        except Exception as e:
            messagebox.showerror("Error", str(e))
