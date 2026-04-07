import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { FiMenu, FiX } from "react-icons/fi";
import { ChevronDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function MobileNav() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [openSubMenu, setOpenSubMenu] = useState<string | null>(null);
  const location = useLocation();

  // Cerrar menú al cambiar de ruta
  useEffect(() => {
    setIsMenuOpen(false);
    setOpenSubMenu(null);
  }, [location.pathname]);

  // Evitar scroll cuando el menú está abierto
  useEffect(() => {
    if (isMenuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }
  }, [isMenuOpen]);

  const toggleSubMenu = (name: string) => {
    setOpenSubMenu(openSubMenu === name ? null : name);
  };

  const menuItems = [
    { name: "Inicio", path: "/", isDropdown: false },
    {
      name: "Sobre el Congreso",
      path: "/sobre-el-congreso",
      isDropdown: true,
      subItems: [
        { name: "Programa", path: "/programa" },
        { name: "Disertantes", path: "/ponentes" },
        { name: "Empresas", path: "/empresas" },
        { name: "Información General", path: "/sobre-el-congreso" },
      ],
    },
    { name: "Registro", path: "/registro", isDropdown: false },
    { name: "Bolsa de Trabajo", path: "/bolsa-de-trabajo", isDropdown: false },
    { name: "Contacto", path: "/contacto", isDropdown: false },
    {
      name: "Historia del Campus",
      path: "/historia-campus",
      isDropdown: false,
    },
  ];

  return (
    <div className="lg:hidden">
      {/* Botón Hamburguesa - Flotante o integrado */}
      <button
        onClick={() => setIsMenuOpen(true)}
        className="text-white p-2 focus:outline-none hover:bg-white/10 rounded-full transition-colors"
        aria-label="Abrir menú"
      >
        <FiMenu size={28} />
      </button>

      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md flex justify-end h-[100dvh]"
          >
            {/* Overlay background click to close */}
            <div 
              className="absolute inset-0" 
              onClick={() => setIsMenuOpen(false)} 
            />

            {/* Menu Panel */}
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="relative w-[300px] max-w-[85%] h-full bg-congress-blue shadow-2xl flex flex-col overflow-hidden"
              style={{ height: '100dvh' }}
            >
              {/* Header con padding para safe area (notch) */}
              <div className="flex items-center justify-between p-6 pt-[calc(env(safe-area-inset-top)+2.5rem)] border-b border-white/10 shrink-0">
                <span className="text-xl font-bold text-white tracking-tight">MENU</span>
                <button
                  onClick={() => setIsMenuOpen(false)}
                  className="text-white p-2 hover:bg-white/10 rounded-full transition-colors"
                >
                  <FiX size={24} />
                </button>
              </div>

              {/* Navigation scrollable area */}
              <nav className="flex-1 overflow-y-auto py-4 px-4 space-y-2 overscroll-contain custom-scrollbar">
                {menuItems.map((item, index) => (
                  <div key={item.name}>
                    {item.isDropdown ? (
                      <div>
                        <button
                          onClick={() => toggleSubMenu(item.name)}
                          className={`w-full flex items-center justify-between p-4 rounded-xl transition-all ${
                            openSubMenu === item.name 
                              ? "bg-white/10 text-congress-cyan" 
                              : "text-white hover:bg-white/5"
                          }`}
                        >
                          <span className="text-lg font-medium">{item.name}</span>
                          <motion.div
                            animate={{ rotate: openSubMenu === item.name ? 180 : 0 }}
                            transition={{ duration: 0.3 }}
                          >
                            <ChevronDown size={20} />
                          </motion.div>
                        </button>
                        
                        <AnimatePresence>
                          {openSubMenu === item.name && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: "auto", opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              transition={{ duration: 0.3, ease: "easeInOut" }}
                              className="overflow-hidden bg-white/5 rounded-b-xl mx-2"
                            >
                              <div className="py-2 flex flex-col">
                                {item.subItems?.map((subItem) => {
                                  const isActive = location.pathname === subItem.path;
                                  return (
                                    <Link
                                      key={subItem.name}
                                      to={subItem.path}
                                      className={`px-6 py-3 text-base transition-colors ${
                                        isActive 
                                          ? "text-congress-cyan font-bold" 
                                          : "text-white/80 hover:text-white"
                                      }`}
                                    >
                                      {subItem.name}
                                    </Link>
                                  );
                                })}
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    ) : (
                      <Link
                        to={item.path}
                        className={`block p-4 rounded-xl transition-all ${
                          location.pathname === item.path
                            ? "bg-white/10 text-congress-cyan font-bold"
                            : "text-white hover:bg-white/5"
                        }`}
                      >
                        <span className="text-lg font-medium">{item.name}</span>
                      </Link>
                    )}
                  </div>
                ))}
              </nav>

              {/* Footer con padding inferior adaptado a dispositivos móviles modernos */}
              <div className="p-6 pb-[calc(env(safe-area-inset-bottom)+2rem)] border-t border-white/10 bg-black/10 shrink-0">
                <p className="text-xs text-white/40 text-center">
                  © 2026 Congreso UNAB <br/> Logística y Transporte
                </p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}