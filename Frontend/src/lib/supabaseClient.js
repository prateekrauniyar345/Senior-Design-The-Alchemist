/**
 * Supabase client for OAuth only.
 * Uses in-memory session only: no persistence across refresh or dev-server restart.
 * Do NOT use localStorage/sessionStorage for auth.
 *
 * Requires VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in .env or .env.local.
 * Restart the dev server (npm run dev) after changing env files.
 */
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnon = import.meta.env.VITE_SUPABASE_ANON_KEY;

const hasUrl = Boolean(supabaseUrl?.trim());
const hasKey = Boolean(supabaseAnon?.trim());

if (!hasUrl || !hasKey) {
  const msg =
    "Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY. Create .env.local (or .env) in the Frontend folder, add both variables, then restart npm run dev.";
  console.error(msg);
  throw new Error(msg);
}

if (import.meta.env.DEV) {
  console.debug("Supabase env loaded: URL ✅ KEY ✅");
}

export const supabaseClient = createClient(supabaseUrl, supabaseAnon, {
  auth: {
    persistSession: false,
    autoRefreshToken: false,
    detectSessionInUrl: true,
  },
});
