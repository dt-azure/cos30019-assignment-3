import "../styles/Header.scss"

export default function Header() {
  return (
    <header className="header">
      <div className="header-left">
        <h1 className="logo">Traffic-Based Route Guidance System</h1>
      </div>

      <div className="header-right">
        <nav className="nav">
          <button className="nav-item active">Dashboard</button>
          <button className="nav-item">About Us</button>
        </nav>
      </div>
    </header>
  )
}