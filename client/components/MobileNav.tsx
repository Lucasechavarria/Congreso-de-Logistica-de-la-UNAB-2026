import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { FiMenu, FiX } from "react-icons/fi";
import { ChevronDown, ChevronUp } from "lucide-react";

export default function MobileNav() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isSubMenuOpen, setIsSubMenuOpen] = useState(false);
  const location = useLocation();

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
    if (isMenuOpen) {
      setIsSubMenuOpen(false);
    }
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
    setIsSubMenuOpen(false);
  };

  const toggleSubMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsSubMenuOpen(!isSubMenuOpen);
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
    { name: "Contacto", path: "/contacto", isDropdown: false },
    {
      name: "Historia del Campus",
      path: "/historia-campus",
      isDropdown: false,
    },
  ];

  return (
    <div className="lg:hidden">
      {/* Hamburger Button */}
      <button
        onClick={toggleMenu}
        className="text-white p-2 focus:outline-none"
      >
        {isMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
      </button>

      {/* Mobile Menu Overlay */}
      {isMenuOpen && (
        <div className="fixed inset-0 bg-congress-blue z-50 flex flex-col items-center justify-center space-y-6">
          <button
            onClick={closeMenu}
            className="absolute top-4 right-4 text-white p-2"
          >
            <FiX size={24} />
          </button>
          <nav className="flex flex-col space-y-4 text-2xl font-semibold w-full px-8">
            {menuItems.map((item, index) => (
              <div
                key={item.name}
                className="animate-fade-in-down"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                {item.isDropdown ? (
                  <>
                    <button
                      onClick={toggleSubMenu}
                      className="w-full text-left text-white hover:text-congress-cyan transition-colors flex items-center justify-between"
                    >
                      {item.name}
                      {isSubMenuOpen ? (
                        <ChevronUp size={24} />
                      ) : (
                        <ChevronDown size={24} />
                      )}
                    </button>
                    {isSubMenuOpen && (
                      <div className="flex flex-col space-y-2 mt-2 pl-4 animate-fade-in-down">
                        {item.subItems?.map((subItem, subIndex) => (
                          <Link
                            key={subItem.name}
                            to={subItem.path}
                            onClick={closeMenu}
                            className="text-base font-normal text-white hover:text-congress-cyan transition-colors"
                            style={{ animationDelay: `${subIndex * 0.1}s` }}
                          >
                            {subItem.name}
                          </Link>
                        ))}
                      </div>
                    )}
                  </>
                ) : (
                  <Link
                    to={item.path}
                    onClick={closeMenu}
                    className="text-white hover:text-congress-cyan transition-colors"
                  >
                    {item.name}
                  </Link>
                )}
              </div>
            ))}
          </nav>
        </div>
      )}
    </div>
  );
}