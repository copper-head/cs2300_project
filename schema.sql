-- ================ USERS AND SUBUSERS SCHEMA ================ --

CREATE TABLE users
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    password_salt TEXT NOT NULL,
    is_enabled INTEGER DEFAULT 1                        -- Sqlite3 has no "bool" datatype. Use INT instead.
);

CREATE TABLE applicants 
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT UNIQUE,
    birth_date TEXT,
    first_name TEXT,
    last_name TEXT,
    address TEXT, -- Once again, we might serialize
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE review_staff 
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    is_available INT DEFAULT 1
);

CREATE TABLE applications 
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    applicant_id INT NOT NULL,
    submission_date TEXT NOT NULL,
    welfare_program TEXT NOT NULL,
    ly_income REAL DEFAULT 0,
    has_disability INT DEFAULT 0,
    reliability_points INT NOT NULL,
    review_status TEXT NOT NULL DEFAULT "unreviewed",
    auditor_id INT,
    FOREIGN KEY (auditor_id) REFERENCES review_staff(user_id),
    FOREIGN KEY (applicant_id) REFERENCES applicants(id)
);

-- ================== TOKEN SCHEMA ==================== --

CREATE TABLE session_tokens 
(
    user_id INT NOT NULL,
    token TEXT NOT NULL,
    expiration_time TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE staff_tokens 
(
    user_id INT NOT NULL,
    token TEXT NOT NULL,
    expiration_time TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);