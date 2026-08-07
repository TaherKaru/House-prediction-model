import { Link } from 'react-router-dom'
import Brand from './Brand'

export default function Navbar() {
  return (
    <header className="navbar">
      <Brand compact />
      <nav className="nav-links" aria-label="Primary navigation">
        <a href="#how-it-works">Features</a><a href="#how-it-works">How It Works</a><a href="#about">About</a>
      </nav>
      <div className="nav-actions">
        <Link className="login-link" to="/login">Log in</Link>
        <Link className="outline-button" to="/signup">Get Started</Link>
      </div>
    </header>
  )
}
