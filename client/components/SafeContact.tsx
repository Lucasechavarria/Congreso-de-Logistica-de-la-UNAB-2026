import React from "react";

interface SafeContactProps {
  type: "email" | "whatsapp";
  user?: string; // Para email: parte local
  domain?: string; // Para email: dominio
  phone?: string; // Para whatsapp: número completo sin espacios ni +
  label?: string; // Texto a mostrar
  className?: string;
  icon?: React.ReactNode;
}

/**
 * SafeContact component to prevent bot scraping.
 * It avoids putting mailto: or wa.me: in the static HTML.
 */
export default function SafeContact({ 
  type, 
  user = "", 
  domain = "", 
  phone = "", 
  label, 
  className = "", 
  icon 
}: SafeContactProps) {
  
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    
    if (type === "email") {
      // Reconstruir email dinámicamente
      const email = `${user}@${domain}`;
      window.location.href = `mailto:${email}`;
    } else if (type === "whatsapp") {
      // Reconstruir link de WhatsApp
      // El número solicitado es: +54 9 11 7827-0919 -> 5491178270919
      const cleanPhone = phone.replace(/\D/g, "");
      const msg = encodeURIComponent("Hola, quisiera recibir información sobre el Congreso de Logística 2026");
      window.open(`https://wa.me/${cleanPhone}?text=${msg}`, "_blank", "noopener,noreferrer");
    }
  };

  return (
    <button
      onClick={handleClick}
      className={`inline-flex items-center text-left focus:outline-none focus:ring-0 ${className} hover:opacity-80 transition-opacity`}
      title={type === "email" ? "Enviar correo" : "Contacto WhatsApp"}
    >
      {icon && <span className="mr-2">{icon}</span>}
      <span className="break-all">{label || (type === "email" ? "Enviar Correo" : "WhatsApp")}</span>
    </button>
  );
}
