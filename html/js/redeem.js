document.getElementById("redeemForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const code = document.getElementById("voucherInput").value.trim();

  if (!code) {
    document.getElementById("result").textContent =
      "Please enter a voucher code.";
    return;
  }

  try {
    const response = await fetch("/api/redeem", {
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
    document.getElementById("result").textContent =
      error.message || "An error occurred.";
  }
});
