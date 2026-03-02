export async function parseJsonOrText(res) {
    const text = await res.text();
    let data = {};
    try { data = text ? JSON.parse(text) : {}; }
    catch { data = { detail: text }; }
  
    if (!res.ok) {
      const msg = data.message || data.detail || `Request failed (${res.status})`;
      throw new Error(msg);
    }
    return data;
  }