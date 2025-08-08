import axios, { AxiosInstance, AxiosResponse } from 'axios';

// Create axios instance
const getBaseURL = () => {
  // In development, explicitly point to backend if proxy isn't working
  // Check if we're running on localhost:3000 (React dev server)
  if (window.location.hostname === 'localhost' && window.location.port === '3000') {
    return 'http://localhost:8000/api/v1';
  }
  // In production or if proxy is working, use relative URL
  return '/api/v1';
};

const api: AxiosInstance = axios.create({
  baseURL: getBaseURL(),
  timeout: 60000, // Increased to 60 seconds to match backend timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  register: async (userData: {
    email: string;
    username: string;
    full_name: string;
    password: string;
    role?: string;
  }) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },
};

// Chat API
export const chatAPI = {
  createSession: async (sessionData: {
    title: string;
    session_type?: string;
  }) => {
    const response = await api.post('/chat/sessions', sessionData);
    return response.data;
  },

  getSessions: async () => {
    const response = await api.get('/chat/sessions');
    return response.data;
  },

  getMessages: async (sessionId: number) => {
    const response = await api.get(`/chat/sessions/${sessionId}/messages`);
    return response.data;
  },

  sendMessage: async (sessionId: number, content: string) => {
    const response = await api.post(`/chat/sessions/${sessionId}/messages`, {
      content,
    }, {
      timeout: 90000, // 90 second timeout for AI analysis
    });
    return response.data;
  },

  analyzeCompany: async (companyId: number, query: string) => {
    const response = await api.post('/chat/analyze', {
      company_id: companyId,
      query,
    });
    return response.data;
  },

  closeSession: async (sessionId: number) => {
    const response = await api.post(`/chat/sessions/${sessionId}/close`);
    return response.data;
  },
};

// Company API
export const companyAPI = {
  getCompanies: async () => {
    const response = await api.get('/companies/');
    return response.data;
  },

  getCompany: async (companyId: number) => {
    const response = await api.get(`/companies/${companyId}`);
    return response.data;
  },

  getBalanceSheets: async (companyId: number) => {
    const response = await api.get(`/companies/${companyId}/balance-sheets`);
    return response.data;
  },

  getAnalytics: async (companyId: number) => {
    const response = await api.get(`/companies/${companyId}/analytics`);
    return response.data;
  },
};

// Reports API
export const reportsAPI = {
  getReports: async (companyId?: number) => {
    const params = companyId ? { company_id: companyId } : {};
    const response = await api.get('/reports', { params });
    return response.data;
  },

  createReport: async (reportData: {
    title: string;
    company_id: number;
    report_type: string;
    period_start?: string;
    period_end?: string;
  }) => {
    const response = await api.post('/reports', reportData);
    return response.data;
  },

  getReport: async (reportId: number) => {
    const response = await api.get(`/reports/${reportId}`);
    return response.data;
  },

  updateReport: async (reportId: number, reportData: any) => {
    const response = await api.put(`/reports/${reportId}`, reportData);
    return response.data;
  },

  deleteReport: async (reportId: number) => {
    const response = await api.delete(`/reports/${reportId}`);
    return response.data;
  },
};

// Analytics API
export const analyticsAPI = {
  getMetrics: async (companyId: number) => {
    const response = await api.get(`/analytics/${companyId}/metrics`);
    return response.data;
  },

  getTrends: async (companyId: number, period: string = '1y') => {
    const response = await api.get(`/analytics/${companyId}/trends`, {
      params: { period },
    });
    return response.data;
  },

  getInsights: async (companyId: number) => {
    const response = await api.get(`/analytics/${companyId}/insights`);
    return response.data;
  },

  compareCompanies: async (companyIds: number[]) => {
    const response = await api.post('/analytics/compare', {
      company_ids: companyIds,
    });
    return response.data;
  },

  getForecast: async (companyId: number, periods: number = 4) => {
    const response = await api.get(`/analytics/${companyId}/forecast`, {
      params: { periods },
    });
    return response.data;
  },
};

// PDF API
export const pdfAPI = {
  processPDF: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/pdf/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getUploadedFiles: async () => {
    const response = await api.get('/pdf/uploaded-files');
    return response.data;
  },

  getAllFiles: async () => {
    const response = await api.get('/pdf/all-files');
    return response.data;
  },

  getUploadedFile: async (fileId: number) => {
    const response = await api.get(`/pdf/uploaded-files/${fileId}`);
    return response.data;
  },

  getVectorStoreHealth: async () => {
    const response = await api.get('/pdf/health');
    return response.data;
  },
};

// Activities API
export const activitiesAPI = {
  getRecentActivities: async () => {
    const response = await api.get('/activities/recent');
    return response.data;
  },

  getUserActivities: async (userId: number) => {
    const response = await api.get(`/activities/user/${userId}`);
    return response.data;
  },

  getAllActivities: async () => {
    const response = await api.get('/activities/all');
    return response.data;
  },
};

// Analysis API
export const analysisAPI = {
  getAvailableFiles: async () => {
    const response = await api.get('/analysis/available-files');
    return response.data;
  },

  generateFinancialAnalysis: async (fileId: number) => {
    const response = await api.post('/analysis/financial-analysis', { file_id: fileId });
    return response.data;
  },
};

// Export the api instance
export default api; 