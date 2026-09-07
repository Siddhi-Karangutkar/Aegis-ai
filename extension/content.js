// Store the last highlighted selection range
let lastRange = null;

document.addEventListener("selectionchange", () => {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        lastRange = selection.getRangeAt(0);
    }
});

let currentBadge = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "showLoading") {
        if (!lastRange) return;

        // Remove old badge if exists
        if (currentBadge) currentBadge.remove();

        currentBadge = document.createElement("span");
        currentBadge.className = "aegis-badge loading";
        currentBadge.innerText = "AEGIS: Scanning...";
        
        // Insert right after the highlighted text
        const rect = lastRange.getBoundingClientRect();
        
        // In this simple version, we'll just collapse the range to the end and insert the node
        const endRange = lastRange.cloneRange();
        endRange.collapse(false);
        endRange.insertNode(currentBadge);
    }

    if (request.action === "showResult" && currentBadge) {
        const { result } = request;
        const sev = result.severity ? result.severity.toLowerCase() : 'low';
        
        currentBadge.className = `aegis-badge ${sev}`;
        currentBadge.innerText = `AEGIS: ${result.verdict} (${result.threat_score}/100)`;

        // Build the tooltip
        const tooltip = document.createElement("div");
        tooltip.className = "aegis-tooltip";
        
        let flagsHtml = "";
        if (result.flagged_phrases && result.flagged_phrases.length > 0) {
            flagsHtml = result.flagged_phrases.map(f => `
                <div class="aegis-flag-item ${f.level}">
                    <span class="aegis-flag-word">"${f.text}"</span>
                    <span class="aegis-flag-reason">${f.reason}</span>
                </div>
            `).join("");
        } else {
            flagsHtml = `<div class="aegis-flag-item"><span class="aegis-flag-reason">No specific threat patterns detected.</span></div>`;
        }

        tooltip.innerHTML = `
            <div class="aegis-tooltip-header">
                <span class="aegis-tooltip-title">${result.verdict} DETECTED</span>
                <span class="aegis-tooltip-score">Score: ${result.threat_score}</span>
            </div>
            ${flagsHtml}
            <div class="aegis-action">${result.recommended_action || 'Proceed with normal caution.'}</div>
        `;

        document.body.appendChild(tooltip);

        currentBadge.addEventListener('mouseenter', () => {
            tooltip.style.display = 'block';
            const rect = currentBadge.getBoundingClientRect();
            // Position above the badge, accounting for scrolling
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
            tooltip.style.left = (rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)) + 'px';
        });

        currentBadge.addEventListener('mouseleave', () => {
            tooltip.style.display = 'none';
        });
    }

    if (request.action === "showError" && currentBadge) {
        currentBadge.className = "aegis-badge crit";
        currentBadge.innerText = `AEGIS: Connection Error`;
        currentBadge.title = request.error;
    }
});
