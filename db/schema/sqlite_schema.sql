PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

-- Interest Groups Table
CREATE TABLE "interest_groups" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "code" VARCHAR(50) NOT NULL,
    "description" TEXT,
    "group_permissions" TEXT,
    "ai_functionality" TEXT,
    "typical_tasks" TEXT,
    "is_external" BOOLEAN NOT NULL DEFAULT 0,
    "is_active" BOOLEAN NOT NULL DEFAULT 1,
    "created_at" DATETIME NOT NULL DEFAULT (datetime('now'))
);

-- Users Table
CREATE TABLE "users" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "email" VARCHAR(100) NOT NULL,
    "full_name" VARCHAR(200) NOT NULL,
    "employee_id" VARCHAR(50),
    "organizational_unit" VARCHAR(100),
    "hashed_password" VARCHAR(255),
    "individual_permissions" TEXT,
    "is_department_head" BOOLEAN NOT NULL DEFAULT 0,
    "approval_level" INTEGER DEFAULT 1,
    "is_active" BOOLEAN NOT NULL DEFAULT 1,
    "created_at" DATETIME NOT NULL DEFAULT (datetime('now'))
);

-- User Group Memberships Table
CREATE TABLE "user_group_memberships" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "user_id" INTEGER NOT NULL,
    "interest_group_id" INTEGER NOT NULL,
    "role_in_group" VARCHAR(50),
    "approval_level" INTEGER NOT NULL DEFAULT 1,
    "is_department_head" BOOLEAN NOT NULL DEFAULT 0,
    "is_active" BOOLEAN NOT NULL DEFAULT 1,
    "joined_at" DATETIME NOT NULL DEFAULT (datetime('now')),
    "assigned_by_id" INTEGER,
    "notes" TEXT,
    FOREIGN KEY("user_id") REFERENCES "users"("id"),
    FOREIGN KEY("interest_group_id") REFERENCES "interest_groups"("id"),
    FOREIGN KEY("assigned_by_id") REFERENCES "users"("id")
);

-- Documents Table
CREATE TABLE "documents" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "document_number" VARCHAR(50) NOT NULL,
    "document_type" VARCHAR(50) DEFAULT 'OTHER',
    "version" VARCHAR(20) NOT NULL DEFAULT '1.0',
    "status" VARCHAR(50) DEFAULT 'draft',
    "content" TEXT,
    "file_path" VARCHAR(500),
    "file_hash" VARCHAR(64),
    "file_size" INTEGER,
    "creator_id" INTEGER,
    "reviewer_id" INTEGER,
    "approver_id" INTEGER,
    "created_at" DATETIME NOT NULL DEFAULT (datetime('now')),
    "updated_at" DATETIME NOT NULL DEFAULT (datetime('now')),
    "approved_at" DATETIME,
    "is_active" BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY("creator_id") REFERENCES "users"("id"),
    FOREIGN KEY("reviewer_id") REFERENCES "users"("id"),
    FOREIGN KEY("approver_id") REFERENCES "users"("id")
);

-- Indexes
CREATE INDEX "ix_interest_groups_name" ON "interest_groups" ("name");
CREATE INDEX "ix_interest_groups_code" ON "interest_groups" ("code");
CREATE INDEX "ix_users_email" ON "users" ("email");
CREATE INDEX "ix_users_employee_id" ON "users" ("employee_id");
CREATE INDEX "ix_user_group_memberships_user_id" ON "user_group_memberships" ("user_id");
CREATE INDEX "ix_user_group_memberships_interest_group_id" ON "user_group_memberships" ("interest_group_id");
CREATE INDEX "ix_documents_title" ON "documents" ("title");
CREATE INDEX "ix_documents_document_number" ON "documents" ("document_number");
CREATE INDEX "ix_documents_status" ON "documents" ("status");

-- Unique Constraints
CREATE UNIQUE INDEX "ix_interest_groups_name_unique" ON "interest_groups" ("name");
CREATE UNIQUE INDEX "ix_interest_groups_code_unique" ON "interest_groups" ("code");
CREATE UNIQUE INDEX "ix_users_email_unique" ON "users" ("email");
CREATE UNIQUE INDEX "ix_users_employee_id_unique" ON "users" ("employee_id");
CREATE UNIQUE INDEX "ix_documents_document_number_unique" ON "documents" ("document_number");

COMMIT;
PRAGMA foreign_keys=ON;
