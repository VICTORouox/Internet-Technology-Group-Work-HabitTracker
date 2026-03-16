/**
 * Authentication interaction handler
 * Handle UI state switching and accessibility feedback during form submission
 */
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const submitBtn = document.getElementById('submitBtn');
    
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            
            // Add feedback for screen reader users
            submitBtn.setAttribute('aria-busy', 'true');
            submitBtn.setAttribute('disabled', 'disabled');
            
            const originalText = submitBtn.querySelector('span').innerText;
            submitBtn.querySelector('span').innerText = 'Verifying credentials...';
            
            // Re-render Lucide icons to handle dynamic content
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
            
            // Delayed backup to restore original state (in case submission fails)
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
    
    // Add validation feedback for all forms
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