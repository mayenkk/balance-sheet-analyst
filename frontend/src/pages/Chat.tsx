import React, { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Send, MessageSquare, Plus, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { chatAPI } from '../services/api.ts';
import { useAuth } from '../contexts/AuthContext.tsx';
import toast from 'react-hot-toast';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  metadata?: any;
}

interface ChatSession {
  id: number;
  title: string;
  session_type: string;
  is_active: boolean;
  created_at: string;
}

const Chat: React.FC = () => {
  const [selectedSession, setSelectedSession] = useState<ChatSession | null>(null);
  const [message, setMessage] = useState('');
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  const [newSessionTitle, setNewSessionTitle] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();
  const { user } = useAuth();

  const { data: sessions, isLoading: sessionsLoading } = useQuery(
    ['chat-sessions'],
    () => chatAPI.getSessions(),
    { enabled: true }
  );

  const { data: messages, isLoading: messagesLoading } = useQuery(
    ['chat-messages', selectedSession?.id],
    () => chatAPI.getMessages(selectedSession!.id),
    { enabled: !!selectedSession }
  );

  const sendMessageMutation = useMutation(
    (content: string) => chatAPI.sendMessage(selectedSession!.id, content),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['chat-messages', selectedSession?.id]);
        setMessage('');
        toast.success('AI analysis completed!');
      },
      onError: (error: any) => {
        console.error('Send message error:', error);
        const errorMessage = error.response?.data?.detail || 
                           error.message || 
                           'AI analysis is taking longer than expected. Please try again.';
        toast.error(errorMessage);
        // Still invalidate to show any partial response
        queryClient.invalidateQueries(['chat-messages', selectedSession?.id]);
      },
      retry: 0, // Don't retry automatically - let user retry manually
      retryDelay: 1000,
    }
  );

  const createSessionMutation = useMutation(
    (sessionData: { title: string; session_type: string }) =>
      chatAPI.createSession(sessionData),
    {
      onSuccess: (newSession) => {
        queryClient.invalidateQueries(['chat-sessions']);
        setSelectedSession(newSession);
        setIsCreatingSession(false);
        setNewSessionTitle('');
        toast.success('New chat session created!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create session');
      },
    }
  );

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || !selectedSession) return;

    // Show loading toast with longer timeout message
    const loadingToast = toast.loading('AI is analyzing your question... This may take up to 90 seconds for complex queries.');
    
    sendMessageMutation.mutate(message, {
      onSuccess: () => {
        toast.dismiss(loadingToast);
        toast.success('AI analysis completed!');
      },
      onError: () => {
        toast.dismiss(loadingToast);
      }
    });
  };

  const handleCreateSession = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSessionTitle.trim()) return;

    // Only send required fields - backend handles company access based on user role
    const sessionData = {
      title: newSessionTitle,
      session_type: "analysis"
    };

    createSessionMutation.mutate(sessionData);
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Chat Sessions</h2>
              <button
                onClick={() => setIsCreatingSession(true)}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Create Session Modal */}
          {isCreatingSession && (
            <div className="p-4 border-b border-gray-200 bg-gray-50">
              <div className="mb-3 p-2 bg-blue-50 border border-blue-200 rounded-md">
                <p className="text-sm text-blue-800">
                  <strong>Data Access:</strong> You have access to {
                    user?.role === 'ceo' ? 'your assigned company data' :
                    user?.role === 'group_ceo' ? 'all group companies data' :
                    user?.role === 'analyst' ? 'all companies data' :
                    user?.role === 'top_management' ? 'all companies data' :
                    'available data'
                  }
                </p>
              </div>
              <form onSubmit={handleCreateSession} className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Session Title</label>
                  <input
                    type="text"
                    value={newSessionTitle}
                    onChange={(e) => setNewSessionTitle(e.target.value)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="Enter session title"
                    required
                  />
                </div>
                <div className="flex space-x-2">
                  <button
                    type="submit"
                    disabled={createSessionMutation.isLoading}
                    className="flex-1 bg-blue-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
                  >
                    {createSessionMutation.isLoading ? 'Creating...' : 'Create'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setIsCreatingSession(false);
                      setNewSessionTitle('');
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Sessions List */}
          <div className="flex-1 overflow-y-auto">
            {sessionsLoading ? (
              <div className="p-4 text-center text-gray-500">Loading sessions...</div>
            ) : sessions?.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No chat sessions yet. Create one to get started!
              </div>
            ) : (
              <div className="p-2">
                {sessions?.map((session: ChatSession) => (
                  <button
                    key={session.id}
                    onClick={() => setSelectedSession(session)}
                    className={`w-full text-left p-3 rounded-lg mb-2 transition-colors ${
                      selectedSession?.id === session.id
                        ? 'bg-blue-100 text-blue-900'
                        : 'hover:bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="font-medium truncate">{session.title}</div>
                    <div className="text-sm text-gray-500">
                      {new Date(session.created_at).toLocaleDateString()}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col bg-gray-50">
          {selectedSession ? (
            <>
              {/* Chat Header */}
              <div className="bg-white border-b border-gray-200 px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{selectedSession.title}</h3>
                    <div className="flex items-center space-x-4">
                      <p className="text-sm text-gray-500">
                        Created {new Date(selectedSession.created_at).toLocaleDateString()}
                      </p>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {user?.role === 'ceo' ? 'Company CEO' :
                         user?.role === 'group_ceo' ? 'Group CEO' :
                         user?.role === 'analyst' ? 'Analyst' :
                         user?.role === 'top_management' ? 'Top Management' :
                         user?.role?.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6">
                {messagesLoading ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {messages?.map((msg: Message) => (
                      <div
                        key={msg.id}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                            msg.role === 'user'
                              ? 'bg-blue-600 text-white'
                              : 'bg-white text-gray-900 border border-gray-200'
                          }`}
                        >
                          <ReactMarkdown 
                            remarkPlugins={[remarkGfm]}
                            className="prose prose-sm max-w-none"
                            components={{
                              h1: ({node, ...props}) => <h1 className="text-lg font-bold mb-2" {...props} />,
                              h2: ({node, ...props}) => <h2 className="text-base font-bold mb-2" {...props} />,
                              h3: ({node, ...props}) => <h3 className="text-sm font-bold mb-1" {...props} />,
                              p: ({node, ...props}) => <p className="mb-2" {...props} />,
                              ul: ({node, ...props}) => <ul className="list-disc list-inside mb-2 space-y-1" {...props} />,
                              ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-2 space-y-1" {...props} />,
                              li: ({node, ...props}) => <li className="text-sm" {...props} />,
                              strong: ({node, ...props}) => <strong className="font-semibold" {...props} />,
                              em: ({node, ...props}) => <em className="italic" {...props} />,
                              blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-gray-300 pl-4 italic text-gray-600" {...props} />,
                              code: ({node, inline, ...props}) => 
                                inline ? 
                                  <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono" {...props} /> :
                                  <code className="block bg-gray-100 p-2 rounded text-sm font-mono overflow-x-auto" {...props} />,
                            }}
                          >
                            {msg.content}
                          </ReactMarkdown>
                          {msg.metadata && msg.role === 'assistant' && (
                            <div className="mt-2 pt-2 border-t border-gray-200">
                              {msg.metadata.insights && (
                                <div className="text-sm">
                                  <strong>Key Insights:</strong>
                                  <ul className="mt-1 space-y-1">
                                    {msg.metadata.insights.map((insight: any, index: number) => (
                                      <li key={index} className="text-xs">
                                        • {insight.title}: {insight.description}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>

              {/* Message Input */}
              <div className="bg-white border-t border-gray-200 p-4">
                <form onSubmit={handleSendMessage} className="flex space-x-4">
                  <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder={
                      user?.role === 'ceo' ? 'Ask about your company data...' :
                      user?.role === 'group_ceo' ? 'Ask about group companies data...' :
                      'Ask about financial data...'
                    }
                    className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={sendMessageMutation.isLoading}
                  />
                  <button
                    type="submit"
                    disabled={!message.trim() || sendMessageMutation.isLoading}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Send className="h-5 w-5" />
                  </button>
                </form>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <MessageSquare className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No session selected</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Select a chat session or create a new one to start analyzing.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Chat; 