/**
 * 身份验证交互处理器
 * 处理表单提交时的 UI 状态切换
 */
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');

    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            // 在实际 Django 环境中，如果你想处理 AJAX 登录，会用到 preventDefault
            // 这里我们仅展示高级感的加载反馈
            
            submitBtn.style.pointerEvents = 'none';
            submitBtn.style.opacity = '0.8';
            btnText.innerText = "正在验证空间权限...";
            
            // 重新渲染 Lucide 图标以处理动态内容
            lucide.createIcons();
        });
    }
});