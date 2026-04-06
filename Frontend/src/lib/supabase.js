import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnon = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnon, {
  auth: {
    // Production: persist Supabase session. Dev: no persistence (refresh = clean slate).
    persistSession: !import.meta.env.DEV,
    autoRefreshToken: !import.meta.env.DEV,
    detectSessionInUrl: true,
  },
});
