-- Sample data for Balance Sheet Analyst (RAG/PDF version)

-- Insert sample companies (Reliance Group)
INSERT INTO companies (name, ticker_symbol, industry, sector, description, parent_company_id, is_active, created_at, updated_at) VALUES
('Reliance Industries Limited', 'RELIANCE', 'Oil & Gas', 'Energy', 'India''s largest private sector company with interests in energy, petrochemicals, natural gas, retail, telecommunications, mass media, and textiles.', NULL, true, NOW(), NOW()),
('JIO Platforms Limited', 'JIO', 'Telecommunications', 'Technology', 'Digital services company providing broadband and digital solutions.', 1, true, NOW(), NOW()),
('Reliance Retail Ventures Limited', 'RRVL', 'Retail', 'Consumer Discretionary', 'Retail business with presence across grocery, consumer electronics, fashion and lifestyle.', 1, true, NOW(), NOW()),
('Reliance Jio Infocomm Limited', 'JIOINFO', 'Telecommunications', 'Technology', 'Telecommunications services provider.', 2, true, NOW(), NOW()),
('Reliance Digital Limited', 'RDIGITAL', 'Retail', 'Consumer Discretionary', 'Consumer electronics retail chain.', 3, true, NOW(), NOW());

-- Insert sample users
INSERT INTO users (email, username, full_name, hashed_password, role, is_active, created_at, updated_at) VALUES
('analyst@company.com', 'analyst', 'Financial Analyst', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'analyst', true, NOW(), NOW()),
('ceo@reliance.com', 'ceo_reliance', 'Mukesh Ambani', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'group_ceo', true, NOW(), NOW()),
('ceo@jio.com', 'ceo_jio', 'JIO CEO', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'ceo', true, NOW(), NOW()),
('ceo@retail.com', 'ceo_retail', 'Retail CEO', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'ceo', true, NOW(), NOW()),
('management@reliance.com', 'mgmt_reliance', 'Top Management', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'top_management', true, NOW(), NOW());

-- Assign users to companies
INSERT INTO user_companies (user_id, company_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), -- Analyst has access to all companies
(2, 1), (2, 2), (2, 3), (2, 4), (2, 5), -- Group CEO has access to all companies
(3, 2), (3, 4), -- JIO CEO has access to JIO companies
(4, 3), (4, 5), -- Retail CEO has access to retail companies
(5, 1), (5, 2), (5, 3); -- Top management has access to main companies
