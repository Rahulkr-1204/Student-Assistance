import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  adminForgotPassword,
  adminLogin,
  adminResetPassword,
  getApiErrorMessage,
} from "../../services/api";
import "./Admin.css";

function AdminLogin() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
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
      if (next && !forgotIdentifier.trim() && username.trim()) {
        setForgotIdentifier(username.trim());
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
    if (!username || !password) {
      setError("Please enter username and password");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const res = await adminLogin({ username, password });
      localStorage.setItem("admin", JSON.stringify(res.data.admin));
      if (res.data.token) {
        localStorage.setItem("adminToken", res.data.token);
      }
      navigate("/admin/dashboard");
    } catch (err) {
      setError(getApiErrorMessage(err, "Admin login failed"));
    } finally {
      setLoading(false);
    }
  };

  const onEnter = (e) => {
    if (e.key === "Enter") {
      handleLogin();
    }
  };

  const handleForgotPassword = async () => {
    if (!forgotIdentifier.trim()) {
      setForgotMessage("Enter your admin username or email first");
      return;
    }

    try {
      setForgotLoading(true);
      setForgotMessage("");
      const res = await adminForgotPassword(forgotIdentifier.trim());
      if (res.data?.reset_token) {
        setForgotMessage(
          `Your 6-digit reset code is ${res.data.reset_token}. It is valid for ${res.data?.expires_in_minutes || 20} minutes. Enter it below to set a new password.`
        );
      } else {
        setForgotMessage(
          res.data?.message || "If account exists, a 6-digit reset code has been sent to admin email."
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
      const res = await adminResetPassword({
        identifier: forgotIdentifier.trim(),
        reset_token: resetToken.trim(),
        new_password: newPassword,
      });
      setForgotMessage(res.data?.message || "Admin password reset successful");
      setPassword("");
      setResetToken("");
      setNewPassword("");
      setUsername(forgotIdentifier.trim());
    } catch (err) {
      setForgotMessage(getApiErrorMessage(err, "Admin password reset failed"));
    } finally {
      setForgotLoading(false);
    }
  };

  return (
    <div className="admin-login-page">
      <div className="admin-login-card">
        <h1>Admin Console</h1>
        <p>Sign in to manage users, intents and analytics.</p>

        {error && <p className="error">{error}</p>}

        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          onKeyDown={onEnter}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={onEnter}
        />

        <button onClick={handleLogin} disabled={loading}>
          {loading ? "Signing in..." : "Sign In"}
        </button>

        <button type="button" className="muted-btn" onClick={toggleForgotPassword}>
          {showForgot ? "Hide Forgot Password" : "Forgot Password?"}
        </button>

        {showForgot && (
          <div className="forgot-box">
            <input
              placeholder="Admin Username or Email"
              value={forgotIdentifier}
              onChange={(e) => setForgotIdentifier(e.target.value)}
            />
            <div className="forgot-actions">
              <button type="button" className="admin-btn" onClick={handleForgotPassword} disabled={forgotLoading}>
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
            <p className="form-note">New password must be at least 6 characters.</p>
            <div className="forgot-actions">
              <button type="button" className="admin-btn" onClick={handleResetPassword} disabled={forgotLoading}>
                {forgotLoading ? "Processing..." : "Reset Password"}
              </button>
            </div>
            {forgotMessage && <p className="form-note">{forgotMessage}</p>}
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminLogin;
