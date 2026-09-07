import { CONFIG } from './config.js';

document.addEventListener('DOMContentLoaded', async () => {
    const statusDiv = document.getElementById('connection-status');
    
    try {
        // Ping the root of the FastAPI server to check if it's online
        const response = await fetch(`${CONFIG.API_BASE_URL}/`);
        const data = await response.json();
        
        if (data.status === "SYSTEM ONLINE") {
            statusDiv.textContent = "🟢 Backend Online";
            statusDiv.className = "status online";
        } else {
            throw new Error("Invalid response");
        }
    } catch (error) {
        statusDiv.textContent = "🔴 Backend Offline";
        statusDiv.className = "status offline";
    }
});
