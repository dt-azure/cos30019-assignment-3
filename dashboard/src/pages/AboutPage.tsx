import { BookOpen, Users, Code, Globe } from "lucide-react";

export function AboutPage() {
  return (
    <div className="page page-about">
      <section className="about-hero">
        <h1>About This Project</h1>
        <p>COS30019 - Introduction to AI, Assignment 2B</p>
      </section>

      <section className="about-content">
        <div className="about-card">
          <h2>
            <BookOpen size={22} />
            Project Overview
          </h2>
          <p>
            The Traffic-Based Route Guidance System (TBRGS) uses machine learning to predict
            traffic flow at SCATS intersections in the Boroondara area, then dynamically
            calculates optimal routes based on predicted travel times.
          </p>
          <p>
            The system integrates three ML models (LSTM, GRU, LightGBM) with graph-based
            search algorithms (A*, Uniform Cost Search) to provide real-time route
            recommendations.
          </p>
        </div>

        <div className="about-card">
          <h2>
            <Code size={22} />
            Technology Stack
          </h2>
          <div className="tech-grid">
            <div className="tech-item">
              <h4>Backend</h4>
              <ul>
                <li>Python 3.12</li>
                <li>FastAPI</li>
                <li>TensorFlow / Keras</li>
                <li>LightGBM</li>
                <li>scikit-learn</li>
              </ul>
            </div>
            <div className="tech-item">
              <h4>Frontend</h4>
              <ul>
                <li>React 18 + TypeScript</li>
                <li>Vite</li>
                <li>Leaflet (Maps)</li>
                <li>Recharts (Charts)</li>
                <li>React Router</li>
              </ul>
            </div>
            <div className="tech-item">
              <h4>ML Models</h4>
              <ul>
                <li>LSTM (Long Short-Term Memory)</li>
                <li>GRU (Gated Recurrent Unit)</li>
                <li>LightGBM (Gradient Boosting)</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="about-card">
          <h2>
            <Users size={22} />
            How It Works
          </h2>
          <ol className="steps-list">
            <li>
              <strong>Data Processing:</strong> Raw SCATS traffic data is loaded, normalized,
              and split chronologically into train/validation/test sets.
            </li>
            <li>
              <strong>Model Training:</strong> Three ML models are trained to predict the next
              15-minute traffic flow at each of the 40 SCATS sites.
            </li>
            <li>
              <strong>Flow-to-Speed Conversion:</strong> Predicted flows are converted to speeds
              using the fundamental diagram of traffic flow (quadratic relationship).
            </li>
            <li>
              <strong>Travel Time Estimation:</strong> Speed + distance + 30s intersection delay
              gives travel time for each road segment.
            </li>
            <li>
              <strong>Route Finding:</strong> A* or Uniform Cost Search finds the top-k optimal
              routes from origin to destination.
            </li>
          </ol>
        </div>

        <div className="about-card">
          <h2>
            <Globe size={22} />
            Resources
          </h2>
          <ul className="resources-list">
            <li>
              <strong>Dataset:</strong> VicRoads SCATS traffic data (October 2006) - Boroondara area
            </li>
            <li>
              <strong>Traffic Flow Model:</strong> Fundamental Diagram of Traffic Flow
              (<a href="https://en.wikipedia.org/wiki/Fundamental_diagram_of_traffic_flow" target="_blank" rel="noopener noreferrer">Wikipedia</a>)
            </li>
            <li>
              <strong>Map Tiles:</strong> OpenStreetMap contributors
            </li>
            <li>
              <strong>ML Libraries:</strong> TensorFlow, Keras, LightGBM, scikit-learn
            </li>
          </ul>
        </div>
      </section>
    </div>
  );
}
