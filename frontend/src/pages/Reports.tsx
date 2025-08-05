import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { FileText, Download, Eye, Plus, Calendar, Building } from 'lucide-react';
import { reportsAPI } from '../services/api';

const Reports: React.FC = () => {
  const [selectedReportType, setSelectedReportType] = useState<string>('all');

  // Mock reports data
  const mockReports = [
    {
      id: 1,
      title: 'Q3 2023 Financial Analysis - Reliance Industries',
      company_name: 'Reliance Industries',
      report_type: 'quarterly',
      period_start: '2023-07-01',
      period_end: '2023-09-30',
      status: 'final',
      created_at: '2023-10-15',
      file_size: '2.4 MB',
    },
    {
      id: 2,
      title: 'Annual Performance Review - JIO Platforms',
      company_name: 'JIO Platforms',
      report_type: 'annual',
      period_start: '2023-01-01',
      period_end: '2023-12-31',
      status: 'draft',
      created_at: '2023-12-20',
      file_size: '3.1 MB',
    },
    {
      id: 3,
      title: 'Balance Sheet Analysis - Reliance Retail',
      company_name: 'Reliance Retail',
      report_type: 'custom',
      period_start: '2023-06-01',
      period_end: '2023-11-30',
      status: 'final',
      created_at: '2023-12-01',
      file_size: '1.8 MB',
    },
  ];

  const reportTypes = [
    { id: 'all', name: 'All Reports' },
    { id: 'quarterly', name: 'Quarterly' },
    { id: 'annual', name: 'Annual' },
    { id: 'custom', name: 'Custom' },
  ];

  const filteredReports = selectedReportType === 'all' 
    ? mockReports 
    : mockReports.filter(report => report.report_type === selectedReportType);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'final':
        return 'bg-green-100 text-green-800';
      case 'draft':
        return 'bg-yellow-100 text-yellow-800';
      case 'archived':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
          <p className="mt-1 text-sm text-gray-500">
            View and manage financial analysis reports and insights.
          </p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Generate Report
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Filter by:</span>
          {reportTypes.map((type) => (
            <button
              key={type.id}
              onClick={() => setSelectedReportType(type.id)}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                selectedReportType === type.id
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              }`}
            >
              {type.name}
            </button>
          ))}
        </div>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
        {filteredReports.map((report) => (
          <div key={report.id} className="bg-white shadow rounded-lg overflow-hidden">
            <div className="p-6">
              {/* Report Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="h-10 w-10 bg-blue-600 rounded-lg flex items-center justify-center">
                    <FileText className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                      {report.title}
                    </h3>
                    <p className="text-sm text-gray-500">{report.company_name}</p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                  {report.status}
                </span>
              </div>

              {/* Report Details */}
              <div className="space-y-3 mb-6">
                <div className="flex items-center text-sm text-gray-500">
                  <Calendar className="h-4 w-4 mr-2" />
                  {new Date(report.period_start).toLocaleDateString()} - {new Date(report.period_end).toLocaleDateString()}
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <Building className="h-4 w-4 mr-2" />
                  {report.report_type.charAt(0).toUpperCase() + report.report_type.slice(1)} Report
                </div>
                <div className="text-sm text-gray-500">
                  Generated: {new Date(report.created_at).toLocaleDateString()}
                </div>
                <div className="text-sm text-gray-500">
                  Size: {report.file_size}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3">
                <button className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors flex items-center justify-center">
                  <Eye className="h-4 w-4 mr-2" />
                  View
                </button>
                <button className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-300 transition-colors flex items-center justify-center">
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Report Summary</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{mockReports.length}</div>
            <div className="text-sm text-gray-500">Total Reports</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {mockReports.filter(r => r.status === 'final').length}
            </div>
            <div className="text-sm text-gray-500">Final Reports</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {mockReports.filter(r => r.status === 'draft').length}
            </div>
            <div className="text-sm text-gray-500">Draft Reports</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {mockReports.filter(r => r.report_type === 'quarterly').length}
            </div>
            <div className="text-sm text-gray-500">Quarterly Reports</div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {mockReports.slice(0, 3).map((report) => (
            <div key={report.id} className="flex items-center space-x-4">
              <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                <FileText className="h-4 w-4 text-blue-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{report.title}</p>
                <p className="text-sm text-gray-500">
                  Generated {new Date(report.created_at).toLocaleDateString()}
                </p>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                {report.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Reports; 