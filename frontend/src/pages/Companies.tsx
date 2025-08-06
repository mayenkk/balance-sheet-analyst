import React from 'react';
import { useQuery } from 'react-query';
import { Building, TrendingUp, TrendingDown, Eye, BarChart3 } from 'lucide-react';
import { companyAPI } from '../services/api.ts';

const Companies: React.FC = () => {
  const { data: companies, isLoading } = useQuery('companies', companyAPI.getCompanies);

  // Mock data for demonstration
  const mockCompanies = [
    {
      id: 1,
      name: 'Reliance Industries Limited',
      ticker: 'RELIANCE',
      industry: 'Oil & Gas',
      sector: 'Energy',
      total_assets: 2500000000000,
      total_liabilities: 1800000000000,
      current_ratio: 1.85,
      debt_to_equity: 0.72,
      growth_rate: 12.5,
    },
    {
      id: 2,
      name: 'JIO Platforms Limited',
      ticker: 'JIO',
      industry: 'Telecommunications',
      sector: 'Technology',
      total_assets: 850000000000,
      total_liabilities: 520000000000,
      current_ratio: 2.1,
      debt_to_equity: 0.45,
      growth_rate: 18.2,
    },
    {
      id: 3,
      name: 'Reliance Retail Ventures Limited',
      ticker: 'RRVL',
      industry: 'Retail',
      sector: 'Consumer Discretionary',
      total_assets: 420000000000,
      total_liabilities: 280000000000,
      current_ratio: 1.65,
      debt_to_equity: 0.58,
      growth_rate: 15.8,
    },
  ];

  const formatCurrency = (amount: number) => {
    if (amount >= 1e12) {
      return `$${(amount / 1e12).toFixed(1)}T`;
    } else if (amount >= 1e9) {
      return `$${(amount / 1e9).toFixed(1)}B`;
    } else if (amount >= 1e6) {
      return `$${(amount / 1e6).toFixed(1)}M`;
    }
    return `$${amount.toLocaleString()}`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Companies</h1>
        <p className="mt-1 text-sm text-gray-500">
          Browse and analyze company financial data and performance metrics.
        </p>
      </div>

      {/* Company Cards */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
        {mockCompanies.map((company) => (
          <div key={company.id} className="bg-white shadow rounded-lg overflow-hidden">
            <div className="p-6">
              {/* Company Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className="h-10 w-10 bg-blue-600 rounded-lg flex items-center justify-center">
                    <Building className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-lg font-semibold text-gray-900">{company.name}</h3>
                    <p className="text-sm text-gray-500">{company.ticker}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                    <Eye className="h-5 w-5" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                    <BarChart3 className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Company Info */}
              <div className="space-y-3 mb-6">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Industry</span>
                  <span className="text-sm font-medium text-gray-900">{company.industry}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Sector</span>
                  <span className="text-sm font-medium text-gray-900">{company.sector}</span>
                </div>
              </div>

              {/* Financial Metrics */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-500">Total Assets</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {formatCurrency(company.total_assets)}
                  </div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-500">Total Liabilities</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {formatCurrency(company.total_liabilities)}
                  </div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-500">Current Ratio</div>
                  <div className="text-lg font-semibold text-gray-900">{company.current_ratio}</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-500">Debt/Equity</div>
                  <div className="text-lg font-semibold text-gray-900">{company.debt_to_equity}</div>
                </div>
              </div>

              {/* Growth Indicator */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Growth Rate</span>
                <div className="flex items-center">
                  {company.growth_rate > 0 ? (
                    <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
                  )}
                  <span
                    className={`text-sm font-medium ${
                      company.growth_rate > 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {company.growth_rate > 0 ? '+' : ''}{company.growth_rate}%
                  </span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="bg-gray-50 px-6 py-3 flex space-x-3">
              <button className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors">
                View Details
              </button>
              <button className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-300 transition-colors">
                Analyze
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Portfolio Summary</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{mockCompanies.length}</div>
            <div className="text-sm text-gray-500">Total Companies</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatCurrency(mockCompanies.reduce((sum, c) => sum + c.total_assets, 0))}
            </div>
            <div className="text-sm text-gray-500">Total Assets</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {(mockCompanies.reduce((sum, c) => sum + c.current_ratio, 0) / mockCompanies.length).toFixed(2)}
            </div>
            <div className="text-sm text-gray-500">Avg Current Ratio</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {(mockCompanies.reduce((sum, c) => sum + c.growth_rate, 0) / mockCompanies.length).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-500">Avg Growth Rate</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Companies; 