import { ChartNoAxesCombined, Cpu, FilePenLine, LogIn } from "lucide-react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import HouseScene from "../components/HouseScene";

const steps = [
  {
    icon: <LogIn size={19} />,
    number: "1.",
    title: "Login",
    description: "Access secure portal",
    active: true,
  },
  {
    icon: <FilePenLine size={19} />,
    number: "2.",
    title: "Enter Details",
    description: "Input property info",
    active: true,
  },
  {
    icon: <Cpu size={18} />,
    number: "3.",
    title: "ML Model",
    description: "Data processing",
    comingSoon: true,
  },
  {
    icon: <ChartNoAxesCombined size={19} />,
    number: "4.",
    title: "Estimation",
    description: "Final price forecast",
    comingSoon: true,
  },
];

export default function LandingPage() {
  return (
    <main className="site-shell">
      <div className="container">
        <Navbar />
        <section className="hero" id="about">
          <div>
            <h1>
              Predict House Prices with
              <br />
              Artificial Intelligence
            </h1>
            <p className="hero-copy">
              A modern platform that estimates house prices using Machine
              Learning based on property info. Experience precision market
              forecasting tailored for analysts and investors.
            </p>
            <div className="hero-actions">
              <Link className="primary-button" to="/signup">
                Get Started
              </Link>
              <Link className="outline-button" to="/login">
                Login
              </Link>
            </div>
            <p className="tiny-note">
              No credit card required · Built for confident decisions
            </p>
          </div>
          <div className="house-panel">
            <HouseScene />
          </div>
        </section>
        <div className="trust-bar">
          <span className="trust-item">
            <strong>150k+</strong> property records analyzed
          </span>
          <span className="trust-item">
            <strong>98.4%</strong> valuation confidence
          </span>
          <span className="trust-item">
            <strong>24/7</strong> market signal monitoring
          </span>
        </div>
        <section className="landing-how" id="how-it-works">
          <div className="landing-how-heading">
            <h2>How It Works</h2>
            <p>A streamlined process from raw data to actionable insight.</p>
          </div>
          <div
            className="landing-process-line"
            aria-label="Property estimate process"
          >
            {steps.map((step) => (
              <article
                className={`landing-process-step ${step.active ? "is-active" : ""}`}
                key={step.number}
              >
                <div className="landing-step-icon-wrap">
                  {step.comingSoon && (
                    <span className="landing-coming-soon">Coming Soon</span>
                  )}
                  <span className="landing-step-icon">{step.icon}</span>
                </div>
                <h3>
                  <span>{step.number}</span> {step.title}
                </h3>
                <p>{step.description}</p>
              </article>
            ))}
          </div>
        </section>
        <footer className="footer">
          <span>© 2026 Havenly. Find your footing.</span>
          <span className="footer-links">
            <a href="#about">About</a>
            <a href="#how-it-works">Features</a>
            <a href="#">Privacy</a>
          </span>
        </footer>
      </div>
    </main>
  );
}
