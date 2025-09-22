document.getElementById('simulate').addEventListener('click', () => {
  // Later this can call an ESP32 endpoint to generate a real code
  const code = 'VC' + Math.random().toString(36).substr(2, 6).toUpperCase();
  document.getElementById('voucher').textContent =
    `Your voucher: ${code}`;
});
