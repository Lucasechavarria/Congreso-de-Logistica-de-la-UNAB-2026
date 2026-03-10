import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";

const IMAGES = [
    {
        url: "/images/historia-1.png",
        title: "Gran Apertura",
        description: "Auditorio colmado en la primera edición del congreso."
    },
    {
        url: "/images/historia-2.png",
        title: "Networking Empresarial",
        description: "Espacios de conexión entre profesionales y empresas líderes."
    },
    {
        url: "/images/historia-3.png",
        title: "Innovación en Escena",
        description: "Presentaciones de vanguardia en logística y transporte."
    }
];

export default function PreviousCongressSection() {
    return (
        <section className="py-24 bg-white relative overflow-hidden">
            <div className="container mx-auto px-4 relative z-10">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mb-16"
                >
                    <h2 className="text-3xl md:text-5xl font-extrabold text-[#2d1854] mb-6 tracking-tight">
                        Nuestra Historia
                    </h2>
                    <div className="w-20 h-1 bg-[#8b5cf6] mx-auto mb-8 rounded-full"></div>
                    <p className="text-xl text-slate-600 leading-relaxed max-w-3xl mx-auto">
                        El Primer Congreso de Logística y Transporte fue un hito para la región, reuniendo a más de 1000 asistentes y 50 empresas líderes para debatir el futuro del sector.
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {IMAGES.map((img, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, scale: 0.9 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.1 }}
                            viewport={{ once: true }}
                        >
                            <Card className="overflow-hidden border-none shadow-xl hover:shadow-2xl transition-all duration-500 group rounded-2xl">
                                <div className="relative h-64 overflow-hidden">
                                    <img
                                        src={img.url}
                                        alt={img.title}
                                        className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-6">
                                        <h3 className="text-white font-bold text-xl">{img.title}</h3>
                                        <p className="text-white/80 text-sm mt-2">{img.description}</p>
                                    </div>
                                </div>
                            </Card>
                        </motion.div>
                    ))}
                </div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="mt-16 bg-[#f5f0ff] p-8 md:p-12 rounded-3xl border border-[#8b5cf6]/10 relative overflow-hidden"
                >
                    <div className="absolute -right-20 -top-20 w-64 h-64 bg-[#8b5cf6]/5 rounded-full blur-3xl"></div>
                    <div className="relative z-10 flex flex-col md:flex-row items-center gap-8">
                        <div className="flex-1 text-center md:text-left">
                            <h3 className="text-2xl font-bold text-[#2d1854] mb-4">Un Legado de Innovación</h3>
                            <p className="text-slate-700 leading-relaxed">
                                Durante la primera edición, exploramos las últimas tendencias en logística 4.0, sostenibilidad y los desafíos de la última milla. El éxito rotundo nos impulsó a redoblar esfuerzos para este 2026, buscando expandir los horizontes del conocimiento y la práctica profesional.
                            </p>
                        </div>
                        <div className="flex-shrink-0 grid grid-cols-2 gap-4">
                            <div className="text-center p-4 bg-white rounded-2xl shadow-sm border border-slate-100">
                                <div className="text-3xl font-black text-[#8b5cf6]">1000+</div>
                                <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Asistentes</div>
                            </div>
                            <div className="text-center p-4 bg-white rounded-2xl shadow-sm border border-slate-100">
                                <div className="text-3xl font-black text-[#8b5cf6]">50+</div>
                                <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Empresas</div>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </section>
    );
}
