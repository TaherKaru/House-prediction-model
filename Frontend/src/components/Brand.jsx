import { Link } from 'react-router-dom'

export default function Brand({ compact = false }) {
  return (
    <Link className={`brand${compact ? " brand-compact" : ""}`} to="/">
      {!compact && <span className="brand-mark">E</span>}
      EstatePredict
    </Link>
  )
}
