import { ReactNode, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Button } from "./ui/button";
import { ChevronDown, Mail, MapPin, Calendar } from "lucide-react";
import CongressLogo from "./CongressLogo";
import MobileNav from "./MobileNav";
import SafeContact from "./SafeContact";
import WhatsAppBubble from "./WhatsAppBubble";
import { MessageSquare } from "lucide-react";

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const isSobreElCongresoActive = () => {
    return [
      "/programa",
      "/ponentes",
      "/empresas",
      "/sobre-el-congreso",
    ].includes(location.pathname);
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const handleMouseEnter = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsDropdownOpen(true);
  };

  const handleMouseLeave = () => {
    timeoutRef.current = setTimeout(() => {
      setIsDropdownOpen(false);
    }, 200);
  };

  return (
    <div className="min-h-screen bg-white flex flex-col" lang="es" translate="no">
      <Helmet>
        <title>Congreso de Logística y Transporte 2026</title>
        <meta name="description" content="Nuevas oportunidades, grandes desafíos. Campus UNaB, Almirante Brown." />
        <meta property="og:title" content="Congreso de Logística y Transporte 2026" />
        <meta property="og:description" content="El espacio principal para la innovación, tecnología y desarrollo en el sector del transporte y la cadena de suministro." />
        <meta property="og:type" content="website" />
      </Helmet>
      {/* Header */}
      <header className="bg-congress-blue/90 backdrop-blur-md text-white shadow-lg fixed top-0 left-0 w-full z-50">
        <div className="py-6 pl-5 mx-5">
          <div className="flex justify-between items-center">
            {/* Logo and Title */}
            <div className="flex-shrink-0 ml-0">
              <Link
                to="/"
                onClick={() => {
                  if (location.pathname === "/") {
                    window.scrollTo(0, 0);
                  }
                }}
              >
                <img
                  src="/images/CONGRESO-LOGISTICA-2.png"
                  alt="Logo oficial del Congreso de Logística y Transporte 2026 organizado por la Universidad Nacional Guillermo Brown"
                  className="h-20 w-auto"
                />
              </Link>
            </div>

            {/* Navigation */}
            {/* Navegación de escritorio (visible en pantallas grandes) */}
            <nav className="hidden lg:flex flex-wrap gap-2 lg:gap-4 items-center">
              <Link to="/">
                <Button
                  variant={isActive("/") ? "secondary" : "ghost"}
                  className={
                    isActive("/")
                      ? "bg-white text-congress-blue"
                      : "hover:bg-congress-blue-dark text-white"
                  }
                >
                  Inicio
                </Button>
              </Link>
              {/* Dropdown para "Sobre el Congreso" */}
              <div
                className="relative"
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
              >
                <Button
                  variant={isSobreElCongresoActive() ? "secondary" : "ghost"}
                  className={`${isSobreElCongresoActive() ? "bg-white text-congress-blue" : "text-white hover:bg-congress-blue-dark"} flex items-center gap-1`}
                >
                  Sobre el Congreso
                  <ChevronDown
                    className={`h-4 w-4 transition-transform ${isDropdownOpen ? "rotate-180" : ""}`}
                  />
                </Button>
                {isDropdownOpen && (
                  <div className="absolute top-full left-0 mt-1 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
                    <Link
                      to="/programa"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-congress-blue hover:text-white"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      Programa
                    </Link>
                    <Link
                      to="/ponentes"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-congress-blue hover:text-white"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      Disertantes
                    </Link>
                    <Link
                      to="/empresas"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-congress-blue hover:text-white"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      Empresas
                    </Link>
                    <Link
                      to="/sobre-el-congreso"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-congress-blue hover:text-white"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      Primera Edición 2025
                    </Link>
                  </div>
                )}
              </div>
              <Link to="/seleccion-registro">
                <Button
                  variant={
                    isActive("/seleccion-registro") ? "secondary" : "ghost"
                  }
                  className={
                    isActive("/seleccion-registro")
                      ? "bg-white text-congress-blue"
                      : "text-white hover:bg-congress-blue-dark"
                  }
                >
                  Registro
                </Button>
              </Link>
              <Link to="/contacto">
                <Button
                  variant={isActive("/contacto") ? "secondary" : "ghost"}
                  className={
                    isActive("/contacto")
                      ? "bg-white text-congress-blue"
                      : "text-white hover:bg-congress-blue-dark"
                  }
                >
                  Contacto
                </Button>
              </Link>
              <Link to="/historia-campus">
                <Button
                  variant={isActive("/historia-campus") ? "secondary" : "ghost"}
                  className={
                    isActive("/historia-campus")
                      ? "bg-white text-congress-blue"
                      : "text-white hover:bg-congress-blue-dark"
                  }
                >
                  Historia del Campus
                </Button>
              </Link>
            </nav>

            {/* Navigation (Mobile) - Solo visible en móviles, alineado a la derecha */}
            <div className="lg:hidden">
              <MobileNav />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow mt-[124px]">{children}</main>

      {/* Footer */}
      <footer className="bg-[#1a0a2e] text-slate-300 py-16 mt-auto border-t border-white/10 relative overflow-hidden">
        {/* Subtle Background Pattern (Hero Style) */}
        <div className="absolute inset-0 z-0 opacity-[0.03]">
          <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="footer-grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M0 40h40 M40 0v40" stroke="#FFFFFF" strokeWidth="1" fill="none" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#footer-grid)" />
          </svg>
        </div>

        <div className="container mx-auto px-4 md:pl-16 md:pr-8 relative z-10">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-bold mb-4">
                Nuevas oportunidades, grandes desafíos
              </h3>
              <img
                src="/images/CONGRESO-LOGISTICA-2.png"
                alt="Logo del Congreso de Logística"
                className="h-24 w-auto mt-6"
              />
            </div>
            <div className="text-left">
              <h3 className="text-lg font-bold mb-4">Información del Evento</h3>
              <p className="text-gray-300 mb-2 flex items-center justify-start">
                <Calendar className="text-white mr-2 flex-shrink-0 h-5 w-5" />
                <span>7 de Noviembre de 2026</span>
              </p>
              <p className="text-gray-300 mb-2 notranslate flex items-center justify-start">
                <MapPin className="text-white mr-2 flex-shrink-0 h-5 w-5" />
                <span>Campus UNaB, Blas Parera 132, Burzaco</span>
              </p>
              <div className="text-gray-300 notranslate space-y-3">
                {/* Email Seguro */}
                <SafeContact
                  type="email"
                  user="congresologisticaytransporte"
                  domain="unab.edu.ar"
                  className="text-gray-300 hover:text-white transition-colors"
                  icon={<Mail className="text-white flex-shrink-0 h-5 w-5" />}
                  label="congresologisticaytransporte@unab.edu.ar"
                />
                
                {/* WhatsApp Seguro */}
                <SafeContact
                  type="whatsapp"
                  phone="5491178270919"
                  className="text-gray-300 hover:text-white transition-colors"
                  icon={<MessageSquare className="text-green-400 flex-shrink-0 h-5 w-5" />}
                  label="+54 9 11 7827-0919"
                />
              </div>
            </div>
            <div className="notranslate flex flex-col items-center text-center">
              <h3 className="text-lg font-bold mb-4">
                Universidad Nacional Guillermo Brown
              </h3>
              <div className="flex items-center justify-center space-x-3 mb-4">
                <Link
                  to="/"
                  onClick={() => {
                    if (location.pathname === "/") {
                      window.scrollTo(0, 0);
                    }
                  }}
                >
                  <img
                    src="/images/LogoUnab.png"
                    alt="Logo de la Universidad Nacional Guillermo Brown"
                    className="h-24 md:h-28 w-auto bg-white/10 p-3 rounded-xl mx-auto"
                  />
                </Link>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400 notranslate">
            <p>
              &copy; 2026 Universidad Nacional Guillermo Brown. Todos los
              derechos reservados. Desarrollado por{" "}
              <span className="text-white">LDE-System</span>.
            </p>
          </div>
        </div>
      </footer>
      
      {/* Botón Flotante de WhatsApp */}
      <WhatsAppBubble />
    </div>
  );
}
