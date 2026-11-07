import React, { Suspense, lazy } from "react";
import { HelmetProvider } from "react-helmet-async";
import "./global.css";

import { Toaster } from "@/components/ui/toaster";
import { createRoot } from "react-dom/client";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ScrollToTop from "./components/ScrollToTop";
import PageLoader from "./components/PageLoader";
import Layout from "./components/Layout";

// Vistas con Lazy Loading y Code-Splitting para alta velocidad móvil
const Index = lazy(() => import("./pages/Index"));
const NotFound = lazy(() => import("./pages/NotFound"));
const Programa = lazy(() => import("./pages/Programa"));
const SeleccionRegistro = lazy(() => import("./pages/SeleccionRegistro"));
const RegistroEmpresas = lazy(() => import("./pages/RegistroEmpresas"));
const RegistroParticipantes = lazy(() => import("./pages/RegistroParticipantes"));
const RegistroDisertante = lazy(() => import("./pages/RegistroDisertante"));
const Ponentes = lazy(() => import("./pages/Ponentes"));
const Contacto = lazy(() => import("./pages/Contacto"));
const Empresas = lazy(() => import("./pages/Empresas"));
const VerificarDNI = lazy(() => import("./pages/VerificarDNI"));
const RegistroRapido = lazy(() => import("./pages/RegistroRapido"));
const GenerarQRs = lazy(() => import("./pages/GenerarQRs"));
const HistoriaCampus = lazy(() => import("./pages/HistoriaCampus"));
const ActualizarDNI = lazy(() => import("./pages/ActualizarDNI"));
const BolsaTrabajo = lazy(() => import("./pages/BolsaTrabajo"));
const PostularVacante = lazy(() => import("./pages/PostularVacante"));
const DetalleOferta = lazy(() => import("./pages/DetalleOferta"));
const SobreElCongreso = lazy(() => import("./pages/SobreElCongreso"));

// QueryClient con políticas de caché y reintentos adaptadas al día del evento
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutos de caché para optimizar concurrencia
      retry: 1,                 // 1 reintento para no saturar al servidor
      refetchOnWindowFocus: false,
    },
  },
});

const App = () => (
  <HelmetProvider>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <ScrollToTop />
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route
                path="/programa"
                element={
                  <Layout>
                    <Programa />
                  </Layout>
                }
              />
              <Route
                path="/registro"
                element={
                  <Layout>
                    <SeleccionRegistro />
                  </Layout>
                }
              />
              <Route
                path="/seleccion-registro"
                element={
                  <Layout>
                    <SeleccionRegistro />
                  </Layout>
                }
              />
              <Route
                path="/registro-participantes"
                element={
                  <Layout>
                    <RegistroParticipantes />
                  </Layout>
                }
              />
              <Route
                path="/registro-empresas"
                element={
                  <Layout>
                    <RegistroEmpresas />
                  </Layout>
                }
              />
              <Route
                path="/registro-disertante"
                element={
                  <Layout>
                    <RegistroDisertante />
                  </Layout>
                }
              />
              <Route
                path="/ponentes"
                element={
                  <Layout>
                    <Ponentes />
                  </Layout>
                }
              />
              <Route
                path="/empresas"
                element={
                  <Layout>
                    <Empresas />
                  </Layout>
                }
              />
              <Route
                path="/contacto"
                element={
                  <Layout>
                    <Contacto />
                  </Layout>
                }
              />
              <Route
                path="/historia-campus"
                element={
                  <Layout>
                    <HistoriaCampus />
                  </Layout>
                }
              />
              <Route
                path="/verificar-dni"
                element={
                  <Layout>
                    <VerificarDNI />
                  </Layout>
                }
              />
              <Route
                path="/registro-rapido"
                element={
                  <Layout>
                    <RegistroRapido />
                  </Layout>
                }
              />
              <Route
                path="/generar-qrs"
                element={
                  <Layout>
                    <GenerarQRs />
                  </Layout>
                }
              />
              <Route
                path="/sobre-el-congreso"
                element={
                  <Layout>
                    <SobreElCongreso />
                  </Layout>
                }
              />
              <Route
                path="/actualizar-dni"
                element={
                  <Layout>
                    <ActualizarDNI />
                  </Layout>
                }
              />
              <Route
                path="/bolsa-de-trabajo"
                element={
                  <Layout>
                    <BolsaTrabajo />
                  </Layout>
                }
              />
              <Route
                path="/bolsa-de-trabajo/:id"
                element={
                  <Layout>
                    <DetalleOferta />
                  </Layout>
                }
              />
              <Route
                path="/empresas/postular-vacante"
                element={
                  <Layout>
                    <PostularVacante />
                  </Layout>
                }
              />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  </HelmetProvider>
);

createRoot(document.getElementById("root")!).render(<App />);
