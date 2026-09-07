import { CONFIG } from './config.js';

// Create a context menu when the extension is installed
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "scanWithAegis",
        title: "Scan with AEGIS.AI",
        contexts: ["selection"]
    });
});

// Listen for the context menu click
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    if (info.menuItemId === "scanWithAegis") {
        const selectedText = info.selectionText;
        
        // Let the content script know we are analyzing
        chrome.tabs.sendMessage(tab.id, {
            action: "showLoading",
            text: selectedText
        });

        try {
            // Send the selected text to our local FastAPI backend
            const response = await fetch(`${CONFIG.API_BASE_URL}/analyze/phishing`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ text: selectedText })
            });

            const result = await response.json();
            
            // Send the result back to the content script so it can draw the badge
            chrome.tabs.sendMessage(tab.id, {
                action: "showResult",
                result: result,
                text: selectedText
            });

        } catch (error) {
            console.error("AEGIS Error:", error);
            chrome.tabs.sendMessage(tab.id, {
                action: "showError",
                error: "Could not connect to AEGIS.AI Backend. Is it running?"
            });
        }
    }
});
