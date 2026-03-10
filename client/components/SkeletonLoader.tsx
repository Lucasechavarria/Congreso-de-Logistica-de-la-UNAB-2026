import React from "react";

interface SkeletonLoaderProps {
    className?: string;
    type?: "card" | "avatar" | "text" | "logo";
}

export default function SkeletonLoader({ className = "", type = "text" }: SkeletonLoaderProps) {
    // Clases base compartidas
    const baseClasses = "animate-pulse bg-slate-200 rounded-md";

    // Clases específicas por tipo
    const typeClasses = {
        avatar: "rounded-full w-12 h-12",
        text: "h-4 w-full",
        logo: "w-32 h-16 rounded-lg",
        card: "w-full h-48 rounded-2xl",
    };

    return <div className={`${baseClasses} ${typeClasses[type]} ${className}`} />;
}
