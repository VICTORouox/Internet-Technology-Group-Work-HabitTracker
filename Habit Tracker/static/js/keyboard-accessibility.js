document.addEventListener("DOMContentLoaded", () => {

    document.addEventListener("keydown", (event) => {

        if (event.key !== "Escape") return;

        const calendar = document.getElementById("calendarOverlay");
        const analysis = document.getElementById("analysisOverlay");

        if (calendar && calendar.style.display !== "none") {
            closeCalendar();
        }

        if (analysis && analysis.style.display !== "none") {
            closeAnalysis();
        }

    });

});