import React, { useState, useEffect } from "react";
import ImageSlider from "@/components/ImageSlider";
import FloatingParticles from "@/components/FloatingParticles";
import { motion } from "framer-motion";

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8 } }
};

export default function HistoriaCampus() {
  const heroImages = [
    {
      src: "/images/campus-01.jpg",
      alt: "Vista aérea del campus actual UNaB",
    },
    {
      src: "/images/campus-02.jpg",
      alt: "Ingreso principal y jardines renovados",
    },
    {
      src: "/images/campus-04.jpg",
      alt: "Edificio universitario y áreas verdes",
    },
    {
      src: "/images/Universidad.webp",
      alt: "Fachada de la UNaB",
    },
  ];

  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) => (prevIndex + 1) % heroImages.length);
    }, 4000); // Change image every 4 seconds

    return () => clearInterval(interval);
  }, [heroImages.length]);

  return (
    <div className="min-h-screen font-sans antialiased text-gray-800 relative bg-white">
      <FloatingParticles count={25} />
      <main>
        {/* Hero Section with Fading Background */}
        <section
          className="relative flex h-[60vh] items-center justify-center overflow-hidden text-center md:h-[70vh]"
        >
          {/* Background Images */}
          {heroImages.map((image, index) => (
            <div
              key={image.src}
              className="absolute inset-0 h-full w-full bg-cover bg-center transition-opacity duration-1000 ease-in-out"
              style={{
                backgroundImage: `url(${image.src})`,
                opacity: index === currentImageIndex ? 1 : 0,
              }}
            />
          ))}
          {/* Overlay */}
          <div
            className="absolute inset-0 bg-black/50"
            aria-hidden="true"
          ></div>
          {/* Content */}
          <div className="container mx-auto px-4 max-w-4xl relative z-10">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white tracking-tight [text-shadow:2px_2px_8px_rgba(0,0,0,0.6)]">
              Historia del Predio y la Universidad
            </h1>
          </div>
        </section>

        {/* Sección 1: El Esplendor */}
        <section className="py-16 md:py-24 bg-gradient-to-br from-purple-100 to-fuchsia-100 text-gray-900 relative overflow-hidden">
          <FloatingParticles count={40} color="rgba(88, 28, 135, 0.6)" />
          <div className="container mx-auto px-4 max-w-5xl relative z-10">
            <motion.div
              className="flex flex-col md:flex-row gap-12 items-center"
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeInUp}
            >
              <div className="md:w-1/2">
                <ImageSlider
                  images={[
                    {
                      src: "/images/casona-fachada-trasera.avif",
                      alt: "La mansión vista desde el parque trasero",
                      caption:
                        "La mansión vista desde el parque trasero. Fuente: La Nación",
                    },
                  ]}
                />
              </div>
              <div className="md:w-1/2">
                <p className="text-lg leading-relaxed mb-4">
                  La actual sede de la Universidad Nacional Guillermo Brown
                  (UNaB) se encuentra en la histórica Quinta Rocca, una casona
                  de verano de estilo Tudor construida en 1921 por Luisa Rocca
                  para su hija María Concepción, quien necesitaba "tomar aire
                  puro" por recomendación médica. La mansión, famosa por su lujo
                  y esplendor entre las décadas de 1930 y 1950, fue parte de un
                  predio de 13 hectáreas, el mayor pulmón verde de Almirante
                  Brown.
                </p>
                <p className="text-lg leading-relaxed mb-4">
                  Durante su época dorada, la quinta llegó a tener decenas de
                  empleados: caseros, cocineras, mucamas, niñeras y peones que
                  cuidaban el parque y la casa. El predio contaba con caminos de
                  conchilla, un molino, un patio español con fuente de mármol de
                  Carrara, horno de barro, laguna artificial, pérgola, pileta de
                  mármol y un campanario de 20 metros. La mansión tenía más de
                  una docena de habitaciones, siete baños, boiserie de roble,
                  vitraux, heráldicas y hasta un ascensor instalado en 1946.
                </p>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Sección 2: Galería de fotos del pasado */}
        <section className="py-16 md:py-24 bg-gradient-to-b from-fuchsia-100 to-violet-100 relative">
          <div className="container mx-auto px-4 max-w-5xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-congress-cyan text-center">
              Un vistazo a la historia
            </h2>
            <div className="flex flex-col md:flex-row gap-12 items-center">
              <div className="md:w-1/2">
                <p className="text-lg leading-relaxed mb-4">
                  Las fiestas familiares, los paseos en bote por la laguna, los
                  baños en la pileta y las noches en la terraza bajo las
                  estrellas marcaron la vida de cuatro generaciones. Incluso, en
                  el estanque había peces de la familia de las pirañas, a los
                  que alimentaban con carne, y en el jardín sevillano se
                  celebraban reuniones multitudinarias.
                </p>
                <p className="text-lg leading-relaxed">
                  Con el paso de los años y las crisis, la mansión fue perdiendo
                  su esplendor. El abandono, los robos y la falta de
                  mantenimiento la dejaron en ruinas: se llevaron picaportes,
                  balaustres, faroles y hasta los angelitos de la fuente. El
                  último habitante, Charly, vivió solo allí durante 17 años
                  hasta su fallecimiento en 2006. Finalmente, en 2007 la familia
                  vendió la propiedad al municipio de Almirante Brown, que la
                  destinó a la creación de la universidad.
                </p>
              </div>
              <div className="md:w-1/2">
                <ImageSlider
                  images={[
                    {
                      src: "https://resizer.glanacion.com/resizer/v2/la-casona-tiene-100-anos-y-tiene-una-torre-estilo-JTHGIKZLA5CTZOKCMT42RF46KQ.png?auth=684ec6564f168164864c9b43b9c37ae652cc218e50b74a19a2acac60ae75d27a&width=780&height=520&quality=70&smart=true",
                      alt: "Torre campanario de la casona",
                      caption:
                        "Torre campanario de la casona. Fuente: La Nación",
                    },
                    {
                      src: "https://resizer.glanacion.com/resizer/v2/la-casa-tiene-un-marcado-MHWKCYMWCZDKDAIQTMMJCKORY4.png?auth=929f9183a6970c7be3ba2dd03237546c245c1a4f3348c1eb946fab30699f3cb7&width=780&height=520&quality=70&smart=true",
                      alt: "Eclecticismo arquitectónico de la casona",
                      caption:
                        "Eclecticismo arquitectónico de la casona. Fuente: La Nación",
                    },
                    {
                      src: "https://resizer.glanacion.com/resizer/v2/el-parque-de-adelante-tenia-una-laguna-RKJ53OHNUZHEPBYD4JSWPZ7XTA.png?auth=8802dc68d3dd75c05e05ab2a06b900c01742b94e95e2253e0fbb278f9a2975ca&width=780&height=520&quality=70&smart=true",
                      alt: "Laguna artificial en el parque delantero",
                      caption:
                        "Laguna artificial en el parque delantero. Fuente: La Nación",
                    },
                    {
                      src: "https://resizer.glanacion.com/resizer/v2/en-la-laguna-artificial-habia-un-bote-de-EJWUO5QFDVHT5NAWRUFCUVT55M.png?auth=eb694e6e235b0382fdc51609ffa1413bd5294cda179b1ebda72b0d341cee6c5b&width=780&height=520&quality=70&smart=true",
                      alt: "Bote de madera en la laguna artificial",
                      caption:
                        "Bote de madera en la laguna artificial. Fuente: La Nación",
                    },
                    {
                      src: "https://resizer.glanacion.com/resizer/v2/el-interior-de-la-mansion-esta-recubierto-con-TLLB4USNERHQZOJJUH7CAIUV2U.jpg?auth=52add282c02ea135a494b3d0f47b3c9ecd46a1c4f0df593b3380d8a532e80424&width=780&height=520&quality=70&smart=true",
                      alt: "Interior de la mansión con boiserie",
                      caption:
                        "Interior de la mansión con boiserie. Fuente: La Nación",
                    },
                  ]}
                  interval={4000}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Sección 3: Imágenes de Abandono y Renacimiento */}
        <section className="py-16 md:py-24 bg-gradient-to-br from-violet-100 to-indigo-100 text-gray-900 relative overflow-hidden">
          <FloatingParticles count={40} color="rgba(49, 46, 129, 0.6)" />
          <div className="container mx-auto px-4 max-w-5xl relative z-10">
            <motion.div
              className="flex flex-col md:flex-row gap-12 items-center"
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeInUp}
            >
              <div className="md:w-1/2">
                <div className="flex flex-col gap-4">
                  <img
                    src="https://resizer.glanacion.com/resizer/v2/durante-anos-el-predio-estuvo-en-estado-de-2I64GINC5FHMLE35HR4OGDXRTM.png?auth=8701c2f55e1f072b2ec9c4106cc95019813643bd8eca563b9952ddd69f1b37f0&width=780&height=520&quality=70&smart=true"
                    alt="Predio en estado de abandono"
                    className="rounded shadow-lg w-full transform hover:scale-105 transition-transform duration-500"
                  />
                  <img
                    src="https://resizer.glanacion.com/resizer/v2/durante-anos-la-casona-estuvo-abandonada-se-MPNVHQSZIRAI7LZYQFEZZBR2ZA.jpg?auth=a5676788d470ec81e19985f8e82509fe2e41f16f297a296563020d01dad2473a&width=780&height=520&quality=70&smart=true"
                    alt="Casona abandonada y vandalizada"
                    className="rounded shadow-lg w-full transform hover:scale-105 transition-transform duration-500"
                  />
                </div>
              </div>
              <div className="md:w-1/2">
                <h2 className="text-3xl md:text-4xl font-bold mb-8 text-congress-blue font-display">
                  El lento declive y el renacimiento
                </h2>
                <p className="text-lg leading-relaxed mb-6">
                  Hoy, la UNaB trabaja en la recuperación y puesta en valor de
                  este patrimonio histórico, renovando su legado como espacio de
                  educación y cultura para la comunidad.
                </p>
                <div className="w-20 h-1 bg-congress-cyan rounded-full"></div>
              </div>
            </motion.div>
          </div>
        </section>
      </main>
    </div>
  );
}
