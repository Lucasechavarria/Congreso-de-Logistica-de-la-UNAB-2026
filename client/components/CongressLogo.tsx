interface CongressLogoProps {
  size?: "sm" | "md" | "lg";
  showText?: boolean;
  className?: string;
}

export default function CongressLogo({
  size = "md",
  showText = true,
  className = "",
}: CongressLogoProps) {
  const sizeClasses = {
    sm: "w-8 h-8",
    md: "w-12 h-12",
    lg: "w-16 h-16",
  };

  const textSizeClasses = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-xl",
  };

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {/* Congress Logo Icon */}
      <div className={`bg-congress-cyan p-2 rounded-lg ${sizeClasses[size]}`}>
        <div className="w-full h-full bg-white rounded flex items-center justify-center">
          <div className="w-3/4 h-5/6 bg-congress-blue rounded-sm relative">
            {/* Stylized logistics/transport icon */}
            <div className="absolute top-1 left-1 w-1/3 h-1/6 bg-white rounded-sm"></div>
            <div className="absolute top-1/3 left-1 w-2/3 h-1/6 bg-white rounded-sm"></div>
            <div className="absolute bottom-1/3 left-1 w-1/2 h-1/6 bg-white rounded-sm"></div>
            <div className="absolute bottom-1 left-1 w-1/3 h-1/6 bg-white rounded-sm"></div>
          </div>
        </div>
      </div>

      {showText && (
        <div className="flex-1">
          <div
            className={`font-bold text-congress-blue ${textSizeClasses[size]}`}
          >
            CONGRESO DE LOGÍSTICA
          </div>
          <div
            className={`font-bold text-congress-blue ${textSizeClasses[size]}`}
          >
            Y TRANSPORTE
          </div>
          {size !== "sm" && (
            <div
              className={`text-congress-cyan text-xs ${size === "lg" ? "text-sm" : ""}`}
            >
              Universidad Nacional Guillermo Brown
            </div>
          )}
        </div>
      )}
    </div>
  );
}