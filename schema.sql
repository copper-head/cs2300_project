-- ================ USERS AND SUBUSERS SCHEMA ================ --

CREATE TABLE users
(
    id INTEGER UNIQUE PRIMARY KEY,
    user_name TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    password_salt TEXT NOT NULL,
    is_enabled INTEGER DEFAULT 1                        -- Sqlite3 has no "bool" datatype. Use INT instead.
);

CREATE TABLE applicants 
(
    user_id INT UNIQUE,
    birth_date TEXT,
    first_name TEXT,
    last_name TEXT,
    address TEXT, -- Once again, we might serialize
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE review_staff 
(
    user_id INT UNIQUE,
    first_name TEXT,
    last_name TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE executives 
(
    user_id INT UNIQUE,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- ================ APPLICATIONS SCHEMA ================ --

CREATE TABLE welfare_programs 
(
    name TEXT UNIQUE,
    plan_type TEXT,
    availabe_plans TEXT,
    is_available
);

CREATE TABLE applications 
(
    applicant_id TEXT UNIQUE,
    welfare_program_id TEXT NOT NULL,
    ly_income REAL DEFAULT 0,
    has_disability INT DEFAULT 0,
    reliability_points INT NOT NULL,
    review_status TEXT NOT NULL,
    auditor_id TEXT NOT NULL,
    FOREIGN KEY (auditor_id) REFERENCES review_staff(user_id),
    FOREIGN KEY (applicant_id) REFERENCES applicants(user_id)
);