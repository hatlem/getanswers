import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw, WifiOff, ServerCrash } from 'lucide-react';
import { cn } from '../../lib/utils';

interface ErrorStateProps {
  error: Error | null;
  onRetry?: () => void;
  title?: string;
  description?: string;
  className?: string;
}

export function ErrorState({
  error,
  onRetry,
  title,
  description,
  className,
}: ErrorStateProps) {
  // Determine error type for appropriate icon and messaging
  const isNetworkError = error?.message.includes('Network') || error?.message.includes('network');
  const isServerError = error?.message.includes('500') || error?.message.includes('502') || error?.message.includes('503');

  const defaultTitle = isNetworkError
    ? 'Connection Lost'
    : isServerError
    ? 'Server Error'
    : 'Something Went Wrong';

  const defaultDescription = isNetworkError
    ? 'Please check your internet connection and try again.'
    : isServerError
    ? 'Our servers are experiencing issues. Please try again in a moment.'
    : error?.message || 'An unexpected error occurred. Please try again.';

  const Icon = isNetworkError ? WifiOff : isServerError ? ServerCrash : AlertTriangle;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn('flex flex-col items-center justify-center py-16 text-center', className)}
    >
      {/* Error Icon */}
      <div className="w-16 h-16 rounded-full bg-critical-muted flex items-center justify-center mb-4">
        <Icon className="w-8 h-8 text-critical" />
      </div>

      {/* Error Title */}
      <h3 className="text-lg font-semibold text-text-primary mb-2">
        {title || defaultTitle}
      </h3>

      {/* Error Description */}
      <p className="text-sm text-text-secondary max-w-md mb-6">
        {description || defaultDescription}
      </p>

      {/* Retry Button */}
      {onRetry && (
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onRetry}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20 hover:bg-accent-cyan/20 hover:border-accent-cyan/30 transition-all font-medium text-sm"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Try Again</span>
        </motion.button>
      )}

      {/* Technical Details (collapsed by default) */}
      {error && process.env.NODE_ENV === 'development' && (
        <details className="mt-6 max-w-lg w-full">
          <summary className="cursor-pointer text-xs text-text-muted hover:text-text-secondary transition-colors">
            Technical Details
          </summary>
          <pre className="mt-2 p-3 rounded-lg bg-surface-card border border-surface-border text-left text-xs text-text-secondary overflow-auto">
            {error.toString()}
          </pre>
        </details>
      )}
    </motion.div>
  );
}

// Inline error for smaller spaces (like cards)
interface InlineErrorProps {
  error: Error | null;
  onRetry?: () => void;
  className?: string;
}

export function InlineError({ error, onRetry, className }: InlineErrorProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-3 p-3 rounded-lg bg-critical-muted border border-critical-border',
        className
      )}
    >
      <AlertTriangle className="w-5 h-5 text-critical shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-text-primary">Error</p>
        <p className="text-xs text-text-secondary truncate">
          {error?.message || 'An error occurred'}
        </p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="shrink-0 p-1.5 rounded hover:bg-critical/10 transition-colors"
          title="Retry"
        >
          <RefreshCw className="w-4 h-4 text-critical" />
        </button>
      )}
    </div>
  );
}
