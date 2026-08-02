-- ============================================================
-- HandwerkerKasse – Database Schema
-- ============================================================

DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS job_materials CASCADE;
DROP TABLE IF EXISTS materials CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

CREATE TABLE customers (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(150) NOT NULL,
    email      VARCHAR(150),
    phone      VARCHAR(50)
);

CREATE TABLE jobs (
    id          SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    title       VARCHAR(200) NOT NULL,
    status      VARCHAR(50) NOT NULL DEFAULT 'open'
                CHECK (status IN ('open', 'in_progress', 'completed', 'cancelled')),
    job_date    DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE materials (
    id             SERIAL PRIMARY KEY,
    name           VARCHAR(150) NOT NULL,
    purchase_price NUMERIC(10,2) NOT NULL CHECK (purchase_price >= 0)
);

CREATE TABLE job_materials (
    id          SERIAL PRIMARY KEY,
    job_id      INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    material_id INTEGER NOT NULL REFERENCES materials(id) ON DELETE RESTRICT,
    quantity    NUMERIC(10,2) NOT NULL CHECK (quantity > 0),
    UNIQUE (job_id, material_id)
);

CREATE TABLE invoices (
    id             SERIAL PRIMARY KEY,
    job_id         INTEGER NOT NULL UNIQUE REFERENCES jobs(id) ON DELETE CASCADE,
    amount         NUMERIC(10,2) NOT NULL CHECK (amount >= 0),
    payment_status VARCHAR(50) NOT NULL DEFAULT 'unpaid'
                   CHECK (payment_status IN ('unpaid', 'paid', 'overdue'))
);

-- Index for the profit-report JOIN
CREATE INDEX idx_job_materials_job_id ON job_materials(job_id);
CREATE INDEX idx_jobs_customer_id ON jobs(customer_id);