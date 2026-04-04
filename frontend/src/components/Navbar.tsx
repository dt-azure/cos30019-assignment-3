import { NavLink } from "react-router-dom";
import { MapPin, Info, BarChart3, Route } from "lucide-react";

export function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <MapPin size={24} />
        <span>TBRGS</span>
      </div>
      <div className="navbar-links">
        <NavLink to="/" end className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          <Route size={16} />
          <span>Home</span>
        </NavLink>
        <NavLink to="/map" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          <MapPin size={16} />
          <span>Map Prediction</span>
        </NavLink>
        <NavLink to="/visualization" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          <BarChart3 size={16} />
          <span>Visualization</span>
        </NavLink>
        <NavLink to="/about" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          <Info size={16} />
          <span>About</span>
        </NavLink>
      </div>
    </nav>
  );
}
