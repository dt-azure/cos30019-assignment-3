import { Link } from "react-router-dom";
import { MapPin, TrendingUp, Zap, ArrowRight } from "lucide-react";

export function HomePage() {
  return (
    <div className="page page-home">
      <section className="hero-section">
        <h1>Traffic-Based Route Guidance System</h1>
        <p className="hero-subtitle">
          AI-powered traffic prediction and dynamic route optimization for the Boroondara area.
          Using LSTM, GRU, and LightGBM models to forecast traffic flow and find the fastest routes.
        </p>
        <div className="hero-actions">
          <Link to="/map" className="btn btn-primary">
            <MapPin size={18} />
            <span>Start Route Planning</span>
            <ArrowRight size={18} />
          </Link>
          <Link to="/visualization" className="btn btn-secondary">
            <TrendingUp size={18} />
            <span>View Model Comparison</span>
          </Link>
        </div>
      </section>

      <section className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">
            <TrendingUp size={28} />
          </div>
          <h3>ML Traffic Prediction</h3>
          <p>Three models (LSTM, GRU, LightGBM) trained on VicRoads SCATS data to predict traffic flow at 40 intersections.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">
            <MapPin size={28} />
          </div>
          <h3>Interactive Map</h3>
          <p>Visualize routes on a real map with traffic conditions, travel times, and turn-by-turn details.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">
            <Zap size={28} />
          </div>
          <h3>Dynamic Routing</h3>
          <p>Real-time edge cost updates based on predicted traffic. A* and Uniform Cost Search for optimal path finding.</p>
        </div>
      </section>

      <section className="stats-section">
        <div className="stat">
          <span className="stat-value">3</span>
          <span className="stat-label">ML Models</span>
        </div>
        <div className="stat">
          <span className="stat-value">40</span>
          <span className="stat-label">SCATS Sites</span>
        </div>
        <div className="stat">
          <span className="stat-value">5</span>
          <span className="stat-label">Top Routes</span>
        </div>
        <div className="stat">
          <span className="stat-value">96</span>
          <span className="stat-label">Edges</span>
        </div>
      </section>
    </div>
  );
}
