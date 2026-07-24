import React from "react";
import { Link } from "react-router-dom";
import LoginForm from "../components/LoginForm";
import "../styles/login.css";

const Login = () => {
  return (
    <div className="login-page">
      {/* Left Section */}
      <div className="login-left">
        <div className="overlay"></div>

        <div className="brand-content">
          <Link to="/" className="logo">
            <span className="terra">Terra</span>
            <span className="pulse">Pulse</span>
          </Link>

          <h1>Welcome Back</h1>

          <p>
            Sign in to access AI-powered property insights, neighbourhood
            analytics, and personalized recommendations.
          </p>

          <div className="feature-list">
            <div className="feature">
              <span>📍</span>
              <p>Explore smarter property searches</p>
            </div>

            <div className="feature">
              <span>📊</span>
              <p>View AI-generated neighbourhood scores</p>
            </div>

            <div className="feature">
              <span>🤖</span>
              <p>Receive personalized recommendations</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Section */}
      <div className="login-right">
        <div className="login-card">
          <h2>Sign In</h2>

          <p className="subtitle">
            Enter your email and password to continue.
          </p>

          <LoginForm />

          <div className="signup-link">
            Don't have an account?{" "}
            <Link to="/register">Create Account</Link>
          </div>

          <div className="back-home">
            <Link to="/">← Back to Home</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;