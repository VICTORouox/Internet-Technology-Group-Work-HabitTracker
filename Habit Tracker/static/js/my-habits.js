/* ---------- Global State ---------- */
let currentHabitId = null;
let checkinSet = new Set();
let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth();
let analysisChart;
let currentAnalysisView = "monthly";

/* ---------- Utilities ---------- */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

/* ---------- Calendar ---------- */
async function openCalendar(habitId) {
    currentHabitId = habitId;
    try {
        const res = await fetch(`/calendar/${habitId}/`);
        if (!res.ok) throw new Error('Failed to load checkin data');
        const data = await res.json();
        checkinSet = new Set(data.checkins);
        
        const today = new Date();
        currentYear = today.getFullYear();
        currentMonth = today.getMonth();
        
        renderCalendar();
        document.getElementById("calendarOverlay").style.display = "flex";
        document.getElementById("calendarOverlay").setAttribute('aria-hidden', 'false');
    } catch (err) {
        alert('Error loading calendar: ' + err.message);
    }
}

function closeCalendar() {
    document.getElementById("calendarOverlay").style.display = "none";
    document.getElementById("calendarOverlay").setAttribute('aria-hidden', 'true');
}

function renderCalendar() {
    const grid = document.getElementById("calendarGrid");
    grid.innerHTML = "";
    
    const daysInMonth = new Date(
        currentYear,
        currentMonth + 1,
        0
    ).getDate();
    
    for (let i = 1; i <= daysInMonth; i++) {
        const date = new Date(currentYear, currentMonth, i);
        const dateStr = date.toISOString().split("T")[0];
        
        const div = document.createElement("div");
        div.className = "calendar-day";
        div.tabIndex = 0; // Accessibility: Supports keyboard focus
        div.setAttribute('role', 'button'); // Accessibility: Mark as Button
        div.setAttribute('aria-label', `${dateStr} - ${checkinSet.has(dateStr) ? 'Checked in' : 'Not checked in'}`);
        
        if (checkinSet.has(dateStr)) {
            div.classList.add("checked");
        }
        
        div.innerText = i;
        div.addEventListener('click', () => checkInDate(dateStr));
        // Accessibility: Triggered by keyboard Enter/Spacebar
        div.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                checkInDate(dateStr);
                e.preventDefault();
            }
        });
        
        grid.appendChild(div);
    }
    
    updateMonthTitle();
}

async function checkInDate(dateStr) {
    try {
        const res = await fetch(`/checkin/${currentHabitId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ date: dateStr })
        });
        
        if (!res.ok) throw new Error('Check-in failed');
        const data = await res.json();
        
        if (data.status === "success") {
            checkinSet.add(dateStr);
            renderCalendar();
        }
    } catch (err) {
        alert('Error checking in: ' + err.message);
    }
}

function updateMonthTitle() {
    const months = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ];
    document.getElementById("calendarMonth").innerText =
        months[currentMonth] + " " + currentYear;
}

function prevMonth() {
    currentMonth--;
    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    }
    renderCalendar();
}

function nextMonth() {
    currentMonth++;
    if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    }
    renderCalendar();
}

/* ---------- Analysis ---------- */
function openAnalysis(habitId){
    currentHabitId = habitId;
    document.getElementById("analysisOverlay").style.display = "flex";
    document.getElementById("analysisOverlay").setAttribute('aria-hidden', 'false');
    switchView("monthly");
}

function closeAnalysis(){
    document.getElementById("analysisOverlay").style.display = "none";
    document.getElementById("analysisOverlay").setAttribute('aria-hidden', 'true');
}

function loadAnalysisChart(habitId, view="monthly", month=null){
    const url = new URL(`/analysis/${habitId}/`, window.location.origin);
    url.searchParams.set("view", view);
    if(month !== null){
        url.searchParams.set("month", month);
    }
    
    fetch(url)
        .then(res => {
            if (!res.ok) throw new Error('Failed to load analysis data');
            return res.json();
        })
        .then(data => {
            const ctx = document.getElementById("analysisChart");
            if (analysisChart) {
                analysisChart.destroy();
            }
            
            analysisChart = new Chart(ctx, {
                type: "line",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: "Duration (minutes)",
                        data: data.data,
                        borderColor: "#6c5ce7",
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        })
        .catch(err => {
            alert('Error loading analysis: ' + err.message);
        });
}

function switchView(view){
    currentAnalysisView = view;
    document.getElementById("monthFilter").style.display =
        view === "monthly" ? "block" : "none";
    
    document.querySelectorAll(".view-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.view === view);
    });
    
    const habitId = currentHabitId;
    const month =
        view === "monthly"
        ? document.getElementById("monthSelect").value
        : null;
    
    loadAnalysisChart(habitId, view, month);
}

function loadMonthlyChart(){
    const habitId = currentHabitId;
    const month = parseInt(
        document.getElementById("monthSelect").value
    );
    loadAnalysisChart(habitId, "monthly", month);
}

/* ---------- Page Init & Event Binding ---------- */
document.addEventListener('DOMContentLoaded', function() {
    
    // Check In Button
    document.querySelectorAll('.btn-primary[data-habit-id]').forEach(btn => {
        const habitId = btn.dataset.habitId;
        btn.addEventListener('click', () => openCalendar(habitId));
        // Accessibility: Triggered by keyboard Enter/Spacebar
        btn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                openCalendar(habitId);
                e.preventDefault();
            }
        });
    });

    // Analysis Button
    document.querySelectorAll('.btn-info[data-habit-id]').forEach(btn => {
        const habitId = btn.dataset.habitId;
        btn.addEventListener('click', () => openAnalysis(habitId));
        // Accessibility: Triggered by keyboard Enter/Spacebar
        btn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                openAnalysis(habitId);
                e.preventDefault();
            }
        });
    });

    document.querySelectorAll('.delete-form').forEach(form => {
        form.addEventListener('submit', (e) => {
            const confirmDelete = confirm('Are you sure you want to delete this habit?');
            if (!confirmDelete) e.preventDefault();
        });
    });
    
    document.querySelector('.calendar-close')?.addEventListener('click', closeCalendar);
    document.querySelector('.calendar-header button:first-child')?.addEventListener('click', prevMonth);
    document.querySelector('.calendar-header button:last-child')?.addEventListener('click', nextMonth);
    
    document.querySelector('.analysis-close')?.addEventListener('click', closeAnalysis);
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            switchView(btn.dataset.view);
        });
    });
    document.getElementById('monthSelect')?.addEventListener('change', loadMonthlyChart);
    
    // Accessibility: Supports keyboard operation
    const calendarClose = document.querySelector('.calendar-close');
    const analysisClose = document.querySelector('.analysis-close');
    if (calendarClose) {
        calendarClose.tabIndex = 0;
        calendarClose.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                closeCalendar();
                e.preventDefault();
            }
        });
    }
    if (analysisClose) {
        analysisClose.tabIndex = 0;
        analysisClose.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                closeAnalysis();
                e.preventDefault();
            }
        });
    }
    
    // Page initialization prompt
    if (window.location.search.includes('created=1')) {
        alert("Habit created successfully!");
        window.history.replaceState(
            {},
            document.title,
            window.location.pathname
        );
    }
});