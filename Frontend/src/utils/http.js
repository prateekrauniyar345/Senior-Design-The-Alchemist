/**
 * Safely parse a fetch Response.
 *
 * This helper:
 * 1. Reads response as text first (prevents JSON crash)
 * 2. Attempts to parse JSON safely
 * 3. Normalizes error messages
 * 4. Throws a clean JS Error if response is not OK
 */
export async function parseJsonOrText(res) {

    // Read the response body as raw text
    // This avoids crashing if response is not valid JSON
    const text = await res.text();
  
    let data = {};
  
    try {
      // Try parsing JSON if text exists
      data = text ? JSON.parse(text) : {};
    }
    catch {
      // If JSON parsing fails,
      // fallback to wrapping raw text inside an object
      data = { detail: text };
    }
  
    // If HTTP status is not 2xx (res.ok === false),
    // throw a meaningful error
    if (!res.ok) {
  
      // Try extracting a clean error message
      const msg =
        data.message ||        // custom backend message
        data.detail ||         // FastAPI HTTPException detail
        `Request failed (${res.status})`;  // fallback
  
      throw new Error(msg);
    }
  
    // Return parsed JSON (or empty object)
    return data;
  }