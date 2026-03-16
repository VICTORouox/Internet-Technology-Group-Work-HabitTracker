// static/js/habit-keyboard.js

document.addEventListener("DOMContentLoaded", function () {

    // The button container of each card
    const cardGroups = document.querySelectorAll("[data-card-actions]");

    cardGroups.forEach(group => {

        // Get all the actionable controls in the current card
        const buttons = group.querySelectorAll("button, a");

        if (!buttons.length) return;

        // Initialize roving tabindex: Only allow the first button to be tabbed into
        buttons.forEach((btn, i) => {
            btn.setAttribute("tabindex", i === 0 ? "0" : "-1");
        });

        buttons.forEach((btn, index) => {

            btn.addEventListener("keydown", function (e) {

                let targetIndex = index;

                // Right arrow
                if (e.key === "ArrowRight") {
                    e.preventDefault();
                    targetIndex = (index + 1) % buttons.length;
                }

                // Left arrow
                if (e.key === "ArrowLeft") {
                    e.preventDefault();
                    targetIndex = (index - 1 + buttons.length) % buttons.length;
                }

                // Update focus
                if (targetIndex !== index) {

                    buttons.forEach(b => b.setAttribute("tabindex", "-1"));

                    const target = buttons[targetIndex];
                    target.setAttribute("tabindex", "0");
                    target.focus();
                }

                // Press Enter or Space to trigger the button
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    btn.click();
                }

            });

        });

    });

});