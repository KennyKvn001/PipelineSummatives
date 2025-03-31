
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import PredictionPage from "./pages/PredictionPage";
import AdminPage from "./pages/AdminPage";
import InsightsPage from "./pages/InsightsPage";
import NotFound from "./pages/NotFound";
import { Sidebar } from "./components/Sidebar";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50 flex">
          <Sidebar />
          <div className="flex-1 flex flex-col">
            <Navbar />
            <main className="flex-grow p-6 overflow-y-auto">
              <div className="max-w-7xl mx-auto">
                <Routes>
                  <Route path="/" element={<PredictionPage />} />
                  <Route path="/admin" element={<AdminPage />} />
                  <Route path="/insights" element={<InsightsPage />} />
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </div>
            </main>
          </div>
        </div>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
