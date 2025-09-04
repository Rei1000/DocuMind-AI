-- Seed data for interest_groups table
-- Synthetic data since source DB is empty

INSERT INTO "interest_groups" ("name", "code", "description", "group_permissions", "ai_functionality", "typical_tasks", "is_external", "is_active", "created_at") VALUES 
('Quality Management', 'qm_team', 'Core QM team responsible for quality assurance and compliance', '["document_approval", "audit_management", "compliance_monitoring"]', 'Document analysis, compliance checking, risk assessment', 'Quality audits, document reviews, compliance monitoring, CAPA management', 0, 1, datetime('now'));

-- Seed data for users table
INSERT INTO "users" ("email", "full_name", "employee_id", "organizational_unit", "hashed_password", "individual_permissions", "is_department_head", "approval_level", "is_active", "created_at") VALUES 
('qm.manager@company.com', 'QM Manager', 'EMP001', 'Quality Management', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8QqHh2O', '["full_access", "user_management"]', 1, 5, 1, datetime('now'));

-- Seed data for user_group_memberships table
INSERT INTO "user_group_memberships" ("user_id", "interest_group_id", "role_in_group", "approval_level", "is_department_head", "is_active", "joined_at") VALUES 
(1, 1, 'Department Head', 5, 1, 1, datetime('now'));
