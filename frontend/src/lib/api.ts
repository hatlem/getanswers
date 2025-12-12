// API Client for GetAnswers Backend
// Handles authentication, request/response interceptors, and type-safe API calls

import type {
  User,
  ActionCard,
  ConversationThread,
  NavigationCount,
  EfficiencyStats,
  QueueResponse
} from '../types';

// API Configuration
const getBaseUrl = (): string => {
  // If VITE_API_BASE_URL is set (even to empty string), use it
  // Empty string means use relative URLs (for proxy setup)
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl !== undefined && envUrl !== '') {
    return envUrl;
  }
  // If envUrl is empty string or undefined, use relative URLs for proxy or default
  if (envUrl === '') {
    return '';
  }
  return 'http://localhost:8000';
};

// Auth Token Management
const TOKEN_KEY = 'getanswers_auth_token';

export const tokenManager = {
  get: (): string | null => {
    return localStorage.getItem(TOKEN_KEY);
  },
  set: (token: string): void => {
    localStorage.setItem(TOKEN_KEY, token);
  },
  remove: (): void => {
    localStorage.removeItem(TOKEN_KEY);
  },
};

// API Error Types
export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: unknown
  ) {
    super(`API Error ${status}: ${statusText}`);
    this.name = 'ApiError';
  }
}

// Request/Response Types
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface QueueParams extends Record<string, unknown> {
  filter?: 'all' | 'high_risk' | 'low_confidence';
  status?: string;
  limit?: number;
  offset?: number;
}

export interface Stats {
  navigationCounts: NavigationCount;
  efficiencyStats: EfficiencyStats;
  globalStatus: {
    status: 'all_clear' | 'pending_decisions' | 'urgent';
    message: string;
    pendingCount: number;
  };
}

// HTTP Client with interceptors
class HttpClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = getBaseUrl();
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = tokenManager.get();

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Add Authorization header if token exists
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Handle 401 Unauthorized - redirect to login
      if (response.status === 401) {
        tokenManager.remove();
        window.location.href = '/login';
        throw new ApiError(401, 'Unauthorized', { redirected: true });
      }

      // Handle other error responses
      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { message: response.statusText };
        }
        throw new ApiError(response.status, response.statusText, errorData);
      }

      // Handle empty responses (e.g., 204 No Content)
      if (response.status === 204 || response.headers.get('content-length') === '0') {
        return {} as T;
      }

      // Parse JSON response
      const data = await response.json();
      return data as T;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      // Network errors or other fetch failures
      throw new ApiError(0, 'Network Error', { originalError: error });
    }
  }

  async get<T>(endpoint: string, params?: Record<string, unknown>): Promise<T> {
    const queryString = params
      ? '?' + new URLSearchParams(
          Object.entries(params).reduce((acc, [key, value]) => {
            if (value !== undefined && value !== null) {
              acc[key] = String(value);
            }
            return acc;
          }, {} as Record<string, string>)
        ).toString()
      : '';

    return this.request<T>(`${endpoint}${queryString}`, {
      method: 'GET',
    });
  }

  async post<T>(endpoint: string, body?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put<T>(endpoint: string, body?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async patch<T>(endpoint: string, body?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }
}

// Create HTTP client instance
const httpClient = new HttpClient();

// API Endpoints organized by domain
export const api = {
  // Authentication endpoints
  auth: {
    login: async (email: string, password: string): Promise<AuthResponse> => {
      const response = await httpClient.post<AuthResponse>('/api/auth/login', {
        email,
        password,
      });
      tokenManager.set(response.access_token);
      return response;
    },

    register: async (
      email: string,
      password: string,
      name: string
    ): Promise<AuthResponse> => {
      const response = await httpClient.post<AuthResponse>('/api/auth/register', {
        email,
        password,
        name,
      });
      tokenManager.set(response.access_token);
      return response;
    },

    me: async (): Promise<User> => {
      return httpClient.get<User>('/api/auth/me');
    },

    logout: (): void => {
      tokenManager.remove();
    },

    requestMagicLink: async (email: string): Promise<void> => {
      await httpClient.post<void>('/api/auth/magic-link/request', { email });
    },

    verifyMagicLink: async (token: string): Promise<AuthResponse> => {
      const response = await httpClient.post<AuthResponse>('/api/auth/magic-link/verify', {
        token,
      });
      tokenManager.set(response.access_token);
      return response;
    },

    getGmailAuthUrl: async (): Promise<{ url: string }> => {
      return httpClient.get<{ url: string }>('/api/auth/gmail/authorize');
    },

    handleGmailCallback: async (code: string, state: string): Promise<void> => {
      await httpClient.post<void>('/api/auth/gmail/callback', { code, state });
    },

    disconnectGmail: async (): Promise<void> => {
      await httpClient.post<void>('/api/auth/gmail/disconnect');
    },
  },

  // Queue management endpoints
  queue: {
    getQueue: async (params?: QueueParams): Promise<QueueResponse> => {
      return httpClient.get<QueueResponse>('/api/queue', params);
    },

    approve: async (id: string): Promise<ActionCard> => {
      return httpClient.post<ActionCard>(`/api/queue/${id}/approve`);
    },

    override: async (id: string, reason: string): Promise<ActionCard> => {
      return httpClient.post<ActionCard>(`/api/queue/${id}/override`, { reason });
    },

    edit: async (id: string, content: string): Promise<ActionCard> => {
      return httpClient.patch<ActionCard>(`/api/queue/${id}`, {
        proposedAction: content
      });
    },

    escalate: async (id: string, reason: string): Promise<ActionCard> => {
      return httpClient.post<ActionCard>(`/api/queue/${id}/escalate`, { reason });
    },
  },

  // Statistics endpoints
  stats: {
    get: async (): Promise<Stats> => {
      return httpClient.get<Stats>('/api/stats');
    },
  },

  // Conversation endpoints
  conversations: {
    get: async (id: string): Promise<ConversationThread> => {
      return httpClient.get<ConversationThread>(`/api/conversations/${id}`);
    },

    getByObjectiveId: async (objectiveId: string): Promise<ConversationThread> => {
      return httpClient.get<ConversationThread>(`/api/objectives/${objectiveId}/conversation`);
    },
  },
};

export default api;
