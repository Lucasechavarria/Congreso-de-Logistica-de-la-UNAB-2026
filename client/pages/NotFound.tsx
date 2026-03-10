import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import Layout from "@/components/Layout";
import { Button } from "@/components/ui/button";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname,
    );
  }, [location.pathname]);

  return (
    <Layout>
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center">
          <div className="bg-gray-50 rounded-lg p-12">
            <h1 className="text-6xl font-bold text-congress-blue mb-4">404</h1>
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Página no encontrada
            </h2>
            <p className="text-gray-600 mb-8">
              Lo sentimos, la página que buscas no existe o ha sido movida.
            </p>
            <Link to="/">
              <Button
                size="xl"
                className="bg-congress-blue hover:bg-congress-blue-dark text-white font-bold px-12 py-6 text-lg shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all duration-300"
              >
                Volver al Inicio
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default NotFound;
