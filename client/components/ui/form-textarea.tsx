import React from 'react';
import { cn } from '@/lib/utils';

interface FormTextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const FormTextArea = React.forwardRef<HTMLTextAreaElement, FormTextAreaProps>(
  ({ className, label, error, hint, ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="text-sm font-semibold text-slate-800 tracking-wide">
            {label}
          </label>
        )}
        <textarea
          className={cn(
            "flex min-h-[100px] w-full rounded-xl border border-slate-200 bg-white/80 backdrop-blur-sm px-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-500 transition-all duration-200 resize-none",
            "focus:border-congress-cyan focus:ring-4 focus:ring-congress-cyan/10 focus:bg-white focus:outline-none",
            "hover:border-slate-300 hover:bg-white/90",
            "shadow-sm hover:shadow-md focus:shadow-lg",
            error && "border-red-400 focus:border-red-500 focus:ring-red-500/10",
            className
          )}
          ref={ref}
          {...props}
        />
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

FormTextArea.displayName = "FormTextArea";
