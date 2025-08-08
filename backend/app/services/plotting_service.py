import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from datetime import datetime
import os

from app.services.ai_analysis import AIAnalysisService
from app.core.config import settings
from app.models.user import User
from app.models.company import Company
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class PlottingService:
    def __init__(self):
        self.gemini_client = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini client"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_client = genai.GenerativeModel('gemini-1.5-pro')
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.gemini_client = None

    async def extract_financial_data_from_pdf(self, pdf_content: str, user: User, db: Session) -> Dict[str, Any]:
        """Extract financial data from PDF content using Gemini"""
        if not self.gemini_client:
            raise Exception("Gemini client not initialized")

        # Get user's accessible verticals
        ai_service = AIAnalysisService()
        user_verticals = ai_service._get_user_verticals(user)
        vertical_names = user_verticals
        
        prompt = f"""
        You are a financial data extraction expert. Extract the following financial metrics from the provided balance sheet data:
        
        REQUIRED METRICS TO EXTRACT:
        1. Sales/Revenue (for the last 3-5 years if available)
        2. Growth Rate (year-over-year percentage)
        3. Total Assets (for the last 3-5 years if available)
        4. Total Liabilities (for the last 3-5 years if available)
        5. Net Worth/Equity (Assets - Liabilities)
        6. Profit Margin (if available)
        7. Debt-to-Equity Ratio (if available)
        
        IMPORTANT ACCESS CONTROL:
        - User can only access data for these verticals: {', '.join(vertical_names)}
        - If the PDF contains data for multiple companies, ONLY extract data for companies in the user's accessible verticals
        - If no data is found for user's verticals, return empty results
        
        EXTRACTION RULES:
        - Extract data in JSON format with years as keys
        - For each metric, provide both numeric value and unit (e.g., "1000000", "USD")
        - If a metric is not available, use null
        - Focus on the most recent 3-5 years of data
        - Ensure all monetary values are in the same currency (preferably USD)
        
        PDF CONTENT:
        {pdf_content}
        
        Return ONLY a valid JSON object with this structure:
        {{
            "sales": {{
                "2023": {{"value": 1000000, "unit": "USD"}},
                "2022": {{"value": 900000, "unit": "USD"}},
                "2021": {{"value": 800000, "unit": "USD"}}
            }},
            "growth_rate": {{
                "2023": {{"value": 11.11, "unit": "%"}},
                "2022": {{"value": 12.5, "unit": "%"}}
            }},
            "total_assets": {{
                "2023": {{"value": 2000000, "unit": "USD"}},
                "2022": {{"value": 1800000, "unit": "USD"}},
                "2021": {{"value": 1600000, "unit": "USD"}}
            }},
            "total_liabilities": {{
                "2023": {{"value": 800000, "unit": "USD"}},
                "2022": {{"value": 720000, "unit": "USD"}},
                "2021": {{"value": 640000, "unit": "USD"}}
            }},
            "net_worth": {{
                "2023": {{"value": 1200000, "unit": "USD"}},
                "2022": {{"value": 1080000, "unit": "USD"}},
                "2021": {{"value": 960000, "unit": "USD"}}
            }},
            "profit_margin": {{
                "2023": {{"value": 15.5, "unit": "%"}},
                "2022": {{"value": 14.2, "unit": "%"}}
            }},
            "debt_to_equity": {{
                "2023": {{"value": 0.67, "unit": "ratio"}},
                "2022": {{"value": 0.67, "unit": "ratio"}}
            }},
            "extracted_companies": ["Company names that were extracted"],
            "accessible_companies": {vertical_names},
            "currency": "USD",
            "data_quality": "high/medium/low"
        }}
        """

        try:
            response = self.gemini_client.generate_content(prompt)
            result = response.text.strip()
            
            # Clean the response to extract JSON
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            
            data = json.loads(result)
            logger.info(f"Successfully extracted financial data for user {user.username}")
            return data
            
        except Exception as e:
            logger.error(f"Error extracting financial data: {e}")
            return {
                "sales": {},
                "growth_rate": {},
                "total_assets": {},
                "total_liabilities": {},
                "net_worth": {},
                "profit_margin": {},
                "debt_to_equity": {},
                "extracted_companies": [],
                "accessible_companies": vertical_names,
                "currency": "USD",
                "data_quality": "error"
            }

    def create_financial_plots(self, financial_data: Dict[str, Any]) -> Dict[str, str]:
        """Create financial plots from extracted data"""
        plots = {}
        
        try:
            # Set style for better visibility
            plt.style.use('seaborn-v0_8-whitegrid')
            sns.set_palette("Set2")
            
            # Set default font sizes for better readability
            plt.rcParams.update({
                'font.size': 12,
                'axes.titlesize': 16,
                'axes.labelsize': 14,
                'xtick.labelsize': 12,
                'ytick.labelsize': 12,
                'legend.fontsize': 12,
                'figure.titlesize': 18
            })
            
            # 1. Sales Trend
            if financial_data.get('sales'):
                fig, ax = plt.subplots(figsize=(14, 8))
                years = list(financial_data['sales'].keys())
                sales_values = [financial_data['sales'][year]['value'] for year in years]
                
                ax.plot(years, sales_values, marker='o', linewidth=2, markersize=8)
                ax.set_title('Sales/Revenue Trend', fontsize=16, fontweight='bold')
                ax.set_xlabel('Year', fontsize=12)
                ax.set_ylabel(f"Sales ({financial_data.get('currency', 'USD')})", fontsize=12)
                ax.grid(True, alpha=0.3)
                
                # Add value labels on points
                for i, (year, value) in enumerate(zip(years, sales_values)):
                    ax.annotate(f'{value:,.0f}', (year, value), 
                               textcoords="offset points", xytext=(0,10), 
                               ha='center', fontsize=10)
                
                plt.tight_layout()
                plots['sales_trend'] = self._fig_to_base64(fig)
                plt.close()

            # 2. Growth Rate
            if financial_data.get('growth_rate'):
                fig, ax = plt.subplots(figsize=(14, 8))
                years = list(financial_data['growth_rate'].keys())
                growth_values = [financial_data['growth_rate'][year]['value'] for year in years]
                
                colors = ['green' if x > 0 else 'red' for x in growth_values]
                bars = ax.bar(years, growth_values, color=colors, alpha=0.7)
                ax.set_title('Year-over-Year Growth Rate', fontsize=16, fontweight='bold')
                ax.set_xlabel('Year', fontsize=12)
                ax.set_ylabel('Growth Rate (%)', fontsize=12)
                ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
                ax.grid(True, alpha=0.3)
                
                # Add value labels on bars
                for bar, value in zip(bars, growth_values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{value:.1f}%', ha='center', va='bottom' if height > 0 else 'top')
                
                plt.tight_layout()
                plots['growth_rate'] = self._fig_to_base64(fig)
                plt.close()

            # 3. Assets vs Liabilities
            if financial_data.get('total_assets') and financial_data.get('total_liabilities'):
                fig, ax = plt.subplots(figsize=(16, 8))
                years = list(set(financial_data['total_assets'].keys()) & 
                           set(financial_data['total_liabilities'].keys()))
                years.sort()
                
                assets_values = [financial_data['total_assets'][year]['value'] for year in years]
                liabilities_values = [financial_data['total_liabilities'][year]['value'] for year in years]
                
                x = range(len(years))
                width = 0.35
                
                ax.bar([i - width/2 for i in x], assets_values, width, label='Total Assets', alpha=0.8)
                ax.bar([i + width/2 for i in x], liabilities_values, width, label='Total Liabilities', alpha=0.8)
                
                ax.set_title('Assets vs Liabilities', fontsize=16, fontweight='bold')
                ax.set_xlabel('Year', fontsize=12)
                ax.set_ylabel(f"Amount ({financial_data.get('currency', 'USD')})", fontsize=12)
                ax.set_xticks(x)
                ax.set_xticklabels(years)
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                plt.tight_layout()
                plots['assets_vs_liabilities'] = self._fig_to_base64(fig)
                plt.close()

            # 4. Net Worth Trend
            if financial_data.get('net_worth'):
                fig, ax = plt.subplots(figsize=(14, 8))
                years = list(financial_data['net_worth'].keys())
                net_worth_values = [financial_data['net_worth'][year]['value'] for year in years]
                
                ax.fill_between(years, net_worth_values, alpha=0.3, color='green')
                ax.plot(years, net_worth_values, marker='o', linewidth=2, markersize=8, color='green')
                ax.set_title('Net Worth/Equity Trend', fontsize=16, fontweight='bold')
                ax.set_xlabel('Year', fontsize=12)
                ax.set_ylabel(f"Net Worth ({financial_data.get('currency', 'USD')})", fontsize=12)
                ax.grid(True, alpha=0.3)
                
                # Add value labels
                for i, (year, value) in enumerate(zip(years, net_worth_values)):
                    ax.annotate(f'{value:,.0f}', (year, value), 
                               textcoords="offset points", xytext=(0,10), 
                               ha='center', fontsize=10)
                
                plt.tight_layout()
                plots['net_worth'] = self._fig_to_base64(fig)
                plt.close()

            # 5. Profit Margin
            if financial_data.get('profit_margin'):
                fig, ax = plt.subplots(figsize=(14, 8))
                years = list(financial_data['profit_margin'].keys())
                margin_values = [financial_data['profit_margin'][year]['value'] for year in years]
                
                colors = ['green' if x > 10 else 'orange' if x > 5 else 'red' for x in margin_values]
                bars = ax.bar(years, margin_values, color=colors, alpha=0.7)
                ax.set_title('Profit Margin Trend', fontsize=16, fontweight='bold')
                ax.set_xlabel('Year', fontsize=12)
                ax.set_ylabel('Profit Margin (%)', fontsize=12)
                ax.axhline(y=10, color='green', linestyle='--', alpha=0.5, label='Good (>10%)')
                ax.axhline(y=5, color='orange', linestyle='--', alpha=0.5, label='Average (>5%)')
                ax.grid(True, alpha=0.3)
                ax.legend()
                
                # Add value labels
                for bar, value in zip(bars, margin_values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{value:.1f}%', ha='center', va='bottom')
                
                plt.tight_layout()
                plots['profit_margin'] = self._fig_to_base64(fig)
                plt.close()

            # 6. Debt-to-Equity Ratio
            if financial_data.get('debt_to_equity'):
                fig, ax = plt.subplots(figsize=(14, 8))
                years = list(financial_data['debt_to_equity'].keys())
                ratio_values = [financial_data['debt_to_equity'][year]['value'] for year in years]
                
                colors = ['green' if x < 1 else 'orange' if x < 2 else 'red' for x in ratio_values]
                bars = ax.bar(years, ratio_values, color=colors, alpha=0.7)
                ax.set_title('Debt-to-Equity Ratio', fontsize=16, fontweight='bold')
                ax.set_xlabel('Year', fontsize=12)
                ax.set_ylabel('Debt-to-Equity Ratio', fontsize=12)
                ax.axhline(y=1, color='green', linestyle='--', alpha=0.5, label='Good (<1)')
                ax.axhline(y=2, color='orange', linestyle='--', alpha=0.5, label='Moderate (<2)')
                ax.grid(True, alpha=0.3)
                ax.legend()
                
                # Add value labels
                for bar, value in zip(bars, ratio_values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{value:.2f}', ha='center', va='bottom')
                
                plt.tight_layout()
                plots['debt_to_equity'] = self._fig_to_base64(fig)
                plt.close()

        except Exception as e:
            logger.error(f"Error creating plots: {e}")
            plots['error'] = f"Error creating plots: {str(e)}"

        return plots

    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode()
        buf.close()
        return img_str

    async def generate_financial_analysis(self, pdf_content: str, user: User, db: Session) -> Dict[str, Any]:
        """Generate complete financial analysis with plots"""
        try:
            # Extract financial data
            financial_data = await self.extract_financial_data_from_pdf(pdf_content, user, db)
            
            # Create plots
            plots = self.create_financial_plots(financial_data)
            
            # Generate insights
            insights = self._generate_insights(financial_data)
            
            return {
                "financial_data": financial_data,
                "plots": plots,
                "insights": insights,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in financial analysis: {e}")
            return {
                "financial_data": {},
                "plots": {},
                "insights": [],
                "success": False,
                "error": str(e)
            }

    def _generate_insights(self, financial_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate insights from financial data"""
        insights = []
        
        try:
            # Sales insights
            if financial_data.get('sales'):
                sales_years = list(financial_data['sales'].keys())
                if len(sales_years) >= 2:
                    latest_sales = financial_data['sales'][sales_years[-1]]['value']
                    previous_sales = financial_data['sales'][sales_years[-2]]['value']
                    growth = ((latest_sales - previous_sales) / previous_sales) * 100
                    
                    if growth > 10:
                        insights.append({
                            "type": "positive",
                            "title": "Strong Sales Growth",
                            "description": f"Sales grew by {growth:.1f}% year-over-year, indicating strong business performance."
                        })
                    elif growth < 0:
                        insights.append({
                            "type": "warning",
                            "title": "Declining Sales",
                            "description": f"Sales declined by {abs(growth):.1f}% year-over-year, requiring attention."
                        })

            # Profit margin insights
            if financial_data.get('profit_margin'):
                margin_years = list(financial_data['profit_margin'].keys())
                if margin_years:
                    latest_margin = financial_data['profit_margin'][margin_years[-1]]['value']
                    
                    if latest_margin > 15:
                        insights.append({
                            "type": "positive",
                            "title": "Excellent Profitability",
                            "description": f"Profit margin of {latest_margin:.1f}% indicates excellent operational efficiency."
                        })
                    elif latest_margin < 5:
                        insights.append({
                            "type": "warning",
                            "title": "Low Profitability",
                            "description": f"Profit margin of {latest_margin:.1f}% suggests need for cost optimization."
                        })

            # Debt-to-equity insights
            if financial_data.get('debt_to_equity'):
                ratio_years = list(financial_data['debt_to_equity'].keys())
                if ratio_years:
                    latest_ratio = financial_data['debt_to_equity'][ratio_years[-1]]['value']
                    
                    if latest_ratio < 1:
                        insights.append({
                            "type": "positive",
                            "title": "Healthy Debt Levels",
                            "description": f"Debt-to-equity ratio of {latest_ratio:.2f} indicates conservative financial structure."
                        })
                    elif latest_ratio > 2:
                        insights.append({
                            "type": "warning",
                            "title": "High Debt Levels",
                            "description": f"Debt-to-equity ratio of {latest_ratio:.2f} suggests high financial leverage."
                        })

        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            insights.append({
                "type": "error",
                "title": "Analysis Error",
                "description": "Unable to generate insights due to data processing error."
            })

        return insights

# Global instance
plotting_service = PlottingService() 