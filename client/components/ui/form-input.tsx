import React from 'react';
import { cn } from '@/lib/utils';

interface FormInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
  hint?: string;
  helperText?: React.ReactNode;
}

export const FormInput = React.forwardRef<HTMLInputElement, FormInputProps>(
  ({ className, label, error, icon, hint, helperText, type, ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="text-sm font-semibold text-slate-800 tracking-wide">
            {label}
          </label>
        )}
        <div className="relative group">
          {icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-congress-cyan transition-colors duration-200">
              {icon}
            </div>
          )}
          <input
            type={type}
            className={cn(
              "flex h-12 w-full rounded-xl border border-slate-200 bg-white/80 backdrop-blur-sm px-4 py-2 text-sm font-medium text-slate-900 placeholder:text-slate-500 transition-all duration-200",
              "focus:border-congress-cyan focus:ring-4 focus:ring-congress-cyan/10 focus:bg-white focus:outline-none",
              "hover:border-slate-300 hover:bg-white/90",
              "shadow-sm hover:shadow-md focus:shadow-lg",
              icon && "pl-10",
              error && "border-red-400 focus:border-red-500 focus:ring-red-500/10",
              className
            )}
            ref={ref}
            {...props}
          />
        </div>
        {hint && !error && (
          <p className="text-xs text-slate-600 mt-1">{hint}</p>
        )}
        {helperText && !error && (
          <p className="text-xs text-slate-500 mt-1">{helperText}</p>
        )}
        {error && (
          <p className="text-xs text-red-600 font-medium mt-1 animate-in slide-in-from-top-1 duration-200">
            {error}
          </p>
        )}
      </div>
    );
  }
);

FormInput.displayName = "FormInput";
