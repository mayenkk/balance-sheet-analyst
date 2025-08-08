import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from 'react-query';
import { toast } from 'react-hot-toast';
import { BarChart3, TrendingUp, TrendingDown, DollarSign, PieChart, Activity } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext.tsx';
import { analysisAPI } from '../services/api.ts';

interface File {
  id: number;
  name: string;
  uploaded_at: string;
  file_size: number;
}

interface FinancialData {
  sales?: Record<string, { value: number; unit: string }>;
  growth_rate?: Record<string, { value: number; unit: string }>;
  total_assets?: Record<string, { value: number; unit: string }>;
  total_liabilities?: Record<string, { value: number; unit: string }>;
  net_worth?: Record<string, { value: number; unit: string }>;
  profit_margin?: Record<string, { value: number; unit: string }>;
  debt_to_equity?: Record<string, { value: number; unit: string }>;
  extracted_companies: string[];
  accessible_companies: string[];
  currency: string;
  data_quality: string;
}

interface Insight {
  type: 'positive' | 'warning' | 'error';
  title: string;
  description: string;
}

interface AnalysisResult {
  success: boolean;
  financial_data: FinancialData;
  plots: Record<string, string>; // Base64 encoded images
  insights: Insight[];
  file_name: string;
  error?: string;
}

