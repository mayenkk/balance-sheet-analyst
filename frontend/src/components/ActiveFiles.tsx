import React from 'react';
import { useQuery } from 'react-query';
import { FileText, Download, Eye, CheckCircle, XCircle, Clock, AlertCircle, Users } from 'lucide-react';
import { pdfAPI } from '../services/api.ts';

interface UploadedFile {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  content_type: string;
  is_processed: boolean;
  processing_status: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
  user?: {
    id: number;
    username: string;
    full_name: string;
    email: string;
  };
}

const ActiveFiles: React.FC = () => {
  const { data: allFiles, isLoading, refetch } = useQuery('all-files', pdfAPI.getAllFiles);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'processing':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleView = async (fileId: number, filename: string) => {
    try {
      const blob = await pdfAPI.viewPDF(fileId);
      const url = window.URL.createObjectURL(blob);
      const newWindow = window.open();
      if (newWindow) {
        newWindow.document.title = filename;
        const iframe = newWindow.document.createElement('iframe');
        iframe.src = url;
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = '0';
        newWindow.document.body.style.margin = '0';
        newWindow.document.body.appendChild(iframe);
      } else {
        window.location.href = url;
      }
    } catch (e) {
      console.error('Failed to view PDF', e);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!allFiles || allFiles.files.length === 0) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Active Files</h2>
        <div className="text-center py-8">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No files uploaded</h3>
          <p className="mt-1 text-sm text-gray-500">
            No PDF files have been uploaded to the system yet.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-medium text-gray-900">Active Files</h2>
        <button
          onClick={() => refetch()}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Refresh
        </button>
      </div>
      
      <div className="space-y-4">
        {allFiles.files.map((file: UploadedFile) => (
          <div key={file.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  {getStatusIcon(file.processing_status)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {file.original_filename}
                  </p>
                  <div className="flex items-center space-x-4 mt-1">
                    <span className="text-xs text-gray-500">
                      {formatFileSize(file.file_size)}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(file.created_at).toLocaleDateString()}
                    </span>
                    {file.user && (
                      <div className="flex items-center space-x-1">
                        <Users className="h-3 w-3 text-gray-400" />
                        <span className="text-xs text-gray-500">
                          {file.user.full_name || file.user.username}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(file.processing_status)}`}>
                  {file.processing_status}
                </span>
              </div>
            </div>
            
            {file.error_message && (
              <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded-md">
                <p className="text-xs text-red-800">
                  <strong>Error:</strong> {file.error_message}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ActiveFiles; 