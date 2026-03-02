import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabaseClient } from "../lib/supabaseClient";
import { useAuth } from "../contexts/AuthContext";
import "../components/auth/auth.css";

/**
 * OAuth callback: Supabase redirects here after Google/Microsoft sign-in.
 * We read the session from the URL (detectSessionInUrl) and getSession().
 * Session is in memory only (persistSession: false). We set user in AuthContext
 * and redirect to dashboard. Refresh or restart = logged out (no persistence).
 */
export default function AuthCallback() {
  const nav = useNavigate();
  const { setUserFromOAuth } = useAuth();
  const [status, setStatus] = useState("Signing you in…");

  useEffect(() => {
    let cancelled = false;

    async function handleCallback() {
      try {
        // Session may be in URL hash; Supabase parses it with detectSessionInUrl.
        // getSession() reads from in-memory state. Retry once after short delay
        // in case the client is still processing the hash.
        let { data: { session } } = await supabaseClient.auth.getSession();
        if (!session?.user) {
          await new Promise((r) => setTimeout(r, 400));
          if (cancelled) return;
          const result = await supabaseClient.auth.getSession();
          session = result.data.session;
        }

        if (cancelled) return;
        if (session?.user) {
          setUserFromOAuth(session.user);
          setStatus("Redirecting to dashboard…");
          nav("/", { replace: true });
        } else {
          setStatus("No session found.");
          nav("/signin", { replace: true });
        }
      } catch {
        if (!cancelled) {
          setStatus("Something went wrong.");
          nav("/signin", { replace: true });
        }
      }
    }

    handleCallback();
    return () => { cancelled = true; };
  }, [nav, setUserFromOAuth]);

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <p className="auth-sub" style={{ marginTop: "1rem" }}>{status}</p>
      </div>
    </div>
  );
}
