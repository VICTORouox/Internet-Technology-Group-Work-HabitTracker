let currentHabitId = null;

function openCalendar(habitId) {

    currentHabitId = habitId;

    fetch(calendarUrl.replace("0", habitId))
        .then(response => response.json())
        .then(data => {

            renderCalendar(data);

            const modal = document.getElementById("calendarModal");
            if (modal) {
                modal.style.display = "flex";
            }

        })
        .catch(error => {
            console.error("Calendar load error:", error);
        });
}


function closeCalendar() {
    const modal = document.getElementById("calendarModal");
    if (modal) {
        modal.style.display = "none";
    }
}


function renderCalendar(data) {

    const container = document.getElementById("calendarDays");
    if (!container) return;

    container.innerHTML = "";

    const checkedDates = data.checkins || [];

    for (let i = 0; i < 30; i++) {

        const date = new Date();
        date.setDate(date.getDate() - i);

        const dateStr = date.toISOString().split("T")[0];

        const day = document.createElement("div");
        day.classList.add("calendar-day");
        day.innerText = date.getDate();

        if (checkedDates.includes(dateStr)) {
            day.classList.add("checked");
        }

        day.onclick = () => checkinDay(dateStr);

        container.appendChild(day);
    }
}


function checkinDay(day) {

    fetch(`/checkin/${currentHabitId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
            date: day
        })
    })
    .then(res => res.json())
    .then(data => {

        if (data.status === "success") {
            openCalendar(currentHabitId);
        }

    })
    .catch(error => {
        console.error("Checkin error:", error);
    });
}


function getCSRFToken() {

    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {

        const c = cookie.trim();

        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length);
        }
    }

    return "";
}