import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, type = 'text', ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text-secondary mb-2">
            {label}
          </label>
        )}
        <input
          type={type}
          className={cn(
            'w-full h-11 px-4 rounded-lg',
            'bg-surface-card border text-text-primary placeholder:text-text-muted text-sm',
            'focus:outline-none transition-all',
            error
              ? 'border-critical focus:border-critical focus:ring-1 focus:ring-critical/20'
              : 'border-surface-border focus:border-accent-cyan/50 focus:ring-1 focus:ring-accent-cyan/20',
            props.disabled && 'opacity-50 cursor-not-allowed',
            className
          )}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="mt-1.5 text-xs text-critical">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1.5 text-xs text-text-muted">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
