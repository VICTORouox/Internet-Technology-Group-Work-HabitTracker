document.addEventListener("DOMContentLoaded", function () {

const pw1 = document.getElementById("pw1");
const pw2 = document.getElementById("pw2");
const msg = document.getElementById("msg");
const btn = document.getElementById("resetBtn");

if (!pw1 || !pw2) return;

function validate() {

if (pw2.value === "") {
msg.innerText = "";
btn.disabled = false;
btn.style.opacity = "1";
return;
}

if (pw1.value !== pw2.value) {
msg.innerText = "Passwords do not match";
msg.className = "password-msg error";
btn.disabled = true;
btn.style.opacity = "0.5";
} else {
msg.innerText = "✓ Match";
msg.className = "password-msg success";
btn.disabled = false;
btn.style.opacity = "1";
}

}

pw1.addEventListener("input", validate);
pw2.addEventListener("input", validate);

});