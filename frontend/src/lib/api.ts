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

// Export apiClient for direct usage
export const apiClient = httpClient;

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

// Billing types
export interface BillingConfig {
  publishable_key: string;
  mode: string;
}

export interface SubscriptionInfo {
  plan: string;
  status: string;
  is_active: boolean;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  stripe_mode: string;
}

export interface CheckoutSession {
  checkout_url: string;
  session_id: string;
}

export interface BillingPortal {
  portal_url: string;
}

export interface FeaturesInfo {
  features: Record<string, boolean>;
  plan: string;
}

// Billing endpoints
export const billingApi = {
  getConfig: async (): Promise<BillingConfig> => {
    return httpClient.get<BillingConfig>('/api/billing/config');
  },

  getSubscription: async (): Promise<SubscriptionInfo> => {
    return httpClient.get<SubscriptionInfo>('/api/billing/subscription');
  },

  createCheckout: async (priceId: string, successUrl: string, cancelUrl: string): Promise<CheckoutSession> => {
    return httpClient.post<CheckoutSession>('/api/billing/checkout', {
      price_id: priceId,
      success_url: successUrl,
      cancel_url: cancelUrl,
    });
  },

  createPortal: async (returnUrl: string): Promise<BillingPortal> => {
    return httpClient.post<BillingPortal>(`/api/billing/portal?return_url=${encodeURIComponent(returnUrl)}`);
  },

  getFeatures: async (): Promise<FeaturesInfo> => {
    return httpClient.get<FeaturesInfo>('/api/billing/features');
  },
};

// Admin types
export interface AdminUser {
  id: string;
  email: string;
  name: string;
  is_super_admin: boolean;
  created_at: string;
}

export interface AdminOrganization {
  id: string;
  name: string;
  slug: string;
  is_personal: boolean;
  is_active: boolean;
  member_count: number;
  created_at: string;
}

export interface PlatformStats {
  total_users: number;
  total_organizations: number;
  total_subscriptions: number;
  users_by_plan: Record<string, number>;
  recent_signups: number;
}

export interface StripePrice {
  id: string;
  unit_amount: number | null;
  currency: string;
  recurring_interval: string | null;
  recurring_interval_count: number | null;
  active: boolean;
  nickname: string | null;
  plan_tier: string | null;
}

export interface StripeProduct {
  id: string;
  name: string;
  description: string | null;
  active: boolean;
  default_price_id: string | null;
  metadata: Record<string, string>;
  created: number;
  prices: StripePrice[];
}

export interface StripeConfig {
  mode: string;
  test_key_configured: boolean;
  live_key_configured: boolean;
  webhook_secret_configured: boolean;
}

export interface CreateProductRequest {
  name: string;
  description?: string;
  plan_tier: 'free' | 'starter' | 'pro' | 'enterprise';
}

export interface UpdateProductRequest {
  name?: string;
  description?: string;
  active?: boolean;
}

export interface CreatePriceRequest {
  product_id: string;
  unit_amount: number;
  currency?: string;
  interval?: 'day' | 'week' | 'month' | 'year';
  interval_count?: number;
  nickname?: string;
  plan_tier: 'free' | 'starter' | 'pro' | 'enterprise';
}

export interface UpdatePriceRequest {
  active?: boolean;
  nickname?: string;
}

// Admin endpoints (super admin only)
export const adminApi = {
  // Platform stats
  getStats: async (): Promise<PlatformStats> => {
    return httpClient.get<PlatformStats>('/api/admin/stats');
  },

  // User management
  listUsers: async (params?: { skip?: number; limit?: number; search?: string; super_admins_only?: boolean }): Promise<AdminUser[]> => {
    return httpClient.get<AdminUser[]>('/api/admin/users', params);
  },

  getUser: async (userId: string): Promise<AdminUser> => {
    return httpClient.get<AdminUser>(`/api/admin/users/${userId}`);
  },

  updateUser: async (userId: string, data: { name?: string; is_super_admin?: boolean }): Promise<AdminUser> => {
    return httpClient.patch<AdminUser>(`/api/admin/users/${userId}`, data);
  },

  deleteUser: async (userId: string): Promise<{ message: string }> => {
    return httpClient.delete<{ message: string }>(`/api/admin/users/${userId}`);
  },

  // Organization management
  listOrganizations: async (params?: { skip?: number; limit?: number; search?: string; include_personal?: boolean }): Promise<AdminOrganization[]> => {
    return httpClient.get<AdminOrganization[]>('/api/admin/organizations', params);
  },

  // Stripe product management
  getStripeConfig: async (): Promise<StripeConfig> => {
    return httpClient.get<StripeConfig>('/api/admin/stripe/config');
  },

  listProducts: async (includeInactive?: boolean): Promise<StripeProduct[]> => {
    return httpClient.get<StripeProduct[]>('/api/admin/stripe/products', { include_inactive: includeInactive });
  },

  getProduct: async (productId: string): Promise<StripeProduct> => {
    return httpClient.get<StripeProduct>(`/api/admin/stripe/products/${productId}`);
  },

  createProduct: async (data: CreateProductRequest): Promise<StripeProduct> => {
    return httpClient.post<StripeProduct>('/api/admin/stripe/products', data);
  },

  updateProduct: async (productId: string, data: UpdateProductRequest): Promise<StripeProduct> => {
    return httpClient.patch<StripeProduct>(`/api/admin/stripe/products/${productId}`, data);
  },

  archiveProduct: async (productId: string): Promise<{ message: string; id: string }> => {
    return httpClient.delete<{ message: string; id: string }>(`/api/admin/stripe/products/${productId}`);
  },

  createPrice: async (data: CreatePriceRequest): Promise<StripePrice> => {
    return httpClient.post<StripePrice>('/api/admin/stripe/prices', data);
  },

  updatePrice: async (priceId: string, data: UpdatePriceRequest): Promise<StripePrice> => {
    return httpClient.patch<StripePrice>(`/api/admin/stripe/prices/${priceId}`, data);
  },

  archivePrice: async (priceId: string): Promise<{ message: string; id: string }> => {
    return httpClient.delete<{ message: string; id: string }>(`/api/admin/stripe/prices/${priceId}`);
  },
};

export default api;
