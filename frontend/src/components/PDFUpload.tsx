import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext.tsx';
import api from '../services/api.ts';

interface UploadResponse {
  message: string;
  result: {
    success: boolean;
    total_chunks: number;
    vertical_results: Record<string, {
      success: boolean;
      chunks_stored: number;
      error?: string;
    }>;
    validation: {
      is_valid: boolean;
      errors: string[];
    };
    error?: string;
  };
}

const PDFUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
      setResult(null);
    } else {
      setError('Please select a valid PDF file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/pdf/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  // Helper function to get successful verticals
  const getSuccessfulVerticals = () => {
    if (!result?.result?.vertical_results) return [];
    return Object.entries(result.result.vertical_results)
      .filter(([_, data]) => data.success)
      .map(([vertical, _]) => vertical);
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex items-center mb-4">
        <FileText className="h-6 w-6 text-blue-600 mr-2" />
        <h2 className="text-lg font-medium text-gray-900">Upload Balance Sheet PDF</h2>
      </div>

      <div className="space-y-4">
        {/* File Input */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          <div className="mt-4">
            <label htmlFor="pdf-upload" className="cursor-pointer">
              <span className="text-blue-600 hover:text-blue-500 font-medium">
                Choose a PDF file
              </span>
              <span className="text-gray-500"> or drag and drop</span>
            </label>
            <input
              id="pdf-upload"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            PDF files only, max 50MB
          </p>
        </div>

        {/* File Info */}
        {file && (
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <FileText className="h-5 w-5 text-gray-400 mr-2" />
              <span className="text-sm font-medium text-gray-900">{file.name}</span>
            </div>
            <span className="text-sm text-gray-500">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </span>
          </div>
        )}

        {/* Upload Button */}
        {file && (
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? 'Processing...' : 'Upload and Process PDF'}
          </button>
        )}

        {/* Error Message */}
        {error && (
          <div className="flex items-center p-3 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
            <span className="text-sm text-red-600">{error}</span>
          </div>
        )}

        {/* Success Message */}
        {result && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center mb-2">
              <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
              <span className="text-sm font-medium text-green-800">Upload Successful!</span>
            </div>
            <div className="text-sm text-green-700">
              <p><strong>Verticals processed:</strong> {getSuccessfulVerticals().join(', ') || 'None'}</p>
              <p><strong>Total chunks:</strong> {result.result?.total_chunks || 0}</p>
              <p className="mt-2">{result.message}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PDFUpload; 