const FinancialAnalysis: React.FC = () => {
  const { user } = useAuth();
  const [selectedFile, setSelectedFile] = useState<number | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  // Fetch available files
  const { data: files, isLoading: filesLoading } = useQuery({
    queryKey: ['available-files'],
    queryFn: async () => {
      const data = await analysisAPI.getAvailableFiles();
      console.log('Available files response:', data);
      return data;
    },
  });

  // Generate analysis mutation
  const analysisMutation = useMutation({
    mutationFn: async (fileId: number) => {
      return await analysisAPI.generateFinancialAnalysis(fileId);
    },
    onSuccess: (data: AnalysisResult) => {
      setAnalysisResult(data);
      toast.success('Financial analysis completed successfully!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to generate analysis');
    },
  });

  const handleGenerateAnalysis = () => {
    if (!selectedFile) {
      toast.error('Please select a file first');
      return;
    }
    
    const loadingToast = toast.loading('Generating financial analysis... This may take up to 60 seconds.');
    analysisMutation.mutate(selectedFile, {
      onSuccess: () => {
        toast.dismiss(loadingToast);
      },
      onError: () => {
        toast.dismiss(loadingToast);
      }
    });
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'positive':
        return <TrendingUp className="w-5 h-5 text-green-500" />;
      case 'warning':
        return <TrendingDown className="w-5 h-5 text-yellow-500" />;
      case 'error':
        return <Activity className="w-5 h-5 text-red-500" />;
      default:
        return <Activity className="w-5 h-5 text-gray-500" />;
    }
  };

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'positive':
        return 'border-green-200 bg-green-50';
      case 'warning':
        return 'border-yellow-200 bg-yellow-50';
      case 'error':
        return 'border-red-200 bg-red-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <BarChart3 className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">Financial Analysis</h1>
          </div>
          <p className="text-gray-600">
            Generate comprehensive financial plots and insights from your uploaded PDF balance sheets.
            {user?.role === 'ceo' && ' You can only analyze files from your company.'}
            {user?.role === 'analyst' && ' You have access to all uploaded files.'}
            {user?.role === 'group_ceo' && ' You have access to all uploaded files across all companies.'}
          </p>
        </div>

        {/* File Selection Panel */}
        <div className="mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Select PDF File</h2>
              
              {filesLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : (() => {
                console.log('Files data:', files);
                return files?.files?.length > 0;
              })() ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {files.files.map((file: File) => (
                      <div
                        key={file.id}
                        className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                          selectedFile === file.id
                            ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                            : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
                        }`}
                        onClick={() => setSelectedFile(file.id)}
                      >
                        <div className="font-medium text-gray-900 truncate">{file.name}</div>
                        <div className="text-sm text-gray-500 mt-1">
                          {new Date(file.uploaded_at).toLocaleDateString()} • 
                          {(file.file_size / 1024 / 1024).toFixed(1)} MB
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="flex justify-center">
                    <button
                      onClick={handleGenerateAnalysis}
                      disabled={!selectedFile || analysisMutation.isLoading}
                      className="px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {analysisMutation.isLoading ? 'Generating Analysis...' : 'Generate Financial Analysis'}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <PieChart className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p>No processed PDF files available for analysis.</p>
                  <p className="text-sm mt-2">Upload and process a PDF first.</p>
                </div>
              )}
          </div>
        </div>

        {/* Analysis Results */}
        <div>
            {analysisResult ? (
              <div className="space-y-6">
                {/* File Info */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-2">
                    Analysis Results: {analysisResult.file_name}
                  </h2>
                  <div className="text-sm text-gray-600">
                    Data Quality: <span className="font-medium">{analysisResult.financial_data.data_quality}</span> • 
                    Currency: <span className="font-medium">{analysisResult.financial_data.currency}</span>
                  </div>
                </div>

                {/* Insights */}
                {analysisResult.insights.length > 0 && (
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h3>
                    <div className="space-y-3">
                      {analysisResult.insights.map((insight, index) => (
                        <div
                          key={index}
                          className={`p-4 rounded-lg border ${getInsightColor(insight.type)}`}
                        >
                          <div className="flex items-start space-x-3">
                            {getInsightIcon(insight.type)}
                            <div>
                              <h4 className="font-medium text-gray-900">{insight.title}</h4>
                              <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Plots - Full Width */}
                {Object.keys(analysisResult.plots).length > 0 && (
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">Financial Analysis Charts</h3>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                      {Object.entries(analysisResult.plots).map(([plotType, imageData]) => (
                        <div key={plotType} className="space-y-4">
                          <h4 className="text-xl font-semibold text-gray-900 capitalize text-center border-b-2 border-blue-100 pb-2">
                            {plotType.replace(/_/g, ' ')}
                          </h4>
                          <div className="border-2 border-gray-300 rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition-all duration-300 bg-white">
                            <img
                              src={`data:image/png;base64,${imageData}`}
                              alt={plotType}
                              className="w-full h-auto min-h-[500px] object-contain"
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Financial Data Summary */}
                {analysisResult.financial_data && (
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial Summary</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {analysisResult.financial_data.sales && (
                        <div className="p-4 bg-blue-50 rounded-lg">
                          <div className="flex items-center space-x-2 mb-2">
                            <DollarSign className="w-5 h-5 text-blue-600" />
                            <h4 className="font-medium text-gray-900">Latest Sales</h4>
                          </div>
                          <p className="text-2xl font-bold text-blue-600">
                            {Object.values(analysisResult.financial_data.sales)[0]?.value.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-600">
                            {analysisResult.financial_data.currency}{analysisResult.financial_data.currency === 'INR' ? ' (In Crores)' : ''}
                          </p>
                        </div>
                      )}
                      
                      {analysisResult.financial_data.total_assets && (
                        <div className="p-4 bg-green-50 rounded-lg">
                          <div className="flex items-center space-x-2 mb-2">
                            <TrendingUp className="w-5 h-5 text-green-600" />
                            <h4 className="font-medium text-gray-900">Total Assets</h4>
                          </div>
                          <p className="text-2xl font-bold text-green-600">
                            {Object.values(analysisResult.financial_data.total_assets)[0]?.value.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-600">
                            {analysisResult.financial_data.currency}{analysisResult.financial_data.currency === 'INR' ? ' (In Crores)' : ''}
                          </p>
                        </div>
                      )}
                      
                      {analysisResult.financial_data.profit_margin && (
                        <div className="p-4 bg-purple-50 rounded-lg">
                          <div className="flex items-center space-x-2 mb-2">
                            <BarChart3 className="w-5 h-5 text-purple-600" />
                            <h4 className="font-medium text-gray-900">Profit Margin</h4>
                          </div>
                          <p className="text-2xl font-bold text-purple-600">
                            {Object.values(analysisResult.financial_data.profit_margin)[0]?.value.toFixed(1)}%
                          </p>
                          <p className="text-sm text-gray-600">Latest Year</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis Yet</h3>
                <p className="text-gray-600">
                  Select a PDF file and generate financial analysis to see plots and insights.
                </p>
              </div>
            )}
        </div>
      </div>
    </div>
  );
};

export default FinancialAnalysis; 