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
    const response = await fetch("/api/redeem", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ voucher: code }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Failed to redeem voucher.");
    }

    // --- Decide what to do based on backend message ---
    if (data.message && data.message.includes("Enjoy your extra 5 minutes of internet service.")) {
      result.textContent = data.message;   // just show message
      input.value = "";                     // clear input
    } else {
      window.location.href = "success.html"; // first-time redemption
    }
  } catch (error) {
    // --- Restore form on error ---
    spinner.hidden = true;
    input.hidden = false;
    button.hidden = false;
    input.disabled = false;
    button.disabled = false;
    result.textContent = error.message || "An error occurred.";
  } finally {
    spinner.hidden = true; // always hide spinner after request
    input.hidden = false;
    button.hidden = false;
    input.disabled = false;
    button.disabled = false;
  }
});
