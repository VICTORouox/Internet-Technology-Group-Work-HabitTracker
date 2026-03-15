// static/js/habit-keyboard.js

document.addEventListener("DOMContentLoaded", function () {

    // 每张卡片的按钮容器
    const cardGroups = document.querySelectorAll("[data-card-actions]");

    cardGroups.forEach(group => {

        // 获取当前卡片里的所有可操作控件
        const buttons = group.querySelectorAll("button, a");

        if (!buttons.length) return;

        // 初始化 roving tabindex：只允许第一个按钮 Tab 进入
        buttons.forEach((btn, i) => {
            btn.setAttribute("tabindex", i === 0 ? "0" : "-1");
        });

        buttons.forEach((btn, index) => {

            btn.addEventListener("keydown", function (e) {

                let targetIndex = index;

                // 右方向键
                if (e.key === "ArrowRight") {
                    e.preventDefault();
                    targetIndex = (index + 1) % buttons.length;
                }

                // 左方向键
                if (e.key === "ArrowLeft") {
                    e.preventDefault();
                    targetIndex = (index - 1 + buttons.length) % buttons.length;
                }

                // 更新 focus
                if (targetIndex !== index) {

                    buttons.forEach(b => b.setAttribute("tabindex", "-1"));

                    const target = buttons[targetIndex];
                    target.setAttribute("tabindex", "0");
                    target.focus();
                }

                // Enter 或 Space 触发按钮
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    btn.click();
                }

            });

        });

    });

});