import React from "react";
import { motion, AnimatePresence } from "framer-motion";

/**
 * WhatsApp Floating Bubble Component.
 * Positioned fixed at the bottom-left corner of the screen.
 * Uses obfuscation logic for security.
 */
export default function WhatsAppBubble() {
  const phone = "5491178270919";
  const message = "Hola, quisiera recibir información sobre el Congreso de Logística 2026. (Nota importante: Solo se atienden mensajes de WhatsApp, no se reciben llamadas).";

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    const cleanPhone = phone.replace(/\D/g, "");
    const encodedMsg = encodeURIComponent(message);
    window.open(`https://wa.me/${cleanPhone}?text=${encodedMsg}`, "_blank", "noopener,noreferrer");
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ scale: 0, opacity: 0, y: 50 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        transition={{ 
          type: "spring", 
          stiffness: 260, 
          damping: 20, 
          delay: 1.5 // Pequeño retraso para que cargue después del contenido principal
        }}
        className="fixed bottom-6 left-6 z-[999]"
      >
        <button
          onClick={handleClick}
          aria-label="Contactar por WhatsApp"
          className="group relative flex items-center justify-center w-16 h-16 bg-[#25D366] text-white rounded-full shadow-[0px_8px_24px_rgba(37,211,102,0.5)] hover:shadow-[0px_12px_32px_rgba(37,211,102,0.6)] hover:scale-110 active:scale-95 transition-all duration-300"
        >
          {/* WhatsApp SVG Logo Oficial */}
          <svg 
            viewBox="0 0 24 24" 
            className="w-10 h-10 fill-current" 
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.414 0 .018 5.393 0 12.03c0 2.123.542 4.197 1.57 6.05L0 24l6.117-1.605a11.845 11.845 0 005.928 1.583h.005c6.637 0 12.032-5.391 12.036-12.029a11.82 11.82 0 00-3.417-8.508z" />
          </svg>

          {/* Badge Tooltip (Opcional, Desktop only) */}
          <span className="hidden lg:block absolute left-full ml-4 py-2 px-4 bg-white text-gray-800 text-sm font-semibold rounded-lg shadow-xl opacity-0 scale-75 group-hover:opacity-100 group-hover:scale-100 transition-all duration-300 pointer-events-none whitespace-nowrap">
            Atención al Congreso
          </span>
          
          {/* Animación de pulso ambiental */}
          <span className="absolute inset-0 rounded-full bg-[#25D366] animate-ping opacity-20 pointer-events-none" />
        </button>
      </motion.div>
    </AnimatePresence>
  );
}
