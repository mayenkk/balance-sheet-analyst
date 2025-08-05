# Balance Sheet Analyst - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [User Roles & Permissions](#user-roles--permissions)
3. [Dashboard Overview](#dashboard-overview)
4. [AI Chat Interface](#ai-chat-interface)
5. [Financial Analysis](#financial-analysis)
6. [Company Management](#company-management)
7. [Reports & Insights](#reports--insights)
8. [Security & Best Practices](#security--best-practices)
9. [Troubleshooting](#troubleshooting)

## Getting Started

### First Time Setup

1. **Access the Application**
   - Open your web browser and navigate to `http://localhost:3000`
   - You'll be redirected to the login page

2. **Default Login Credentials**
   ```
   Username: analyst
   Password: password
   ```

3. **Complete Your Profile**
   - After first login, update your profile information
   - Add your full name and contact details
   - Change your password for security

### User Registration

1. **Navigate to Registration**
   - Click "Register" on the login page
   - Fill in the required information:
     - Email address
     - Username (unique)
     - Full name
     - Password (minimum 8 characters)
     - Role selection

2. **Role Selection**
   - **Financial Analyst**: Full access to all features
   - **CEO**: Company-specific access
   - **Top Management**: Limited access to assigned companies

## User Roles & Permissions

### Financial Analyst
**Full Access to All Features**
- View and analyze all company data
- Create and manage balance sheets
- Generate comprehensive reports
- Access AI analysis tools
- Manage user permissions (if admin)

**Key Responsibilities:**
- Data entry and validation
- Financial analysis and reporting
- AI model training and optimization
- System administration

### CEO
**Company-Specific Access**
- View assigned company data only
- Access performance metrics
- Generate company-specific reports
- Use AI analysis for decision making

**Key Responsibilities:**
- Strategic decision making
- Performance monitoring
- Risk assessment
- Stakeholder reporting

### Group CEO
**Multi-Company Access**
- View all companies in the group
- Compare performance across companies
- Generate consolidated reports
- Access group-level analytics

**Key Responsibilities:**
- Group strategy and planning
- Cross-company analysis
- Resource allocation
- Performance optimization

### Top Management
**Limited Access**
- View assigned company data
- Access basic analytics
- Generate standard reports
- Limited AI analysis

**Key Responsibilities:**
- Operational oversight
- Performance tracking
- Risk monitoring
- Team management

## Dashboard Overview

### Main Dashboard Features

1. **Key Metrics Cards**
   - Total Companies
   - Active Sessions
   - Reports Generated
   - Total Users

2. **Quick Actions**
   - Start New Analysis
   - AI Chat
   - View Reports
   - Company Overview

3. **Recent Activity**
   - Latest analysis completed
   - Recent chat sessions
   - Generated reports
   - System updates

### Navigation

- **Dashboard**: Overview and quick access
- **AI Chat**: Interactive financial analysis
- **Analysis**: Detailed financial analysis tools
- **Companies**: Company data management
- **Reports**: Generated reports and insights

## AI Chat Interface

### Starting a Chat Session

1. **Navigate to AI Chat**
   - Click "AI Chat" in the sidebar
   - You'll see existing sessions or create a new one

2. **Create New Session**
   - Click the "+" button
   - Select a company from the dropdown
   - Enter a session title
   - Click "Create"

3. **Select Existing Session**
   - Click on any existing session
   - View previous conversations
   - Continue the analysis

### Asking Questions

**Example Questions:**
- "What is the current ratio trend for Reliance Industries?"
- "How does our debt-to-equity ratio compare to industry standards?"
- "What are the key risks in our balance sheet?"
- "Generate a liquidity analysis for the past 5 years"
- "What recommendations do you have for improving working capital?"

### Understanding AI Responses

**Response Structure:**
1. **Executive Summary**: High-level overview
2. **Key Insights**: Important findings and trends
3. **Recommendations**: Actionable suggestions
4. **Supporting Data**: Relevant metrics and calculations

**Response Types:**
- **Text Analysis**: Detailed explanations
- **Structured Data**: Metrics and ratios
- **Visual Insights**: Charts and graphs
- **Action Items**: Specific recommendations

### Best Practices for AI Chat

1. **Be Specific**: Ask detailed, specific questions
2. **Provide Context**: Mention time periods or specific metrics
3. **Follow Up**: Ask clarifying questions based on responses
4. **Save Important Sessions**: Bookmark valuable conversations
5. **Export Insights**: Download important analysis results

## Financial Analysis

### Balance Sheet Analysis

1. **Navigate to Analysis**
   - Click "Analysis" in the sidebar
   - Select a company from the dropdown

2. **Key Metrics Overview**
   - **Total Assets**: Company's total resources
   - **Total Liabilities**: Company's total obligations
   - **Current Ratio**: Short-term liquidity measure
   - **Debt-to-Equity**: Financial leverage indicator

3. **Trend Analysis**
   - Historical performance tracking
   - Growth rate calculations
   - Comparative analysis
   - Risk assessment

### Performance Metrics

**Liquidity Ratios:**
- **Current Ratio**: Current assets / Current liabilities
- **Quick Ratio**: (Current assets - Inventory) / Current liabilities
- **Cash Ratio**: Cash and equivalents / Current liabilities

**Solvency Ratios:**
- **Debt-to-Equity**: Total debt / Total equity
- **Debt Ratio**: Total debt / Total assets
- **Equity Ratio**: Total equity / Total assets

**Efficiency Ratios:**
- **Asset Turnover**: Revenue / Average total assets
- **Working Capital**: Current assets - Current liabilities

### Risk Assessment

**Liquidity Risk:**
- Current ratio below 1.0 indicates potential liquidity issues
- Quick ratio below 0.8 suggests cash flow problems
- Declining working capital may signal operational challenges

**Solvency Risk:**
- Debt-to-equity ratio above 2.0 indicates high leverage
- Debt ratio above 0.6 suggests significant financial risk
- Declining equity ratio may indicate deteriorating financial health

**Market Risk:**
- Industry comparison analysis
- Economic cycle impact assessment
- Competitive position evaluation

## Company Management

### Viewing Company Data

1. **Navigate to Companies**
   - Click "Companies" in the sidebar
   - View all accessible companies

2. **Company Cards Display**
   - Company name and ticker symbol
   - Industry and sector information
   - Key financial metrics
   - Growth indicators

3. **Company Details**
   - Click "View Details" for comprehensive information
   - Historical balance sheet data
   - Performance trends
   - Risk indicators

### Company Hierarchy

**Parent-Subsidiary Structure:**
- **Reliance Industries**: Parent company
- **JIO Platforms**: Telecommunications subsidiary
- **Reliance Retail**: Retail subsidiary
- **Subsidiary Companies**: Further divisions

**Access Control:**
- CEOs can access their assigned companies
- Group CEOs can access all companies
- Analysts can access all companies
- Top management has limited access

### Data Management

**Adding New Companies:**
1. Navigate to Companies page
2. Click "Add Company" button
3. Fill in required information:
   - Company name
   - Ticker symbol
   - Industry and sector
   - Parent company (if applicable)
4. Assign users with appropriate access

**Updating Company Information:**
1. Select the company
2. Click "Edit" button
3. Update relevant fields
4. Save changes

## Reports & Insights

### Generated Reports

1. **Navigate to Reports**
   - Click "Reports" in the sidebar
   - View all available reports

2. **Report Types**
   - **Quarterly Reports**: Three-month performance analysis
   - **Annual Reports**: Year-end comprehensive analysis
   - **Custom Reports**: User-defined analysis periods
   - **Comparative Reports**: Multi-company analysis

3. **Report Status**
   - **Draft**: In progress, not finalized
   - **Final**: Completed and approved
   - **Archived**: Historical reports

### Report Features

**Interactive Elements:**
- Clickable charts and graphs
- Drill-down capabilities
- Export functionality
- Share options

**Report Content:**
- Executive summary
- Financial highlights
- Risk assessment
- Recommendations
- Supporting data

### Creating Custom Reports

1. **Report Builder**
   - Select report type
   - Choose analysis period
   - Select companies to include
   - Define metrics and ratios

2. **Customization Options**
   - Chart types and layouts
   - Color schemes
   - Data granularity
   - Export formats

3. **Scheduling Reports**
   - Set automatic generation
   - Email notifications
   - Recurring reports
   - Custom alerts

## Security & Best Practices

### Password Security

**Strong Password Requirements:**
- Minimum 8 characters
- Mix of uppercase and lowercase letters
- Include numbers and special characters
- Avoid common words and patterns

**Password Management:**
- Change passwords regularly
- Don't reuse passwords
- Use password manager tools
- Enable two-factor authentication (if available)

### Data Protection

**Access Control:**
- Log out when not using the system
- Don't share login credentials
- Report suspicious activity
- Use secure networks

**Data Handling:**
- Don't download sensitive data to personal devices
- Follow company data policies
- Report data breaches immediately
- Use encrypted connections

### Session Management

**Best Practices:**
- Set appropriate session timeouts
- Monitor active sessions
- Log out from all devices when changing passwords
- Review session history regularly

### Compliance

**Financial Compliance:**
- Follow SOX requirements
- Maintain audit trails
- Document analysis procedures
- Preserve data integrity

**Data Privacy:**
- Follow GDPR guidelines
- Minimize data collection
- Secure data transmission
- Regular privacy audits

## Troubleshooting

### Common Issues

**Login Problems:**
1. **Forgotten Password**
   - Contact system administrator
   - Provide user ID and email
   - Follow password reset process

2. **Account Locked**
   - Wait 15 minutes for automatic unlock
   - Contact administrator for immediate access
   - Review failed login attempts

**Data Access Issues:**
1. **Permission Denied**
   - Check user role and permissions
   - Contact administrator for access
   - Verify company assignments

2. **Missing Data**
   - Check date range settings
   - Verify company selection
   - Contact data administrator

**AI Analysis Issues:**
1. **Slow Responses**
   - Check internet connection
   - Try simpler questions
   - Contact technical support

2. **Inaccurate Results**
   - Verify data completeness
   - Check analysis parameters
   - Review historical data

### Performance Optimization

**Browser Recommendations:**
- Use Chrome, Firefox, or Safari
- Keep browser updated
- Clear cache regularly
- Disable unnecessary extensions

**Network Requirements:**
- Stable internet connection
- Minimum 5 Mbps download speed
- Low latency for real-time features
- Secure network connection

### Getting Help

**Support Channels:**
1. **In-App Help**: Click help icon in interface
2. **Documentation**: Access user guides and tutorials
3. **Technical Support**: Contact IT support team
4. **Training**: Request user training sessions

**Contact Information:**
- **Email**: support@balance-sheet-analyst.com
- **Phone**: +1-555-0123 (Business hours)
- **Chat**: In-app support chat
- **Knowledge Base**: Online documentation

### System Maintenance

**Scheduled Maintenance:**
- Regular system updates
- Database maintenance
- Security patches
- Performance optimization

**Notifications:**
- Email notifications for maintenance
- In-app maintenance alerts
- Status page updates
- Emergency notifications

---

## Quick Reference

### Keyboard Shortcuts
- `Ctrl + N`: New chat session
- `Ctrl + S`: Save report
- `Ctrl + E`: Export data
- `Ctrl + F`: Search
- `Ctrl + H`: Help

### Important URLs
- **Application**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Default Credentials
- **Analyst**: analyst / password
- **CEO**: ceo_reliance / password
- **Group CEO**: ceo_reliance / password

### Support Contacts
- **Technical Issues**: support@company.com
- **Data Questions**: data@company.com
- **Access Requests**: admin@company.com 