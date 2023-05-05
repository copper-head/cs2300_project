
-- WELFARE PROGRAM SAMPLE DATA --
INSERT INTO welfare_programs VALUES("MOAR FOOD", "FOOD", "1");
INSERT INTO welfare_programs VALUES("BLING BLING", "FINANCIAL", "1");

-- INSERTS REVIEW STAFF USER INTO DB -- (username: jstalin, password: purge)
INSERT INTO users(user_name, password_hash, password_salt) VALUES("jstalin", "8035d13f7081666a3f413621521f81ce37c699e2a3b2f3e5500c53756d6d9e7b", "afa4e3fc7807bfd751c8cdc132973fce");
INSERT INTO review_staff(user_id, first_name, last_name) VALUES((SELECT id FROM users WHERE user_name="jstalin"), "Joseph", "Stalin");