-- Mock data for careplan_generator tables
-- Use in psql: \i /path/to/seed_mock_data.sql

BEGIN;

TRUNCATE TABLE
  careplan_generator_careplan,
  careplan_generator_order,
  careplan_generator_doctor,
  careplan_generator_patient
RESTART IDENTITY CASCADE;

INSERT INTO careplan_generator_patient (name, email, created_at)
VALUES
  ('Alice Zhang', 'alice@example.com', NOW()),
  ('Bob Li', 'bob@example.com', NOW()),
  ('Chen Wang', 'chen@example.com', NOW());

INSERT INTO careplan_generator_doctor (name, email, created_at)
VALUES
  ('Dr. Emily Chen', 'emily.chen@example.com', NOW()),
  ('Dr. Daniel Zhao', 'daniel.zhao@example.com', NOW());

INSERT INTO careplan_generator_order (patient_id, doctor_id, note, created_at)
VALUES
  (1, 1, '68-year-old male with hypertension and diabetes. Fatigue and dizziness for 2 weeks.', NOW()),
  (2, 2, '55-year-old female with COPD. Shortness of breath and cough for 3 days.', NOW()),
  (3, NULL, '72-year-old male, post-op knee replacement. Needs rehab plan.', NOW());

INSERT INTO careplan_generator_careplan (order_id, care_plan_text, status, created_at, updated_at)
VALUES
  (1, 'Monitor BP and glucose daily. Encourage low-salt diet. Medication adherence. Follow-up in 2 weeks.', 'COMPLETED', NOW(), NOW()),
  (2, 'Assess respiratory status. Provide bronchodilators as ordered. Encourage breathing exercises.', 'PROCESSING', NOW(), NOW()),
  (3, NULL, 'PENDING', NOW(), NOW());

COMMIT;
