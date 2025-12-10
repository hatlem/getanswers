// Toast Notification Configuration
// Requires: npm install react-hot-toast
// This file provides configured toast functions for the app

import toast, { Toaster, type ToastOptions } from 'react-hot-toast';
import { CheckCircle2, XCircle, AlertCircle, Info } from 'lucide-react';

// Default toast options matching the app theme
const defaultOptions: ToastOptions = {
  duration: 4000,
  position: 'top-right',
  style: {
    background: '#1a1d29', // surface-card
    color: '#e1e4ed', // text-primary
    border: '1px solid #2a2f3f', // surface-border
    borderRadius: '0.75rem',
    padding: '12px 16px',
    fontSize: '14px',
    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.3)',
  },
};

// Success toast
export const successToast = (message: string, options?: ToastOptions) => {
  return toast.success(message, {
    ...defaultOptions,
    ...options,
    icon: <CheckCircle2 className="w-5 h-5 text-success" />,
    style: {
      ...defaultOptions.style,
      borderColor: '#10b981', // success color
    },
  });
};

// Error toast
export const errorToast = (message: string, options?: ToastOptions) => {
  return toast.error(message, {
    ...defaultOptions,
    ...options,
    duration: 6000, // Longer duration for errors
    icon: <XCircle className="w-5 h-5 text-critical" />,
    style: {
      ...defaultOptions.style,
      borderColor: '#ef4444', // critical color
    },
  });
};

// Warning toast
export const warningToast = (message: string, options?: ToastOptions) => {
  return toast(message, {
    ...defaultOptions,
    ...options,
    icon: <AlertCircle className="w-5 h-5 text-warning" />,
    style: {
      ...defaultOptions.style,
      borderColor: '#f59e0b', // warning color
    },
  });
};

// Info toast
export const infoToast = (message: string, options?: ToastOptions) => {
  return toast(message, {
    ...defaultOptions,
    ...options,
    icon: <Info className="w-5 h-5 text-info" />,
    style: {
      ...defaultOptions.style,
      borderColor: '#3b82f6', // info color
    },
  });
};

// Loading toast
export const loadingToast = (message: string) => {
  return toast.loading(message, defaultOptions);
};

// Promise toast for async operations
export const promiseToast = <T,>(
  promise: Promise<T>,
  messages: {
    loading: string;
    success: string | ((data: T) => string);
    error: string | ((error: Error) => string);
  }
) => {
  return toast.promise(
    promise,
    {
      loading: messages.loading,
      success: messages.success,
      error: messages.error,
    },
    defaultOptions
  );
};

// Action toasts with custom actions
export const actionToast = {
  approve: () => successToast('Action approved successfully'),
  approveError: (error?: string) => errorToast(error || 'Failed to approve action'),

  override: () => successToast('Action overridden successfully'),
  overrideError: (error?: string) => errorToast(error || 'Failed to override action'),

  edit: () => successToast('Reply edited successfully'),
  editError: (error?: string) => errorToast(error || 'Failed to edit reply'),

  escalate: () => infoToast('Action escalated for review'),
  escalateError: (error?: string) => errorToast(error || 'Failed to escalate action'),

  takeOver: () => successToast('Thread taken over'),
  takeOverError: (error?: string) => errorToast(error || 'Failed to take over thread'),
};

// Export the Toaster component for mounting in the app
export { Toaster };

// Re-export the toast function for custom use cases
export { toast };
