import { create } from 'zustand';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  gmailConnected: boolean;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  requestMagicLink: (email: string) => Promise<void>;
  verifyMagicLink: (token: string) => Promise<void>;
  logout: () => void;
  connectGmail: () => void;
  disconnectGmail: () => void;
  handleGmailCallback: (code: string) => Promise<void>;
  clearError: () => void;
  checkAuth: () => Promise<void>;
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  gmailConnected: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
            credentials: 'include',
          });

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Login failed');
          }

          const { user, gmailConnected } = await response.json();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            gmailConnected: gmailConnected || false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Login failed',
            isLoading: false
          });
          throw error;
        }
      },

      register: async (name: string, email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password }),
            credentials: 'include',
          });

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Registration failed');
          }

          const { user } = await response.json();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            gmailConnected: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Registration failed',
            isLoading: false
          });
          throw error;
        }
      },

      requestMagicLink: async (email: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch(`${API_BASE}/auth/magic-link`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email }),
          });

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to send magic link');
          }

          set({ isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to send magic link',
            isLoading: false
          });
          throw error;
        }
      },

      verifyMagicLink: async (token: string): Promise<void> => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch(`${API_BASE}/auth/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token }),
            credentials: 'include',
          });

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Invalid or expired link');
          }

          const { user, gmailConnected } = await response.json();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            gmailConnected: gmailConnected || false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Verification failed',
            isLoading: false
          });
          throw error;
        }
      },

      logout: (): void => {
        fetch(`${API_BASE}/auth/logout`, {
          method: 'POST',
          credentials: 'include',
        }).catch((error) => {
          // Log error but don't block logout
          console.error('Logout API call failed:', error);
        });

        set({
          user: null,
          isAuthenticated: false,
          gmailConnected: false,
          error: null
        });
      },

      connectGmail: () => {
        // Redirect to Gmail OAuth
        window.location.href = `${API_BASE}/auth/gmail`;
      },

      disconnectGmail: async (): Promise<void> => {
        try {
          const response = await fetch(`${API_BASE}/auth/gmail/disconnect`, {
            method: 'POST',
            credentials: 'include',
          });

          if (response.ok) {
            set({ gmailConnected: false });
          }
        } catch (error) {
          console.error('Failed to disconnect Gmail:', error);
        }
      },

      handleGmailCallback: async (code: string): Promise<void> => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch(`${API_BASE}/auth/gmail/callback?code=${code}`, {
            method: 'GET',
            credentials: 'include',
          });

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Gmail connection failed');
          }

          set({ gmailConnected: true, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Gmail connection failed',
            isLoading: false
          });
          throw error;
        }
      },

      clearError: () => set({ error: null }),

  checkAuth: async (): Promise<void> => {
    set({ isLoading: true });
    try {
      const response = await fetch(`${API_BASE}/auth/me`, {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const { user, gmailConnected } = await response.json();
        set({
          user,
          isAuthenticated: true,
          gmailConnected: gmailConnected || false,
          isLoading: false
        });
      } else {
        set({
          user: null,
          isAuthenticated: false,
          gmailConnected: false,
          isLoading: false
        });
      }
    } catch (error) {
      set({
        user: null,
        isAuthenticated: false,
        gmailConnected: false,
        isLoading: false
      });
    }
  },
}));
