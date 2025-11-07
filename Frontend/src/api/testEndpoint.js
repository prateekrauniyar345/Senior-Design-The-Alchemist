// testBackendHealth.js
export async function testBackendHealth() {
  try {
    const response = await fetch("/api/health"); 
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    console.log("Backend Health:", data);
    return data;
  } catch (err) {
    console.error("Error testing backend health:", err);
  }
}
