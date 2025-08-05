import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { BarChart3, TrendingUp, TrendingDown, DollarSign, Building } from 'lucide-react';
import { companyAPI } from '../services/api';

const Analysis: React.FC = () => {
  const [selectedCompany, setSelectedCompany] = useState<number | null>(null);

  const companies = [
    { id: 1, name: 'Reliance Industries', ticker: 'RELIANCE' },
    { id: 2, name: 'JIO Platforms', ticker: 'JIO' },
    { id: 3, name: 'Reliance Retail', ticker: 'RRVL' },
  ];

  const { data: balanceSheets, isLoading } = useQuery(
    ['balance-sheets', selectedCompany],
    () => companyAPI.getBalanceSheets(selectedCompany!),
    { enabled: !!selectedCompany }
  );

  const metrics = [
    {
      name: 'Total Assets',
      value: '$2.5T',
      change: '+12.5%',
      changeType: 'positive',
      icon: Building,
    },
    {
      name: 'Total Liabilities',
      value: '$1.8T',
      change: '+8.2%',
      changeType: 'positive',
      icon: DollarSign,
    },
    {
      name: 'Current Ratio',
      value: '1.85',
      change: '+0.15',
      changeType: 'positive',
      icon: TrendingUp,
    },
    {
      name: 'Debt-to-Equity',
      value: '0.72',
      change: '-0.08',
      changeType: 'negative',
      icon: TrendingDown,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Financial Analysis</h1>
        <p className="mt-1 text-sm text-gray-500">
          Comprehensive analysis of company financial performance and trends.
        </p>
      </div>

      {/* Company Selector */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Select Company</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {companies.map((company) => (
            <button
              key={company.id}
              onClick={() => setSelectedCompany(company.id)}
              className={`p-4 border rounded-lg text-left transition-colors ${
                selectedCompany === company.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="font-medium text-gray-900">{company.name}</div>
              <div className="text-sm text-gray-500">{company.ticker}</div>
            </button>
          ))}
        </div>
      </div>

      {selectedCompany && (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {metrics.map((metric) => {
              const Icon = metric.icon;
              return (
                <div key={metric.name} className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <Icon className="h-6 w-6 text-gray-400" />
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">{metric.name}</dt>
                          <dd className="flex items-baseline">
                            <div className="text-2xl font-semibold text-gray-900">{metric.value}</div>
                            <div
                              className={`ml-2 flex items-baseline text-sm font-semibold ${
                                metric.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                              }`}
                            >
                              {metric.change}
                            </div>
                          </dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Analysis Content */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Financial Trends */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Financial Trends</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Asset Growth</span>
                  <span className="text-sm font-medium text-green-600">+12.5%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Liability Growth</span>
                  <span className="text-sm font-medium text-green-600">+8.2%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Equity Growth</span>
                  <span className="text-sm font-medium text-green-600">+15.3%</span>
                </div>
              </div>
            </div>

            {/* Risk Assessment */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Risk Assessment</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Liquidity Risk</span>
                  <span className="text-sm font-medium text-green-600">Low</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Solvency Risk</span>
                  <span className="text-sm font-medium text-yellow-600">Medium</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Market Risk</span>
                  <span className="text-sm font-medium text-green-600">Low</span>
                </div>
              </div>
            </div>
          </div>

          {/* Detailed Analysis */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Detailed Analysis</h3>
            <div className="prose max-w-none">
              <p className="text-gray-700">
                Based on the analysis of the balance sheet data, {companies.find(c => c.id === selectedCompany)?.name} 
                shows strong financial performance with healthy growth in assets and equity. The current ratio of 1.85 
                indicates good short-term liquidity, while the debt-to-equity ratio of 0.72 suggests moderate leverage 
                levels that are well within acceptable ranges.
              </p>
              <p className="text-gray-700 mt-4">
                Key strengths include consistent asset growth, improving profitability ratios, and strong cash flow 
                generation. Areas for attention include monitoring debt levels and ensuring continued operational 
                efficiency improvements.
              </p>
            </div>
          </div>
        </>
      )}

      {!selectedCompany && (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No company selected</h3>
          <p className="mt-1 text-sm text-gray-500">
            Select a company above to view detailed financial analysis.
          </p>
        </div>
      )}
    </div>
  );
};

export default Analysis; 