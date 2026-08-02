# HandwerkerKasse -- Material and Invoice Tracker with Profit Analysis per Job

**Module:** Introduction to Database Management Systems - THGA Bochum
**Author:** Mohamed Yassine Hachimi
**Lecturer:** Stephan Boekelmann - sboekelmann@ep1.rub.de

HandwerkerKasse is a database-driven application for small craft businesses.
It lets users manage customers, jobs, materials and invoices, and automatically
calculates the profit of each job by comparing the invoice amount against the
material costs used.

## Documentation

- Project Proposal: proposal-template/proposal.tex
- User Guide: user-documentation/documentation.pdf
- Developer Documentation: developer-documentation/documentation.pdf

## Architecture

Frontend (Tkinter, installed as .deb) -- HTTP + X-API-Key --> FastAPI --> PostgreSQL

Backend and database run via Docker Compose.

- Database: PostgreSQL, 5 tables (customers, jobs, materials, job_materials, invoices), normalized to 3NF.
- Backend: FastAPI with SQLAlchemy, 12 REST endpoints, write operations protected with an X-API-Key header.
- Frontend: Tkinter desktop application, packaged as a Debian (.deb) installer.
- Deployment: Backend and database run as containers via Docker Compose.

## Repository layout