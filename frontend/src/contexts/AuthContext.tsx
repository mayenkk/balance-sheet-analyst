import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  register: (userData: RegisterData) => Promise<boolean>;
}

interface RegisterData {
  email: string;
  username: string;
  full_name: string;
  password: string;
  role?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check if user is already logged in on app start
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const userData = await authAPI.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('Auth check failed:', error);
          localStorage.removeItem('access_token');
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      const response = await authAPI.login(username, password);
      
      localStorage.setItem('access_token', response.access_token);
      setUser(response.user);
      
      toast.success('Login successful!');
      return true;
    } catch (error: any) {
      console.error('Login failed:', error);
      toast.error(error.response?.data?.detail || 'Login failed');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      setUser(null);
      toast.success('Logged out successfully');
    }
  };

  const register = async (userData: RegisterData): Promise<boolean> => {
    try {
      setLoading(true);
      const response = await authAPI.register(userData);
      
      toast.success('Registration successful! Please log in.');
      return true;
    } catch (error: any) {
      console.error('Registration failed:', error);
      toast.error(error.response?.data?.detail || 'Registration failed');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    register,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 