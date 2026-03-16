function scrollHabits(direction) {
    const container = document.getElementById("habitContainer");
    const scrollAmount = 400;

    if (direction === "left") {
        container.scrollBy({
            left: -scrollAmount,
            behavior: "smooth"
        });
    } else {
        container.scrollBy({
            left: scrollAmount,
            behavior: "smooth"
        });
    }
}

document.addEventListener("DOMContentLoaded", function () {

    const leftArrow = document.querySelector(".left-arrow");
    const rightArrow = document.querySelector(".right-arrow");

    if (leftArrow) {
        leftArrow.addEventListener("click", function () {
            scrollHabits("left");
        });
    }

    if (rightArrow) {
        rightArrow.addEventListener("click", function () {
            scrollHabits("right");
        });
    }

});