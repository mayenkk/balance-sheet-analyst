import React from 'react';
import { useQuery } from 'react-query';
import { 
  BarChart3, 
  MessageSquare, 
  FileText, 
  TrendingUp, 
  TrendingDown,
  Clock,
  User,
  Building
} from 'lucide-react';
import { activitiesAPI } from '../services/api.ts';
import { useAuth } from '../contexts/AuthContext.tsx';

interface Activity {
  id: number;
  activity_type: string;
  title: string;
  description?: string;
  resource_type?: string;
  resource_id?: number;
  activity_metadata?: any;
  created_at: string;
  user?: {
    id: number;
    username: string;
    full_name: string;
    email: string;
  };
}

const RecentActivity: React.FC = () => {
  const { user } = useAuth();
  const { data: activities, isLoading } = useQuery('recent-activities', activitiesAPI.getRecentActivities);

  const getActivityIcon = (activityType: string) => {
    switch (activityType) {
      case 'pdf_upload':
        return <FileText className="h-5 w-5 text-blue-500" />;
      case 'chat_session':
        return <MessageSquare className="h-5 w-5 text-green-500" />;
      case 'chat_message':
        return <BarChart3 className="h-5 w-5 text-purple-500" />;
      case 'analysis':
        return <TrendingUp className="h-5 w-5 text-orange-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const getActivityColor = (activityType: string) => {
    switch (activityType) {
      case 'pdf_upload':
        return 'bg-blue-500';
      case 'chat_session':
        return 'bg-green-500';
      case 'chat_message':
        return 'bg-purple-500';
      case 'analysis':
        return 'bg-orange-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInDays < 7) return `${diffInDays}d ago`;
    return date.toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!activities || activities.activities.length === 0) {
    return (
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Activity</h3>
          <div className="mt-5">
            <div className="text-center py-8">
              <Clock className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No recent activity</h3>
              <p className="mt-1 text-sm text-gray-500">
                Start using the platform to see your activity here.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Activity</h3>
          {user?.role === 'group_ceo' && (
            <span className="text-xs text-gray-500">All Platform Activity</span>
          )}
        </div>
        <div className="mt-5">
          <div className="flow-root">
            <ul className="-mb-8">
              {activities.activities.map((activity: Activity, index: number) => (
                <li key={activity.id}>
                  <div className="relative pb-8">
                    {index < activities.activities.length - 1 && (
                      <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                    )}
                    <div className="relative flex space-x-3">
                      <div>
                        <span className={`h-8 w-8 rounded-full ${getActivityColor(activity.activity_type)} flex items-center justify-center ring-8 ring-white`}>
                          {getActivityIcon(activity.activity_type)}
                        </span>
                      </div>
                      <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                        <div>
                          <p className="text-sm text-gray-500">
                            {activity.title}
                            {activity.user && user?.role === 'group_ceo' && (
                              <span className="font-medium text-gray-900"> by {activity.user.full_name || activity.user.username}</span>
                            )}
                          </p>
                          {activity.description && (
                            <p className="text-xs text-gray-400 mt-1">
                              {activity.description}
                            </p>
                          )}
                        </div>
                        <div className="text-right text-sm whitespace-nowrap text-gray-500">
                          <time dateTime={activity.created_at}>
                            {formatTimeAgo(activity.created_at)}
                          </time>
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecentActivity; 