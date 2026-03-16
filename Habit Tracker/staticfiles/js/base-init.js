// Initialize Lucide icons on page load
function initializeLucideIcons() {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// Scroll habits container left or right
function scrollHabits(direction) {
    const container = document.getElementById('habitContainer');
    if (!container) return;
    
    const scrollAmount = container.clientWidth / 3 + 20;

    if (direction === 'left') {
        container.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    } else {
        container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initializeLucideIcons);
