import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Building,
  BarChart3,
  MessageSquare,
  FileText,
  Users,
} from 'lucide-react';
import { companyAPI } from '../services/api.ts';
import { useAuth } from '../contexts/AuthContext.tsx';
import PDFUpload from '../components/PDFUpload.tsx';
import UploadedFiles from '../components/UploadedFiles.tsx';
import ActiveFiles from '../components/ActiveFiles.tsx';
import RecentActivity from '../components/RecentActivity.tsx';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { data: companies, isLoading, error } = useQuery('companies', companyAPI.getCompanies, {
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
    onError: (error) => {
      console.error('Companies API error:', error);
    },
    onSuccess: (data) => {
      console.log('Companies data received:', data);
    }
  });

  const getCompaniesCount = () => {
    if (isLoading) return 'Loading...';
    if (error) return 'Error';
    return companies?.length || 0;
  };

  const stats = [
    {
      name: 'Total Companies',
      value: getCompaniesCount(),
      icon: Building,
      change: isLoading ? 'Loading companies...' : error ? 'Failed to load companies' : '',
      changeType: 'neutral',
    },
    {
      name: 'Your Role',
      value: user?.role?.replace('_', ' ') || 'User',
      icon: Users,
      change: '',
      changeType: 'neutral',
    },
  ];

  const quickActions = [
    {
      name: 'AI Chat',
      description: 'Ask questions about financial data',
      href: '/chat',
      icon: MessageSquare,
      color: 'bg-green-500',
    },
    {
      name: 'PDF Upload',
      description: 'Upload balance sheet PDFs for analysis',
      href: '#',
      icon: FileText,
      color: 'bg-blue-500',
    },
  ];

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
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome to your Balance Sheet Analyst dashboard. Get insights into your company's financial performance.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Icon className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">{stat.name}</dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900">{stat.value}</div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.name}
                to={action.href}
                className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg shadow hover:shadow-md transition-shadow"
              >
                <div>
                  <span className={`rounded-lg inline-flex p-3 ${action.color} text-white ring-4 ring-white`}>
                    <Icon className="h-6 w-6" />
                  </span>
                </div>
                <div className="mt-8">
                  <h3 className="text-lg font-medium">
                    <span className="absolute inset-0" aria-hidden="true" />
                    {action.name}
                  </h3>
                  <p className="mt-2 text-sm text-gray-500">{action.description}</p>
                </div>
                <span
                  className="pointer-events-none absolute top-6 right-6 text-gray-300 group-hover:text-gray-400"
                  aria-hidden="true"
                >
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20 4h1a1 1 0 00-1-1v1zm-1 12a1 1 0 102 0h-2zM8 3a1 1 0 000 2V3zM3.293 19.293a1 1 0 101.414 1.414l-1.414-1.414zM19 4v12h2V4h-2zm1-1H8v2h12V3zm-.707.293l-16 16 1.414 1.414 16-16-1.414-1.414z" />
                  </svg>
                </span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* PDF Upload Section */}
      <div>
        <h2 className="text-lg font-medium text-gray-900 mb-4">Upload Balance Sheet</h2>
        <PDFUpload />
      </div>

      {/* Active Files Section */}
      <div>
        <h2 className="text-lg font-medium text-gray-900 mb-4">Active Files</h2>
        <ActiveFiles />
      </div>

      {/* Uploaded Files Section */}
      <div>
        <h2 className="text-lg font-medium text-gray-900 mb-4">Uploaded Files</h2>
        <UploadedFiles />
      </div>

      {/* Recent Activity */}
      <RecentActivity />
    </div>
  );
};

export default Dashboard; 