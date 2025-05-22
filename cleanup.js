function cleanUpDivs() {
    console.log("%cInjected script cleanUpDivs running...", "font-size: 24px");

    const targetDiv = document.querySelector('div.chat-scrollable-area__message-container[data-test-selector="chat-scrollable-area__message-container"][role="log"]');
    
    if (!targetDiv) {
        console.warn('Target div not found.');
        return;
    }

    // Create a Set of elements to **keep**
    const excludedDivs = new Set();
    
    // Add target div
    excludedDivs.add(targetDiv);

    // Add all children of target div
    targetDiv.querySelectorAll('div').forEach(child => excludedDivs.add(child));

    // Add all parent elements up to <html>
    let parent = targetDiv.parentElement;
    while (parent) {
        excludedDivs.add(parent);
        parent = parent.parentElement;
    }

    // Handle the chat welcome message removal
    document.querySelectorAll('div[data-a-target="chat-welcome-message"]').forEach(welcomeDiv => {
        const parentDiv = welcomeDiv.closest('div'); // Get first parent div
        const siblingDiv = parentDiv?.nextElementSibling; // Get following sibling div

        // Remove the welcome message div
        welcomeDiv.remove();

        // Remove parent div (if found)
        if (parentDiv) parentDiv.remove();

        // Remove the sibling div (if found)
        if (siblingDiv && siblingDiv.tagName === 'DIV') siblingDiv.remove();
    });

    // Remove all divs that are **not** in excludedDivs
    document.querySelectorAll('div').forEach(div => {
        if (!excludedDivs.has(div)) {
            div.remove();
        }
    });

    console.log('Cleanup complete.');
}

// Run the function
cleanUpDivs();
