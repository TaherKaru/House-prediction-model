import { ArrowLeft, ArrowRight, Check, Eye, EyeOff } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Brand from "../components/Brand";
import { apiRequest } from "../lib/api";

const initialValues = { email: "", password: "", remember: false };

export default function LoginPage() {
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

  async function handleSubmit(event) {
    event.preventDefault();
    const nextErrors = {};
    if (!/^\S+@\S+\.\S+$/.test(values.email)) {
      nextErrors.email = "Enter a valid email address.";
    }
    if (!values.password) nextErrors.password = "Enter your password.";
    setErrors(nextErrors);
    setSubmitError("");

    if (Object.keys(nextErrors).length) return;

    try {
      setIsSubmitting(true);
      const data = await apiRequest("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: values.email,
          password: values.password,
          remember: values.remember,
        }),
      });

      localStorage.setItem("token", data.access_token);
      setSubmitted(true);
      window.setTimeout(() => navigate("/"), 1200);
    } catch (error) {
      setSubmitError(error.message || "Unable to log in right now.");
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
          <h1>Every good property decision starts with a clearer view.</h1>
          <p>
            Welcome back. Your saved homes, valuations, and local insights are
            ready when you are.
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
                <h2>Welcome back</h2>
                <p className="form-intro">
                  New to Havenly? <Link to="/signup">Create an account</Link>
                </p>
              </div>
              <div className="field">
                <label htmlFor="email">Email address</label>
                <input
                  className={errors.email ? "input-error" : ""}
                  id="email"
                  name="email"
                  placeholder="alex@example.com"
                  type="email"
                  value={values.email}
                  onChange={updateField}
                />
                {errors.email && <span className="error-text">{errors.email}</span>}
              </div>
              <div className="field">
                <div className="password-row">
                  <label htmlFor="password">Password</label>
                  <button type="button" onClick={() => setShowPassword((show) => !show)}>
                    {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>
                <input
                  className={errors.password ? "input-error" : ""}
                  id="password"
                  name="password"
                  placeholder="Enter your password"
                  type={showPassword ? "text" : "password"}
                  value={values.password}
                  onChange={updateField}
                />
                {errors.password && <span className="error-text">{errors.password}</span>}
              </div>
              <div className="login-options">
                <label className="terms">
                  <input
                    checked={values.remember}
                    name="remember"
                    onChange={updateField}
                    type="checkbox"
                  />
                  <span>Remember me</span>
                </label>
                <a className="forgot-link" href="#reset-password">Forgot password?</a>
              </div>
              {submitError && <span className="error-text">{submitError}</span>}
              <button className="primary-button form-submit" type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Logging in..." : "Log in"} <ArrowRight size={16} />
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

function SuccessState() {
  return (
    <div className="success-state">
      <div className="success-icon"><Check size={23} /></div>
      <h3>You’re signed in.</h3>
      <p>Your saved property intelligence is ready to explore.</p>
      <Link className="primary-button" to="/">Explore Havenly <ArrowRight size={16} /></Link>
    </div>
  );
}
