-- Sample data for Balance Sheet Analyst (RAG/PDF version)

-- Insert sample companies (Reliance Group)
INSERT INTO companies (name, ticker_symbol, industry, sector, description, parent_company_id, is_active, created_at, updated_at) VALUES
('Reliance Industries Limited', 'RELIANCE', 'Oil & Gas', 'Energy', 'India''s largest private sector company with interests in energy, petrochemicals, natural gas, retail, telecommunications, mass media, and textiles.', NULL, true, NOW(), NOW()),
('JIO Platforms Limited', 'JIO', 'Telecommunications', 'Technology', 'Digital services company providing broadband and digital solutions.', 1, true, NOW(), NOW()),
('Reliance Retail Ventures Limited', 'RRVL', 'Retail', 'Consumer Discretionary', 'Retail business with presence across grocery, consumer electronics, fashion and lifestyle.', 1, true, NOW(), NOW()),
('Reliance Jio Infocomm Limited', 'JIOINFO', 'Telecommunications', 'Technology', 'Telecommunications services provider.', 2, true, NOW(), NOW()),
('Reliance Digital Limited', 'RDIGITAL', 'Retail', 'Consumer Discretionary', 'Consumer electronics retail chain.', 3, true, NOW(), NOW()),
('Oil to Chemicals (O2C)', 'O2C', 'Oil & Gas', 'Energy', 'Integrated oil to chemicals business', 1, true, NOW(), NOW()),
('Oil & Gas', 'OILGAS', 'Oil & Gas', 'Energy', 'Upstream and downstream oil & gas operations', 1, true, NOW(), NOW()),
('Financial Services', 'FIN', 'Financial Services', 'Finance', 'Banking, insurance, and investment services', 1, true, NOW(), NOW()),
('Media & Entertainment', 'MEDIA', 'Media & Entertainment', 'Entertainment', 'Broadcasting, digital media, and entertainment', 1, true, NOW(), NOW()),
('New Energy & Materials', 'NEM', 'Energy', 'Energy', 'Renewable energy and advanced materials', 1, true, NOW(), NOW());

-- Insert sample users
INSERT INTO users (email, username, full_name, hashed_password, role, is_active, created_at, updated_at) VALUES
('analyst@company.com', 'analyst', 'Financial Analyst', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'analyst', true, NOW(), NOW()),
('ceo@reliance.com', 'ceo_reliance', 'Mukesh Ambani', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'group_ceo', true, NOW(), NOW()),
('ceo@jio.com', 'ceo_jio', 'JIO CEO', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'ceo', true, NOW(), NOW()),
('ceo@retail.com', 'ceo_retail', 'Retail CEO', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'ceo', true, NOW(), NOW()),
('management@reliance.com', 'mgmt_reliance', 'Top Management', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'top_management', true, NOW(), NOW()),
('ceo@o2c.com', 'ceo_o2c', 'O2C CEO', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'ceo', true, NOW(), NOW()),
('ceo@oilgas.com', 'ceo_oilgas', 'Oil & Gas CEO', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'ceo', true, NOW(), NOW()),
('ceo@financial.com', 'ceo_financial', 'Financial Services CEO', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'ceo', true, NOW(), NOW()),
('ceo@media.com', 'ceo_media', 'Media & Entertainment CEO', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'ceo', true, NOW(), NOW()),
('ceo@newenergy.com', 'ceo_newenergy', 'New Energy & Materials CEO', '$2b$12$/3hnWfRsri7v/XSi87B5U.mBsbidwDMv4fytWysz9LFIwrcIKptfS', 'ceo', true, NOW(), NOW());

-- Assign users to companies
INSERT INTO user_companies (user_id, company_id) VALUES
-- Analyst has access to all companies
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10),
-- Group CEO has access to all companies
(2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10),
-- JIO CEO has access to JIO companies
(3, 2), (3, 4),
-- Retail CEO has access to retail companies
(4, 3), (4, 5),
-- Top management has access to main companies
(5, 1), (5, 2), (5, 3),
-- O2C CEO has access to O2C
(6, 6),
-- Oil & Gas CEO has access to Oil & Gas
(7, 7),
-- Financial Services CEO has access to Financial Services
(8, 8),
-- Media & Entertainment CEO has access to Media & Entertainment
(9, 9),
-- New Energy & Materials CEO has access to New Energy & Materials
(10, 10);
