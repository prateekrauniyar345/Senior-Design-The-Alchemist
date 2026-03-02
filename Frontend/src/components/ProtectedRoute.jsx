import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

/**
 * Auth guard: do not redirect while booting; redirect to /login only when not booting and user is null.
 * Never set user=null or call logout here — navigation must not clear auth.
 */
export default function ProtectedRoute() {
  const { user, booting } = useAuth();

  if (booting) {
    return (
      <div className="d-flex align-items-center justify-content-center min-vh-100">
        <div className="spinner-border text-light" role="status">
          <span className="visually-hidden">Loading…</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
