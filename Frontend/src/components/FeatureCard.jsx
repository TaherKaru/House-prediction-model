export default function FeatureCard({ icon, title, children }) {
  return <article className="feature-card"><div className="feature-icon">{icon}</div><h3>{title}</h3><p>{children}</p></article>
}
