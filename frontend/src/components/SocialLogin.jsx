import React from "react";

const SocialLogin = () => {
  const handleGoogleLogin = () => {
    // TODO: Connect Google OAuth
    console.log("Google Login");
  };

  const handleGithubLogin = () => {
    // TODO: Connect GitHub OAuth
    console.log("GitHub Login");
  };

  return (
    <div className="social-login">
      <div className="divider">
        <span>OR</span>
      </div>

      <button
        type="button"
        className="social-btn google-btn"
        onClick={handleGoogleLogin}
      >
        <img
          src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/google/google-original.svg"
          alt="Google"
          className="social-icon"
        />
        Continue with Google
      </button>

      <button
        type="button"
        className="social-btn github-btn"
        onClick={handleGithubLogin}
      >
        <img
          src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg"
          alt="GitHub"
          className="social-icon"
        />
        Continue with GitHub
      </button>
    </div>
  );
};

export default SocialLogin;