import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../../lib/supabase";

export default function AuthCallback() {
  const nav = useNavigate();

  useEffect(() => {
    // Supabase parses the URL hash and stores the session automatically.
    // We just wait a tick and go somewhere nice.
    (async () => {
      // optional: verify we really have a session
      const { data: { session } } = await supabase.auth.getSession();
      nav(session ? "/dashboard" : "/login", { replace: true });
    })();
  }, [nav]);

  return <div style={{padding:24}}>Signing you in…</div>;
}
