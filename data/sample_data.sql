-- Sample data for Balance Sheet Analyst

-- Insert sample companies (Reliance Group)
INSERT INTO companies (name, ticker_symbol, industry, sector, description, parent_company_id, is_active, created_at, updated_at) VALUES
('Reliance Industries Limited', 'RELIANCE', 'Oil & Gas', 'Energy', 'India''s largest private sector company with interests in energy, petrochemicals, natural gas, retail, telecommunications, mass media, and textiles.', NULL, true, NOW(), NOW()),
('JIO Platforms Limited', 'JIO', 'Telecommunications', 'Technology', 'Digital services company providing broadband and digital solutions.', 1, true, NOW(), NOW()),
('Reliance Retail Ventures Limited', 'RRVL', 'Retail', 'Consumer Discretionary', 'Retail business with presence across grocery, consumer electronics, fashion and lifestyle.', 1, true, NOW(), NOW()),
('Reliance Jio Infocomm Limited', 'JIOINFO', 'Telecommunications', 'Technology', 'Telecommunications services provider.', 2, true, NOW(), NOW()),
('Reliance Digital Limited', 'RDIGITAL', 'Retail', 'Consumer Discretionary', 'Consumer electronics retail chain.', 3, true, NOW(), NOW());

-- Insert sample users
INSERT INTO users (email, username, full_name, hashed_password, role, is_active, created_at, updated_at) VALUES
('analyst@company.com', 'analyst', 'Financial Analyst', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', 'analyst', true, NOW(), NOW()),
('ceo@reliance.com', 'ceo_reliance', 'Mukesh Ambani', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', 'group_ceo', true, NOW(), NOW()),
('ceo@jio.com', 'ceo_jio', 'JIO CEO', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', 'ceo', true, NOW(), NOW()),
('ceo@retail.com', 'ceo_retail', 'Retail CEO', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', 'ceo', true, NOW(), NOW()),
('management@reliance.com', 'mgmt_reliance', 'Top Management', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', 'top_management', true, NOW(), NOW());

-- Assign users to companies
INSERT INTO user_companies (user_id, company_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), -- Analyst has access to all companies
(2, 1), (2, 2), (2, 3), (2, 4), (2, 5), -- Group CEO has access to all companies
(3, 2), (3, 4), -- JIO CEO has access to JIO companies
(4, 3), (4, 5), -- Retail CEO has access to retail companies
(5, 1), (5, 2), (5, 3); -- Top management has access to main companies

-- Insert sample balance sheet data for Reliance Industries (2020-2023)
INSERT INTO balance_sheets (company_id, reporting_date, period_end_date, currency, total_assets, current_assets, cash_and_cash_equivalents, accounts_receivable, inventory, non_current_assets, property_plant_equipment, intangible_assets, goodwill, total_liabilities, current_liabilities, accounts_payable, short_term_debt, non_current_liabilities, long_term_debt, total_equity, common_stock, retained_earnings, treasury_stock, working_capital, debt_to_equity_ratio, current_ratio, quick_ratio, source, notes, is_audited, created_at, updated_at) VALUES
-- 2020
(1, '2020-03-31', '2020-03-31', 'INR', 15000000000000, 4500000000000, 1200000000000, 800000000000, 2500000000000, 10500000000000, 8000000000000, 1500000000000, 1000000000000, 9000000000000, 3000000000000, 1200000000000, 800000000000, 6000000000000, 4000000000000, 6000000000000, 3000000000000, 3000000000000, 0, 1500000000000, 1.5, 1.5, 1.23, 'public_filing', 'Annual Report 2020', true, NOW(), NOW()),
-- 2021
(1, '2021-03-31', '2021-03-31', 'INR', 16500000000000, 5000000000000, 1400000000000, 900000000000, 2700000000000, 11500000000000, 8500000000000, 1800000000000, 1200000000000, 9500000000000, 3200000000000, 1300000000000, 900000000000, 6300000000000, 4200000000000, 7000000000000, 3500000000000, 3500000000000, 0, 1800000000000, 1.36, 1.56, 1.28, 'public_filing', 'Annual Report 2021', true, NOW(), NOW()),
-- 2022
(1, '2022-03-31', '2022-03-31', 'INR', 18000000000000, 5500000000000, 1600000000000, 1000000000000, 2900000000000, 12500000000000, 9000000000000, 2000000000000, 1500000000000, 10000000000000, 3400000000000, 1400000000000, 1000000000000, 6600000000000, 4400000000000, 8000000000000, 4000000000000, 4000000000000, 0, 2100000000000, 1.25, 1.62, 1.32, 'public_filing', 'Annual Report 2022', true, NOW(), NOW()),
-- 2023
(1, '2023-03-31', '2023-03-31', 'INR', 20000000000000, 6000000000000, 1800000000000, 1100000000000, 3100000000000, 14000000000000, 10000000000000, 2200000000000, 1800000000000, 11000000000000, 3600000000000, 1500000000000, 1100000000000, 7400000000000, 4800000000000, 9000000000000, 4500000000000, 4500000000000, 0, 2400000000000, 1.22, 1.67, 1.36, 'public_filing', 'Annual Report 2023', true, NOW(), NOW());

-- Insert sample balance sheet data for JIO Platforms (2021-2023)
INSERT INTO balance_sheets (company_id, reporting_date, period_end_date, currency, total_assets, current_assets, cash_and_cash_equivalents, accounts_receivable, inventory, non_current_assets, property_plant_equipment, intangible_assets, goodwill, total_liabilities, current_liabilities, accounts_payable, short_term_debt, non_current_liabilities, long_term_debt, total_equity, common_stock, retained_earnings, treasury_stock, working_capital, debt_to_equity_ratio, current_ratio, quick_ratio, source, notes, is_audited, created_at, updated_at) VALUES
-- 2021
(2, '2021-03-31', '2021-03-31', 'INR', 8000000000000, 2500000000000, 800000000000, 400000000000, 1300000000000, 5500000000000, 4000000000000, 800000000000, 700000000000, 4500000000000, 1500000000000, 600000000000, 400000000000, 3000000000000, 2000000000000, 3500000000000, 2000000000000, 1500000000000, 0, 1000000000000, 1.29, 1.67, 1.47, 'public_filing', 'Annual Report 2021', true, NOW(), NOW()),
-- 2022
(2, '2022-03-31', '2022-03-31', 'INR', 9000000000000, 2800000000000, 900000000000, 450000000000, 1450000000000, 6200000000000, 4500000000000, 900000000000, 800000000000, 4800000000000, 1600000000000, 650000000000, 450000000000, 3200000000000, 2100000000000, 4200000000000, 2200000000000, 2000000000000, 0, 1200000000000, 1.14, 1.75, 1.54, 'public_filing', 'Annual Report 2022', true, NOW(), NOW()),
-- 2023
(2, '2023-03-31', '2023-03-31', 'INR', 10000000000000, 3200000000000, 1000000000000, 500000000000, 1700000000000, 6800000000000, 5000000000000, 1000000000000, 800000000000, 5200000000000, 1700000000000, 700000000000, 500000000000, 3500000000000, 2300000000000, 4800000000000, 2400000000000, 2400000000000, 0, 1500000000000, 1.08, 1.88, 1.59, 'public_filing', 'Annual Report 2023', true, NOW(), NOW());

-- Insert sample balance sheet data for Reliance Retail (2021-2023)
INSERT INTO balance_sheets (company_id, reporting_date, period_end_date, currency, total_assets, current_assets, cash_and_cash_equivalents, accounts_receivable, inventory, non_current_assets, property_plant_equipment, intangible_assets, goodwill, total_liabilities, current_liabilities, accounts_payable, short_term_debt, non_current_liabilities, long_term_debt, total_equity, common_stock, retained_earnings, treasury_stock, working_capital, debt_to_equity_ratio, current_ratio, quick_ratio, source, notes, is_audited, created_at, updated_at) VALUES
-- 2021
(3, '2021-03-31', '2021-03-31', 'INR', 4000000000000, 1500000000000, 400000000000, 300000000000, 800000000000, 2500000000000, 1800000000000, 400000000000, 300000000000, 2500000000000, 800000000000, 300000000000, 200000000000, 1700000000000, 1100000000000, 1500000000000, 800000000000, 700000000000, 0, 700000000000, 1.67, 1.88, 1.38, 'public_filing', 'Annual Report 2021', true, NOW(), NOW()),
-- 2022
(3, '2022-03-31', '2022-03-31', 'INR', 4500000000000, 1700000000000, 450000000000, 350000000000, 900000000000, 2800000000000, 2000000000000, 450000000000, 350000000000, 2700000000000, 850000000000, 320000000000, 230000000000, 1850000000000, 1200000000000, 1800000000000, 900000000000, 900000000000, 0, 850000000000, 1.50, 2.00, 1.41, 'public_filing', 'Annual Report 2022', true, NOW(), NOW()),
-- 2023
(3, '2023-03-31', '2023-03-31', 'INR', 5000000000000, 1900000000000, 500000000000, 400000000000, 1000000000000, 3100000000000, 2200000000000, 500000000000, 400000000000, 2900000000000, 900000000000, 350000000000, 250000000000, 2000000000000, 1300000000000, 2100000000000, 1000000000000, 1100000000000, 0, 1000000000000, 1.38, 2.11, 1.44, 'public_filing', 'Annual Report 2023', true, NOW(), NOW());

-- Insert sample chat sessions
INSERT INTO chat_sessions (user_id, company_id, title, session_type, is_active, created_at, updated_at) VALUES
(1, 1, 'Reliance Industries Q3 Analysis', 'analysis', true, NOW(), NOW()),
(2, 1, 'Group Performance Review', 'analysis', true, NOW(), NOW()),
(3, 2, 'JIO Financial Performance', 'analysis', true, NOW(), NOW()),
(4, 3, 'Retail Business Analysis', 'analysis', true, NOW(), NOW());

-- Insert sample chat messages
INSERT INTO chat_messages (session_id, role, content, metadata, tokens_used, response_time_ms, created_at) VALUES
(1, 'user', 'What is the current ratio trend for Reliance Industries?', NULL, 0, 0, NOW()),
(1, 'assistant', 'Based on the balance sheet data, Reliance Industries shows a positive trend in current ratio:\n\n- 2020: 1.50\n- 2021: 1.56\n- 2022: 1.62\n- 2023: 1.67\n\nThe current ratio has improved consistently over the past 4 years, indicating strengthening liquidity position.', '{"insights": [{"title": "Improving Liquidity", "description": "Current ratio increased from 1.50 to 1.67 over 4 years", "impact": "positive", "trend": "positive"}]}', 150, 1200, NOW()),
(2, 'user', 'How does the debt-to-equity ratio compare across our group companies?', NULL, 0, 0, NOW()),
(2, 'assistant', 'Here is the debt-to-equity ratio comparison across Reliance Group companies:\n\n- Reliance Industries: 1.22 (2023)\n- JIO Platforms: 1.08 (2023)\n- Reliance Retail: 1.38 (2023)\n\nJIO Platforms has the lowest leverage, while Reliance Retail has slightly higher leverage. All ratios are within acceptable ranges.', '{"insights": [{"title": "Conservative Leverage", "description": "All group companies maintain reasonable debt levels", "impact": "positive", "trend": "stable"}]}', 180, 1500, NOW()); 