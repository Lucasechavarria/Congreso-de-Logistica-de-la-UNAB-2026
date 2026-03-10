import React from 'react';
import { cn } from '@/lib/utils';

interface FormCardProps {
  title?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export const FormCard: React.FC<FormCardProps> = ({ 
  title, 
  description, 
  children, 
  className 
}) => {
  return (
    <div className={cn(
      "bg-white/90 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20",
      "p-8 md:p-10 space-y-8",
      "hover:shadow-2xl transition-all duration-300",
      className
    )}>
      {(title || description) && (
        <div className="text-center space-y-2">
          {title && (
            <h2 className="text-3xl font-bold text-slate-900 tracking-tight">
              {title}
            </h2>
          )}
          {description && (
            <p className="text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
              {description}
            </p>
          )}
        </div>
      )}
      <div className="space-y-6">
        {children}
      </div>
    </div>
  );
};

interface FormSectionProps {
  title?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export const FormSection: React.FC<FormSectionProps> = ({ 
  title, 
  description, 
  children, 
  className 
}) => {
  return (
    <div className={cn("space-y-4", className)}>
      {(title || description) && (
        <div className="space-y-1">
          {title && (
            <h3 className="text-lg font-semibold text-slate-900 tracking-wide">
              {title}
            </h3>
          )}
          {description && (
            <p className="text-sm text-slate-600">
              {description}
            </p>
          )}
        </div>
      )}
      <div className="space-y-4">
        {children}
      </div>
    </div>
  );
};
