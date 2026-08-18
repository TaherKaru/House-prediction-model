import { ArrowLeft, ArrowRight, Check, Eye, EyeOff } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Brand from "../components/Brand";
import { apiRequest } from "../lib/api";

const initialValues = { name: "", email: "", password: "", consent: false };

export default function SignupPage() {
  const navigate = useNavigate();
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function updateField(event) {
    const { name, value, checked, type } = event.target;
    setValues((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
  }
  function validate() {
    const next = {};
    if (!values.name.trim()) next.name = "Please enter your name.";
    if (!/^\S+@\S+\.\S+$/.test(values.email))
      next.email = "Enter a valid email address.";
    if (values.password.length < 8)
      next.password = "Use at least 8 characters.";
    if (!values.consent) next.consent = "Please accept the terms to continue.";
    return next;
  }
  async function handleSubmit(event) {
    event.preventDefault();
    const nextErrors = validate();
    setErrors(nextErrors);
    setSubmitError("");

    if (Object.keys(nextErrors).length) return;

    try {
      setIsSubmitting(true);
      await apiRequest("/api/auth/signup", {
        method: "POST",
        body: JSON.stringify({
          name: values.name,
          email: values.email,
          password: values.password,
        }),
      });
      setSubmitted(true);
      window.setTimeout(() => navigate("/login"), 1200);
    } catch (error) {
      setSubmitError(error.message || "Unable to create account right now.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="signup-shell">
      <aside className="signup-art">
        <Brand />
        <div className="signup-quote">
          <div className="quote-mark">“</div>
          <h1>A calmer way to make one of life’s biggest decisions.</h1>
          <p>
            Start with a clearer picture of the place you’re considering—and
            what it could be worth.
          </p>
        </div>
        <span className="art-footer">Havenly / Property intelligence</span>
      </aside>
      <section className="form-side">
        <div className="form-wrap">
          <Link className="back-link" to="/">
            <ArrowLeft size={15} /> Back to home
          </Link>
          {submitted ? (
            <SuccessState />
          ) : (
            <form className="signup-form" onSubmit={handleSubmit} noValidate>
              <div>
                <h2>Create your account</h2>
                <p className="form-intro">
                  Already have an account? <Link to="/login">Log in</Link>
                </p>
              </div>
              <Field
                label="Full name"
                name="name"
                placeholder="Alex Morgan"
                value={values.name}
                error={errors.name}
                onChange={updateField}
              />
              <Field
                label="Email address"
                name="email"
                placeholder="alex@example.com"
                type="email"
                value={values.email}
                error={errors.email}
                onChange={updateField}
              />
              <div className="field">
                <div className="password-row">
                  <label htmlFor="password">Password</label>
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}{" "}
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>
                <input
                  className={errors.password ? "input-error" : ""}
                  id="password"
                  name="password"
                  placeholder="At least 8 characters"
                  type={showPassword ? "text" : "password"}
                  value={values.password}
                  onChange={updateField}
                />
                {errors.password && (
                  <span className="error-text">{errors.password}</span>
                )}
              </div>
              <label className="terms">
                <input
                  checked={values.consent}
                  name="consent"
                  onChange={updateField}
                  type="checkbox"
                />
                <span>
                  I agree to the <a href="#terms">Terms of Service</a> and{" "}
                  <a href="#privacy">Privacy Policy</a>.
                </span>
              </label>
              {errors.consent && (
                <span className="error-text">{errors.consent}</span>
              )}
              {submitError && <span className="error-text">{submitError}</span>}
              <button className="primary-button form-submit" type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Creating account..." : "Create account"} <ArrowRight size={16} />
              </button>
              <div className="form-divider">or</div>
              <button className="outline-button google-button" type="button">
                <span className="google-dot" />
                Continue with Google
              </button>
            </form>
          )}
        </div>
      </section>
    </main>
  );
}

function Field({ label, name, type = "text", error, ...props }) {
  return (
    <div className="field">
      <label htmlFor={name}>{label}</label>
      <input
        className={error ? "input-error" : ""}
        id={name}
        name={name}
        type={type}
        {...props}
      />
      {error && <span className="error-text">{error}</span>}
    </div>
  );
}
function SuccessState() {
  return (
    <div className="success-state">
      <div className="success-icon">
        <Check size={23} />
      </div>
      <h3>You’re all set.</h3>
      <p>
        Your Havenly account is ready. Welcome to a clearer view of property.
      </p>
      <Link className="primary-button" to="/">
        Return home <ArrowRight size={16} />
      </Link>
    </div>
  );
}
