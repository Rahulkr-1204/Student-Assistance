import { useState } from "react";
import { useNavigate } from "react-router-dom";
import BackgroundSlider from "../Background/BackgroundSlider";
import { forgotPassword, getApiErrorMessage, loginUser, resetPassword } from "../../services/api";
import "./Auth.css";

function Login() {

  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showForgot, setShowForgot] = useState(false);
  const [forgotIdentifier, setForgotIdentifier] = useState("");
  const [resetToken, setResetToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [forgotMessage, setForgotMessage] = useState("");
  const [forgotLoading, setForgotLoading] = useState(false);

  const toggleForgotPassword = () => {
    setShowForgot((previous) => {
      const next = !previous;
      if (next && !forgotIdentifier.trim() && identifier.trim()) {
        setForgotIdentifier(identifier.trim());
      }
      if (!next) {
        setForgotMessage("");
        setResetToken("");
        setNewPassword("");
      }
      return next;
    });
  };

  const handleLogin = async () => {
  console.log("LOGIN CLICKED"); // 🔥 DEBUG

  if (!identifier || !password) {
    console.log("Missing fields");
    setError("Please enter email/registration number and password");
    return;
  }

  try {
    setLoading(true);
    setError("");

    console.log("Calling API...");

    const res = await loginUser({ identifier, password });

    console.log("API RESPONSE:", res);

    localStorage.setItem("loggedInUser", JSON.stringify(res.data.user));
    navigate("/chat");
  } catch (err) {
    console.log("ERROR:", err); // 🔥 VERY IMPORTANT
    setError(getApiErrorMessage(err, "Login failed"));
  } finally {
    setLoading(false);
  }
};

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleLogin();
    }
  };

  const handleForgotPassword = async () => {
    if (!forgotIdentifier.trim()) {
      setForgotMessage("Enter your email or registration number first");
      return;
    }
    try {
      setForgotLoading(true);
      setForgotMessage("");
      const res = await forgotPassword(forgotIdentifier.trim());
      if (res.data?.reset_token) {
        setForgotMessage(
          `Your 6-digit reset code is ${res.data.reset_token}. It is valid for ${res.data?.expires_in_minutes || 20} minutes. Enter it below to set a new password.`
        );
      } else {
        setForgotMessage(
          res.data?.message || "If your account exists, a 6-digit reset code has been sent to your email."
        );
      }
    } catch (err) {
      setForgotMessage(getApiErrorMessage(err, "Failed to generate reset token"));
    } finally {
      setForgotLoading(false);
    }
  };

  const handleResetPassword = async () => {
    if (!forgotIdentifier.trim() || !resetToken.trim() || !newPassword.trim()) {
      setForgotMessage("Enter identifier, reset token and new password");
      return;
    }
    if (newPassword.trim().length < 6) {
      setForgotMessage("New password must be at least 6 characters");
      return;
    }

    try {
      setForgotLoading(true);
      setForgotMessage("");
      const res = await resetPassword({
        identifier: forgotIdentifier.trim(),
        reset_token: resetToken.trim(),
        new_password: newPassword,
      });
      setForgotMessage(res.data?.message || "Password reset successful");
      setPassword("");
      setResetToken("");
      setNewPassword("");
      setIdentifier(forgotIdentifier.trim());
    } catch (err) {
      setForgotMessage(getApiErrorMessage(err, "Password reset failed"));
    } finally {
      setForgotLoading(false);
    }
  };

  return (
    <>
      <BackgroundSlider />
      <div className="auth-shell">
        <div className="auth-box">
          <h2 className="auth-title">Student Support System</h2>
          <p className="auth-subtitle">Sign in to continue</p>

          {error && <p className="error">{error}</p>}

          <input
            placeholder="Email or Registration Number"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={handleKeyDown}
          />

          <button onClick={handleLogin} disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>

          <button type="button" className="auth-link-secondary" onClick={toggleForgotPassword}>
            {showForgot ? "Hide Forgot Password" : "Forgot Password?"}
          </button>

          {showForgot && (
            <div className="forgot-box">
              <input
                placeholder="Email or Registration Number"
                value={forgotIdentifier}
                onChange={(e) => setForgotIdentifier(e.target.value)}
              />
              <div className="forgot-actions">
                <button type="button" onClick={handleForgotPassword} disabled={forgotLoading}>
                  {forgotLoading ? "Processing..." : "Get Reset Code"}
                </button>
              </div>

              <input
                placeholder="6-digit Reset Code"
                value={resetToken}
                onChange={(e) => setResetToken(e.target.value)}
              />
              <input
                type="password"
                placeholder="New Password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
              <p className="auth-hint">New password must be at least 6 characters.</p>
              <div className="forgot-actions">
                <button type="button" onClick={handleResetPassword} disabled={forgotLoading}>
                  {forgotLoading ? "Processing..." : "Reset Password"}
                </button>
              </div>
              {forgotMessage && <p className="auth-hint">{forgotMessage}</p>}
            </div>
          )}

          <p className="auth-switch">
            New user?{" "}
            <button type="button" className="auth-link" onClick={() => navigate("/signup")}>
              Create Account
            </button>
          </p>
        </div>
      </div>
    </>
  );
}

export default Login;
