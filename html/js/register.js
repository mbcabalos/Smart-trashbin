document
  .getElementById("registerForm")
  .addEventListener("submit", handleRegister);

async function handleRegister(event) {
  event.preventDefault();

  const username = document.getElementById("username").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirmPassword").value;

  const res = await fetch("http://localhost:5000/api/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password, confirmPassword }),
  });

  const data = await res.json();
  if (res.ok) {
    alert(data.message);
    window.location.href = "index.html";
  } else {
    alert(data.error);
  }
}
