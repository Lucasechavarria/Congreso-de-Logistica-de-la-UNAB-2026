import Layout from "@/components/Layout";

interface PlaceholderPageProps {
  title: string;
  description: string;
}

export default function PlaceholderPage({
  title,
  description,
}: PlaceholderPageProps) {
  return (
    <Layout>
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center">
          <div className="bg-gray-50 rounded-lg p-12 border-2 border-dashed border-gray-300">
            <h1 className="text-3xl font-bold text-gray-800 mb-4">{title}</h1>
            <p className="text-gray-600 mb-8">{description}</p>
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-800 mb-2">
                🚧 Página en construcción
              </h2>
              <p className="text-gray-600 text-sm">
                Esta sección estará disponible próximamente. Para completar esta
                página, continúa conversando con el asistente para definir el
                contenido específico.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
