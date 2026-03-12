// Initialize global variables
var candidates = [];
var currentIndex = 0;

// Initialization data
function initCandidates(data) {
    candidates = data || [];
    // Handle empty data to prevent JavaScript errors
    if (candidates.length === 0) {
        renderEmptyState();
        return;
    }
    // Render the first recommended item initially
    renderHabit(currentIndex);
}

// Render recommended content
function renderHabit(index) {
    if (!candidates || candidates.length === 0) return;

    // Boundary handling: Preventing index out-of-bounds errors
    index = index % candidates.length;
    const data = candidates[index];

    // Dynamically update DOM content
    document.getElementById('matchPercent').innerText = data.match || 0;
    document.getElementById('sportIcon').innerText = data.icon || '';
    document.getElementById('sportName').innerText = data.name || 'No recommendation';
    document.getElementById('typeTag').innerText = data.type || 'Uncategorized';
    document.getElementById('reasonText').innerText = data.reason || 'No matching reason';
    document.getElementById('sessionTime').innerText = data.plan || 'No plan';
    document.getElementById('upgradeDesc').innerText = data.upgrade || 'No growth path';

    // Set hidden form values
    document.getElementById('hiddenHabitName').value = data.name || '';
    document.getElementById('hiddenDuration').value = data.plan || '';
    document.getElementById('hiddenSportType').value = data.type || '';
}

// Switch recommendation options
function switchHabit() {
    if (!candidates || candidates.length === 0) return;
    currentIndex = (currentIndex + 1) % candidates.length;
    renderHabit(currentIndex);
}

// Handle the empty state with no recommended results
function renderEmptyState() {
    document.getElementById('matchPercent').innerText = 0;
    document.getElementById('sportName').innerText = 'No suitable recommendations';
    document.getElementById('typeTag').innerText = 'No data';
    document.getElementById('reasonText').innerText = 'We could not find any suitable exercise recommendations based on your input. Please try adjusting your preferences.';
    document.getElementById('sessionTime').innerText = '—';
    document.getElementById('upgradeDesc').innerText = '—';
    // Disable the toggle button and the submit button
    const switchBtn = document.querySelector('.btn-secondary');
    const submitBtn = document.querySelector('.btn-primary');
    if (switchBtn) switchBtn.disabled = true;
    if (submitBtn) submitBtn.disabled = true;
}

// Error handling logic
function handlePageError(errorMsg) {
    if (errorMsg) {
        alert(errorMsg);
        if (window.history.length > 1) {
            window.history.back();
        } else {
            window.location.href = "/dashboard/"; // 替换成你项目中main_dashboard对应的实际URL
        }
    }
}

// Page initialization (binding events + rendering data)
document.addEventListener('DOMContentLoaded', function() {
    const switchBtn = document.querySelector('.btn-secondary');
    if (switchBtn) {
        switchBtn.addEventListener('click', switchHabit);
        switchBtn.addEventListener('keydown', function(e) {
            // 【修改点3】Tab键改为Enter键（Tab是切换焦点，不该触发点击）
            if (e.key === 'Enter' || e.key === ' ') {
                switchHabit();
                e.preventDefault();
            }
        });
    }

    if (window.pageErrorMsg) {
        handlePageError(window.pageErrorMsg);
    }
});