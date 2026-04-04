// testBackendHealth.js
import apiClient from './apiClient';

export async function testBackendHealth() {
  try {
    const response = await apiClient.get("/api/health");
    console.log("Backend Health:", response.data);
    return response.data;
  } catch (err) {
    console.error("Error testing backend health:", err.message);
  }
}
