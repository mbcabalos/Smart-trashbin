const form = document.getElementById("redeemForm");
const input = document.getElementById("voucherInput");
const button = form.querySelector("button");
const spinner = document.getElementById("spinner");
const result = document.getElementById("result");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const code = input.value.trim();

  if (!code) {
    result.textContent = "Please enter a voucher code.";
    return;
  }

  // --- Show spinner and disable controls ---
  input.disabled = true;
  button.disabled = true;
  button.hidden = true;
  input.hidden = true;
  spinner.hidden = false;
  result.textContent = "";

  try {
    const response = await fetch("http://127.0.0.1:5000/api/redeem", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ voucher: code }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Failed to redeem voucher.");
    }

    window.location.href = "success.html";
  } catch (error) {
    // --- Restore form on error ---
    spinner.hidden = true;
    input.hidden = false;
    button.hidden = false;
    input.disabled = false;
    button.disabled = false;
    result.textContent = error.message || "An error occurred.";
  }
});
