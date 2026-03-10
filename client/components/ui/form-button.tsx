import React from 'react';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

interface FormButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  icon?: React.ReactNode;
  fullWidth?: boolean;
}

const buttonVariants = {
  primary: "bg-gradient-to-r from-congress-cyan to-violet-600 text-white shadow-lg hover:shadow-xl hover:from-congress-cyan/90 hover:to-violet-600/90 focus:ring-congress-cyan/30",
  secondary: "bg-gradient-to-r from-slate-100 to-slate-200 text-slate-800 shadow-md hover:shadow-lg hover:from-slate-200 hover:to-slate-300 focus:ring-slate-300/30",
  outline: "border-2 border-congress-cyan text-congress-cyan bg-white/80 backdrop-blur-sm hover:bg-congress-cyan hover:text-white focus:ring-congress-cyan/30",
  ghost: "text-slate-600 hover:text-slate-900 hover:bg-slate-100 focus:ring-slate-300/30"
};

const buttonSizes = {
  sm: "h-9 px-4 text-sm",
  md: "h-12 px-6 text-sm font-semibold",
  lg: "h-14 px-8 text-base font-semibold"
};

export const FormButton = React.forwardRef<HTMLButtonElement, FormButtonProps>(
  ({
    className,
    variant = 'primary',
    size = 'md',
    isLoading = false,
    icon,
    fullWidth = false,
    children,
    disabled,
    ...props
  }, ref) => {
    return (
      <button
        className={cn(
          "inline-flex items-center justify-center rounded-xl transition-all duration-200 font-medium tracking-wide",
          "focus:outline-none focus:ring-4 focus:ring-offset-2 focus:ring-offset-white",
          "disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none",
          "transform hover:scale-[1.02] active:scale-[0.98]",
          buttonVariants[variant],
          buttonSizes[size],
          fullWidth && "w-full",
          className
        )}
        disabled={disabled || isLoading}
        ref={ref}
        {...props}
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Procesando...
          </>
        ) : (
          <>
            {icon && <span className="mr-2">{icon}</span>}
            {children}
          </>
        )}
      </button>
    );
  }
);

FormButton.displayName = "FormButton";
