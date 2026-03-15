function applyErrorStyle(element) {
    element.classList.add('error-message-active');
}

/* Step 1 Validation */
function validateStep1() {
    const goalChecked = document.querySelector('input[name="goal"]:checked');
    const preferenceChecked = document.querySelector('input[name="preference"]:checked');
    const goalError = document.getElementById('goal-error');
    const preferenceError = document.getElementById('preference-error');
    let isValid = true;

    goalError.textContent = '';
    preferenceError.textContent = '';
    goalError.classList.remove('error-message-active');
    preferenceError.classList.remove('error-message-active');

    if (!goalChecked) {
        goalError.textContent = '⚠ Please select a goal';
        applyErrorStyle(goalError);
        isValid = false;
    }

    if (!preferenceChecked) {
        preferenceError.textContent = '⚠ Please select an exercise preference';
        applyErrorStyle(preferenceError);
        isValid = false;
    }

    return isValid;
}

/* Step 2 Validation */
function validateStep2() {
    const heightInput = document.getElementById('height-input');
    const weightInput = document.getElementById('weight-input');
    const heightError = document.getElementById('height-error');
    const weightError = document.getElementById('weight-error');
    let isValid = true;

    heightError.textContent = '';
    weightError.textContent = '';
    heightError.classList.remove('error-message-active');
    weightError.classList.remove('error-message-active');
    heightInput.classList.remove('input-error');
    weightInput.classList.remove('input-error');

    const height = parseInt(heightInput.value);
    const weight = parseInt(weightInput.value);

    if (!heightInput.value) {
        heightError.textContent = '⚠ Height is required';
        applyErrorStyle(heightError);
        heightInput.classList.add('input-error');
        isValid = false;
    } else if (height < 100 || height > 250) {
        heightError.textContent = '⚠ Height must be between 100-250 cm';
        applyErrorStyle(heightError);
        heightInput.classList.add('input-error');
        isValid = false;
    }

    if (!weightInput.value) {
        weightError.textContent = '⚠ Weight is required';
        applyErrorStyle(weightError);
        weightInput.classList.add('input-error');
        isValid = false;
    } else if (weight < 30 || weight > 200) {
        weightError.textContent = '⚠ Weight must be between 30-200 kg';
        applyErrorStyle(weightError);
        weightInput.classList.add('input-error');
        isValid = false;
    }

    return isValid;
}

/* Step 3 Validation */
function validateStep3() {
    const conditionsChecked = document.querySelectorAll('input[name="conditions"]:checked');
    const conditionsError = document.getElementById('conditions-error');

    conditionsError.textContent = '';
    conditionsError.classList.remove('error-message-active');

    if (conditionsChecked.length === 0) {
        conditionsError.textContent = '⚠ Please select at least one option';
        applyErrorStyle(conditionsError);
        return false;
    }

    return true;
}

/* Step Navigation */
function nextStep(stepNum) {

    if (stepNum === 2 && !validateStep1()) return;
    if (stepNum === 3 && !validateStep2()) return;

    var contents = document.getElementsByClassName("step-content");
    for (var i = 0; i < contents.length; i++) {
        contents[i].classList.remove("active");
    }

    var steps = document.getElementsByClassName("step-item");
    for (var j = 0; j < steps.length; j++) {

        steps[j].classList.remove("active");
        steps[j].classList.remove("completed");

        if (j + 1 < stepNum) {
            steps[j].classList.add("completed");
        }

        if (j + 1 === stepNum) {
            steps[j].classList.add("active");
        }

    }

    document.getElementById("step-" + stepNum).classList.add("active");

}

/* 页面加载后初始化 */
document.addEventListener('DOMContentLoaded', function() {

    const heightInput = document.getElementById('height-input');
    const weightInput = document.getElementById('weight-input');
    const form = document.getElementById('recommendForm');

    /* Height validation */
    if (heightInput) {

        heightInput.addEventListener('input', function() {

            const height = parseInt(this.value);
            const heightError = document.getElementById('height-error');
            heightError.classList.remove('error-message-active');

            if (this.value && (height < 100 || height > 250)) {
                heightError.textContent = '⚠ Height must be between 100-250 cm';
                applyErrorStyle(heightError);
                this.classList.add('input-error');
            } else {
                heightError.textContent = '';
                this.classList.remove('input-error');
            }

        });

    }

    /* Weight validation */
    if (weightInput) {

        weightInput.addEventListener('input', function() {

            const weight = parseInt(this.value);
            const weightError = document.getElementById('weight-error');
            weightError.classList.remove('error-message-active');

            if (this.value && (weight < 30 || weight > 200)) {
                weightError.textContent = '⚠ Weight must be between 30-200 kg';
                applyErrorStyle(weightError);
                this.classList.add('input-error');
            } else {
                weightError.textContent = '';
                this.classList.remove('input-error');
            }

        });

    }

    /* Submit validation */
    if (form) {

        form.addEventListener('submit', function(e) {

            if (!validateStep3()) {
                e.preventDefault();
            }

        });

    }

    /* =========================
       Keyboard Accessibility
       ========================= */

    const labels = document.querySelectorAll('.option-grid label');

    labels.forEach(label => {

        label.addEventListener('keydown', function(e) {

            if (e.key === 'Enter' || e.key === ' ') {

                e.preventDefault();

                const input = document.getElementById(label.getAttribute('for'));

                if (input.type === 'radio') {
                    input.checked = true;
                }

                if (input.type === 'checkbox') {
                    input.checked = !input.checked;
                }

            }

        });

    });

});