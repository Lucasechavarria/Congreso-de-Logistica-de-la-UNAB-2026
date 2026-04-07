import { HelmetProvider } from "react-helmet-async";
import "./global.css";

import { Toaster } from "@/components/ui/toaster";
import { createRoot } from "react-dom/client";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ScrollToTop from "./components/ScrollToTop";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import Programa from "./pages/Programa";
import SeleccionRegistro from "./pages/SeleccionRegistro";
import RegistroEmpresas from "./pages/RegistroEmpresas";
import RegistroParticipantes from "./pages/RegistroParticipantes";
import RegistroDisertante from "./pages/RegistroDisertante";
import Ponentes from "./pages/Ponentes";
import Contacto from "././pages/Contacto";
import Empresas from "./pages/Empresas";
import VerificarDNI from "./pages/VerificarDNI";
import RegistroRapido from "./pages/RegistroRapido";
import GenerarQRs from "./pages/GenerarQRs";
import HistoriaCampus from "./pages/HistoriaCampus";
import ActualizarDNI from "./pages/ActualizarDNI";
import BolsaTrabajo from "./pages/BolsaTrabajo";
import PostularVacante from "./pages/PostularVacante";

import SobreElCongreso from "./pages/SobreElCongreso";
import Layout from "./components/Layout";

const queryClient = new QueryClient();

const App = () => (
  <HelmetProvider>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <ScrollToTop />
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
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  </HelmetProvider>
);

createRoot(document.getElementById("root")!).render(<App />);
