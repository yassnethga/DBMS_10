from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150))
    phone = Column(String(50))

    jobs = relationship("Job", back_populates="customer")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False, default="open")
    job_date = Column(Date, nullable=False)

    customer = relationship("Customer", back_populates="jobs")
    materials = relationship("JobMaterial", back_populates="job")
    invoice = relationship("Invoice", back_populates="job", uselist=False)


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    purchase_price = Column(Numeric(10, 2), nullable=False)

    job_links = relationship("JobMaterial", back_populates="material")


class JobMaterial(Base):
    __tablename__ = "job_materials"
    __table_args__ = (UniqueConstraint("job_id", "material_id"),)

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)

    job = relationship("Job", back_populates="materials")
    material = relationship("Material", back_populates="job_links")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), unique=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(String(50), nullable=False, default="unpaid")

    job = relationship("Job", back_populates="invoice")