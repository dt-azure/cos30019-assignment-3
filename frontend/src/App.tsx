import { Routes, Route } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { HomePage } from "./pages/HomePage";
import { AboutPage } from "./pages/AboutPage";
import { VisualizationPage } from "./pages/VisualizationPage";
import { MapPredictionPage } from "./pages/MapPredictionPage";

export default function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/visualization" element={<VisualizationPage />} />
        <Route path="/map" element={<MapPredictionPage />} />
      </Routes>
    </div>
  );
}
