import React from 'react';
import { cn } from '@/lib/utils';
import { ChevronDown } from 'lucide-react';

interface FormSelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
  hint?: string;
  options: Array<{ value: string; label: string; disabled?: boolean }>;
}

export const FormSelect = React.forwardRef<HTMLSelectElement, FormSelectProps>(
  ({ className, label, error, icon, hint, options, ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="text-sm font-semibold text-slate-800 tracking-wide">
            {label}
          </label>
        )}
        <div className="relative group">
          {icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-congress-cyan transition-colors duration-200 z-10">
              {icon}
            </div>
          )}
          <select
            className={cn(
              "flex h-12 w-full rounded-xl border border-slate-200 bg-white/80 backdrop-blur-sm px-4 py-2 text-sm font-medium text-slate-900 transition-all duration-200 appearance-none cursor-pointer",
              "focus:border-congress-cyan focus:ring-4 focus:ring-congress-cyan/10 focus:bg-white focus:outline-none",
              "hover:border-slate-300 hover:bg-white/90",
              "shadow-sm hover:shadow-md focus:shadow-lg",
              icon && "pl-10",
              error && "border-red-400 focus:border-red-500 focus:ring-red-500/10",
              className
            )}
            ref={ref}
            {...props}
          >
            {options.map((option) => (
              <option 
                key={option.value} 
                value={option.value}
                disabled={option.disabled}
                className="py-2"
              >
                {option.label}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500 pointer-events-none" />
        </div>
        {hint && !error && (
          <p className="text-xs text-slate-600 mt-1">{hint}</p>
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

FormSelect.displayName = "FormSelect";
