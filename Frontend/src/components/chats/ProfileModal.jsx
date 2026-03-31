import React, { useState, useEffect, useCallback } from "react";
import { X, Upload, User as UserIcon } from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { parseJsonOrText } from "../../utils/http";
import "./ProfileModal.css";

const API = import.meta.env.VITE_API_URL;

const ProfileModal = ({ isOpen, onClose }) => {
  const { user, logout, refreshMe, updateUser } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ name: "", email: "" });
  const [previewImage, setPreviewImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: null, text: "" });

  const fetchProfile = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/auth/profile`, { credentials: "include" });
      const data = await parseJsonOrText(res);
      setFormData({ name: data.name || "", email: data.email || "" });
    } catch (err) {
      setFormData({ name: user?.name || "", email: user?.email || "" });
    }
  }, [user?.name, user?.email]);

  useEffect(() => {
    if (isOpen) {
      setMessage({ type: null, text: "" });
      if (user?.email) {
        setFormData({ name: user.name || "", email: user.email || "" });
        fetchProfile();
      }
    }
  }, [isOpen, user?.email, fetchProfile]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setPreviewImage(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    setMessage({ type: null, text: "" });
    try {
      const res = await fetch(`${API}/api/auth/profile`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ name: formData.name.trim() }),
      });
      const data = await parseJsonOrText(res);
      updateUser({ name: data.name });
      setFormData((prev) => ({ ...prev, name: data.name }));
      setMessage({ type: "success", text: "Profile updated successfully." });
      await refreshMe();
    } catch (err) {
      setMessage({ type: "error", text: err.message || "Failed to update profile." });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="profile-modal" onClick={(e) => e.stopPropagation()}>
        <div className="profile-modal-header">
          <h2 className="profile-modal-title">Profile Settings</h2>
          <button className="profile-close-btn" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </div>

        <div className="profile-modal-body">
          {/* Profile Picture Section */}
          <div className="profile-picture-section">
            <div className="profile-picture-container">
              {previewImage ? (
                <img src={previewImage} alt="Profile" className="profile-picture" />
              ) : (
                <div className="profile-picture-placeholder">
                  <UserIcon size={48} />
                </div>
              )}
            </div>
            <div className="profile-picture-actions">
              <label htmlFor="profile-upload" className="upload-btn">
                <Upload size={16} />
                Upload Photo
              </label>
              <input
                id="profile-upload"
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="d-none"
              />
              {previewImage && (
                <button className="remove-btn" onClick={() => setPreviewImage(null)}>
                  Remove
                </button>
              )}
            </div>
          </div>

          {/* Form Fields */}
          <div className="profile-form">
            {message.text && (
              <div className={`profile-message profile-message-${message.type}`}>
                {message.text}
              </div>
            )}
            <div className="form-group">
              <label htmlFor="name">Name</label>
              <input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                className="form-control"
                placeholder="Enter your name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                readOnly
                className="form-control form-control-readonly"
                placeholder="Enter your email"
              />
            </div>
          </div>
        </div>

        <div className="profile-modal-footer">
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
          <div className="action-buttons">
            <button className="cancel-btn" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button className="save-btn" onClick={handleSave} disabled={loading}>
              {loading ? "Saving…" : "Save Changes"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileModal;
