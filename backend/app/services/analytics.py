import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.balance_sheet import BalanceSheet
from app.models.company import Company


class FinancialAnalyticsService:
    """Service for financial analytics and calculations"""
    
    def calculate_key_metrics(self, balance_sheets: List[BalanceSheet]) -> Dict[str, Any]:
        """Calculate key financial metrics from balance sheet data"""
        if not balance_sheets:
            return {}
        
        # Sort by date
        sorted_bs = sorted(balance_sheets, key=lambda x: x.reporting_date)
        latest_bs = sorted_bs[-1]
        
        metrics = {
            "current_period": {
                "total_assets": float(latest_bs.total_assets or 0),
                "total_liabilities": float(latest_bs.total_liabilities or 0),
                "total_equity": float(latest_bs.total_equity or 0),
                "current_ratio": float(latest_bs.current_ratio or 0),
                "quick_ratio": float(latest_bs.quick_ratio or 0),
                "debt_to_equity": float(latest_bs.debt_to_equity_ratio or 0),
                "working_capital": float(latest_bs.working_capital or 0)
            },
            "trends": self._calculate_trends(sorted_bs),
            "growth_rates": self._calculate_growth_rates(sorted_bs),
            "ratios": self._calculate_additional_ratios(sorted_bs)
        }
        
        return metrics
    
    def _calculate_trends(self, balance_sheets: List[BalanceSheet]) -> Dict[str, List[float]]:
        """Calculate trends over time"""
        trends = {
            "periods": [],
            "total_assets": [],
            "total_liabilities": [],
            "total_equity": [],
            "current_ratio": [],
            "debt_to_equity": []
        }
        
        for bs in balance_sheets:
            trends["periods"].append(bs.reporting_date.strftime("%Y-%m-%d"))
            trends["total_assets"].append(float(bs.total_assets or 0))
            trends["total_liabilities"].append(float(bs.total_liabilities or 0))
            trends["total_equity"].append(float(bs.total_equity or 0))
            trends["current_ratio"].append(float(bs.current_ratio or 0))
            trends["debt_to_equity"].append(float(bs.debt_to_equity_ratio or 0))
        
        return trends
    
    def _calculate_growth_rates(self, balance_sheets: List[BalanceSheet]) -> Dict[str, float]:
        """Calculate year-over-year growth rates"""
        if len(balance_sheets) < 2:
            return {}
        
        latest = balance_sheets[-1]
        previous = balance_sheets[-2]
        
        def calculate_growth(current: float, previous: float) -> float:
            if previous == 0:
                return 0
            return ((current - previous) / previous) * 100
        
        growth_rates = {
            "assets_growth": calculate_growth(
                float(latest.total_assets or 0),
                float(previous.total_assets or 0)
            ),
            "liabilities_growth": calculate_growth(
                float(latest.total_liabilities or 0),
                float(previous.total_liabilities or 0)
            ),
            "equity_growth": calculate_growth(
                float(latest.total_equity or 0),
                float(previous.total_equity or 0)
            )
        }
        
        return growth_rates
    
    def _calculate_additional_ratios(self, balance_sheets: List[BalanceSheet]) -> Dict[str, float]:
        """Calculate additional financial ratios"""
        if not balance_sheets:
            return {}
        
        latest = balance_sheets[-1]
        
        # Asset utilization ratios
        total_assets = float(latest.total_assets or 0)
        current_assets = float(latest.current_assets or 0)
        current_liabilities = float(latest.current_liabilities or 0)
        total_liabilities = float(latest.total_liabilities or 0)
        total_equity = float(latest.total_equity or 0)
        
        ratios = {}
        
        # Asset composition
        if total_assets > 0:
            ratios["current_assets_ratio"] = (current_assets / total_assets) * 100
            ratios["non_current_assets_ratio"] = ((total_assets - current_assets) / total_assets) * 100
        
        # Liability composition
        if total_liabilities > 0:
            ratios["current_liabilities_ratio"] = (current_liabilities / total_liabilities) * 100
            ratios["long_term_liabilities_ratio"] = ((total_liabilities - current_liabilities) / total_liabilities) * 100
        
        # Financial leverage
        if total_equity > 0:
            ratios["debt_ratio"] = (total_liabilities / total_assets) * 100
            ratios["equity_ratio"] = (total_equity / total_assets) * 100
        
        return ratios
    
    def generate_performance_insights(self, balance_sheets: List[BalanceSheet]) -> List[Dict[str, Any]]:
        """Generate performance insights from balance sheet data"""
        insights = []
        
        if len(balance_sheets) < 2:
            return insights
        
        metrics = self.calculate_key_metrics(balance_sheets)
        trends = metrics["trends"]
        growth_rates = metrics["growth_rates"]
        
        # Asset growth analysis
        if growth_rates.get("assets_growth", 0) > 10:
            insights.append({
                "type": "positive",
                "title": "Strong Asset Growth",
                "description": f"Total assets grew by {growth_rates['assets_growth']:.1f}% year-over-year",
                "impact": "high"
            })
        elif growth_rates.get("assets_growth", 0) < -5:
            insights.append({
                "type": "negative",
                "title": "Declining Assets",
                "description": f"Total assets declined by {abs(growth_rates['assets_growth']):.1f}% year-over-year",
                "impact": "high"
            })
        
        # Liquidity analysis
        current_ratio = metrics["current_period"]["current_ratio"]
        if current_ratio > 2.0:
            insights.append({
                "type": "positive",
                "title": "Strong Liquidity",
                "description": f"Current ratio of {current_ratio:.2f} indicates strong short-term liquidity",
                "impact": "medium"
            })
        elif current_ratio < 1.0:
            insights.append({
                "type": "negative",
                "title": "Liquidity Concerns",
                "description": f"Current ratio of {current_ratio:.2f} indicates potential liquidity issues",
                "impact": "high"
            })
        
        # Debt analysis
        debt_to_equity = metrics["current_period"]["debt_to_equity"]
        if debt_to_equity > 1.0:
            insights.append({
                "type": "warning",
                "title": "High Leverage",
                "description": f"Debt-to-equity ratio of {debt_to_equity:.2f} indicates high financial leverage",
                "impact": "high"
            })
        
        return insights
    
    def compare_companies(
        self, 
        company1_bs: List[BalanceSheet], 
        company2_bs: List[BalanceSheet],
        company1_name: str,
        company2_name: str
    ) -> Dict[str, Any]:
        """Compare financial metrics between two companies"""
        
        metrics1 = self.calculate_key_metrics(company1_bs)
        metrics2 = self.calculate_key_metrics(company2_bs)
        
        comparison = {
            "companies": [company1_name, company2_name],
            "current_ratios": [
                metrics1["current_period"]["current_ratio"],
                metrics2["current_period"]["current_ratio"]
            ],
            "debt_to_equity": [
                metrics1["current_period"]["debt_to_equity"],
                metrics2["current_period"]["debt_to_equity"]
            ],
            "total_assets": [
                metrics1["current_period"]["total_assets"],
                metrics2["current_period"]["total_assets"]
            ],
            "working_capital": [
                metrics1["current_period"]["working_capital"],
                metrics2["current_period"]["working_capital"]
            ]
        }
        
        return comparison
    
    def forecast_metrics(self, balance_sheets: List[BalanceSheet], periods: int = 4) -> Dict[str, List[float]]:
        """Simple forecasting of key metrics"""
        if len(balance_sheets) < 3:
            return {}
        
        # Convert to pandas DataFrame for easier analysis
        df = pd.DataFrame([
            {
                'period': i,
                'total_assets': float(bs.total_assets or 0),
                'total_liabilities': float(bs.total_liabilities or 0),
                'total_equity': float(bs.total_equity or 0)
            }
            for i, bs in enumerate(balance_sheets)
        ])
        
        forecasts = {}
        
        # Simple linear trend forecasting
        for metric in ['total_assets', 'total_liabilities', 'total_equity']:
            if len(df) >= 2:
                # Calculate trend
                x = df['period'].values
                y = df[metric].values
                
                # Simple linear regression
                slope = np.polyfit(x, y, 1)[0]
                intercept = np.polyfit(x, y, 1)[1]
                
                # Forecast future periods
                future_periods = range(len(df), len(df) + periods)
                forecast_values = [slope * p + intercept for p in future_periods]
                
                forecasts[metric] = forecast_values
        
        return forecasts 