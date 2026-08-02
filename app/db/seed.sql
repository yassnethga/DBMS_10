-- ============================================================
-- HandwerkerKasse – Seed data (for local testing/demo)
-- ============================================================

INSERT INTO customers (name, email, phone) VALUES
('Frau Schmidt', 'schmidt@example.com', '0221-1234567'),
('Herr Mueller', 'mueller@example.com', '0234-9876543');

INSERT INTO jobs (customer_id, title, status, job_date) VALUES
(1, 'Electrical installation', 'completed', '2026-07-15'),
(2, 'Bathroom rewiring', 'completed', '2026-07-20'),
(1, 'Outdoor lighting', 'in_progress', '2026-07-28');

INSERT INTO materials (name, purchase_price) VALUES
('Copper cable (10m)', 25.00),
('Circuit breaker', 15.50),
('LED spotlight', 8.75),
('Junction box', 4.20);

INSERT INTO job_materials (job_id, material_id, quantity) VALUES
(1, 1, 3),   -- 3x cable
(1, 2, 2),   -- 2x breaker
(2, 1, 2),
(2, 4, 4),
(3, 3, 6);

INSERT INTO invoices (job_id, amount, payment_status) VALUES
(1, 1200.00, 'paid'),
(2, 450.00, 'unpaid');