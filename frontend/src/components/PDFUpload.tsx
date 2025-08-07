import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { useMutation, useQueryClient } from 'react-query';
import { useAuth } from '../contexts/AuthContext.tsx';
import { pdfAPI } from '../services/api.ts';
import toast from 'react-hot-toast';

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
  uploaded_file_id?: number;
}

const PDFUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const uploadMutation = useMutation(
    (file: File) => pdfAPI.processPDF(file),
    {
      onSuccess: (data: UploadResponse) => {
        toast.success('PDF uploaded and processed successfully!');
        // Invalidate uploaded files query to refresh the list
        queryClient.invalidateQueries('uploaded-files');
        setFile(null);
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Upload failed');
      },
    }
  );

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
    } else {
      toast.error('Please select a valid PDF file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    uploadMutation.mutate(file);
  };

  // Helper function to get successful verticals
  const getSuccessfulVerticals = () => {
    if (!uploadMutation.data?.result?.vertical_results) return [];
    return Object.entries(uploadMutation.data.result.vertical_results)
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
            disabled={uploadMutation.isLoading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploadMutation.isLoading ? 'Processing...' : 'Upload and Process PDF'}
          </button>
        )}

        {/* Error Message */}
        {uploadMutation.isError && (
          <div className="flex items-center p-3 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
            <span className="text-sm text-red-600">{uploadMutation.error.response?.data?.detail || 'Upload failed'}</span>
          </div>
        )}

        {/* Success Message */}
        {uploadMutation.isSuccess && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center mb-2">
              <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
              <span className="text-sm font-medium text-green-800">Upload Successful!</span>
            </div>
            <div className="text-sm text-green-700">
              <p><strong>Verticals processed:</strong> {getSuccessfulVerticals().join(', ') || 'None'}</p>
              <p><strong>Total chunks:</strong> {uploadMutation.data?.result?.total_chunks || 0}</p>
              <p className="mt-2">{uploadMutation.data?.message}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PDFUpload; 