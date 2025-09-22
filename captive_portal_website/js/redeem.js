document.getElementById('redeemForm').addEventListener('submit', e => {
  e.preventDefault();
  const code = document.getElementById('voucherInput').value.trim();
  if (code.startsWith('VC')) {
    document.getElementById('result').textContent =
      'Voucher accepted! Wi-Fi access granted.';
  } else {
    document.getElementById('result').textContent =
      'Invalid voucher.';
  }
});
