import React from 'react';
import { cn } from '@/lib/utils';

interface FormCheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  description?: string;
  error?: string;
}

export const FormCheckbox = React.forwardRef<HTMLInputElement, FormCheckboxProps>(
  ({ className, label, description, error, ...props }, ref) => {
    return (
      <div className="space-y-2">
        <div className="flex items-start space-x-3">
          <div className="relative flex items-center">
            <input
              type="checkbox"
              className={cn(
                "h-5 w-5 rounded-md border-2 border-slate-300 text-congress-cyan transition-all duration-200 cursor-pointer",
                "focus:border-congress-cyan focus:ring-4 focus:ring-congress-cyan/10 focus:ring-offset-0",
                "hover:border-slate-400",
                "checked:bg-congress-cyan checked:border-congress-cyan",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                error && "border-red-400 focus:border-red-500 focus:ring-red-500/10",
                className
              )}
              ref={ref}
              {...props}
            />
          </div>
          {(label || description) && (
            <div className="flex-1 min-w-0">
              {label && (
                <label className="text-sm font-medium text-slate-900 cursor-pointer block">
                  {label}
                </label>
              )}
              {description && (
                <p className="text-sm text-slate-600 mt-0.5">{description}</p>
              )}
            </div>
          )}
        </div>
        {error && (
          <p className="text-xs text-red-600 font-medium ml-8 animate-in slide-in-from-top-1 duration-200">
            {error}
          </p>
        )}
      </div>
    );
  }
);

FormCheckbox.displayName = "FormCheckbox";
