/**
 * 身份验证交互处理器
 * 处理表单提交时的 UI 状态切换和可访问性反馈
 */
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const submitBtn = document.getElementById('submitBtn');
    
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            // 在实际 Django 环境中，如果你想处理 AJAX 登录，会用到 preventDefault
            // 这里我们仅展示高级感的加载反馈
            
            // 为屏幕阅读器用户添加反馈
            submitBtn.setAttribute('aria-busy', 'true');
            submitBtn.setAttribute('disabled', 'disabled');
            
            const originalText = submitBtn.querySelector('span').innerText;
            submitBtn.querySelector('span').innerText = 'Verifying credentials...';
            
            // 重新渲染 Lucide 图标以处理动态内容
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
            
            // 恢复原始状态的延时备份（以防提交失败）
            setTimeout(() => {
                submitBtn.removeAttribute('aria-busy');
                submitBtn.removeAttribute('disabled');
                submitBtn.querySelector('span').innerText = originalText;
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            }, 3000);
        });
    }
    
    // 为所有表单添加验证反馈
    const inputs = document.querySelectorAll('input[type="email"], input[type="password"]');
    inputs.forEach(input => {
        input.addEventListener('invalid', (e) => {
            if (e.target.type === 'email' && e.target.validity.typeMismatch) {
                e.target.setAttribute('aria-invalid', 'true');
                e.target.setAttribute('aria-describedby', 'email-error');
            }
        });
        
        input.addEventListener('input', () => {
            if (input.validity.valid) {
                input.removeAttribute('aria-invalid');
            }
        });
    });
});