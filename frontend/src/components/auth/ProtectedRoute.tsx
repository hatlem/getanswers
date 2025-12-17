import { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Loader2, Layers, ShieldX } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireSuperAdmin?: boolean;
}

export function ProtectedRoute({ children, requireSuperAdmin = false }: ProtectedRouteProps) {
  const location = useLocation();
  const { isAuthenticated, isLoading, checkAuth, user } = useAuthStore();

  useEffect(() => {
    // Check authentication status when component mounts
    checkAuth();
  }, [checkAuth]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="h-screen bg-surface-base flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center mx-auto mb-4">
            <Layers className="w-9 h-9 text-white" />
          </div>
          <div className="flex items-center justify-center gap-2 text-text-secondary">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="text-sm font-medium">Loading...</span>
          </div>
        </motion.div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check super admin access
  if (requireSuperAdmin && !user?.is_super_admin) {
    return (
      <div className="h-screen bg-surface-base flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center max-w-md px-4"
        >
          <div className="w-16 h-16 rounded-xl bg-error/20 flex items-center justify-center mx-auto mb-4">
            <ShieldX className="w-9 h-9 text-error" />
          </div>
          <h2 className="text-xl font-bold text-text-primary mb-2">Access Denied</h2>
          <p className="text-text-secondary mb-4">
            This page requires super admin privileges.
          </p>
          <a
            href="/dashboard"
            className="inline-flex items-center gap-2 px-4 py-2 bg-accent-cyan text-white rounded-lg hover:bg-accent-cyan/90 transition-colors"
          >
            Back to Dashboard
          </a>
        </motion.div>
      </div>
    );
  }

  // Render protected content
  return <>{children}</>;
}
