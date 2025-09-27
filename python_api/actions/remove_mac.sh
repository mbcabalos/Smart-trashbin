#!/bin/bash
# Usage: sudo ./revoke_mac.sh <MAC_ADDRESS>

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

MAC="$1"

if [ -z "$MAC" ]; then
  echo "Usage: $0 <MAC_ADDRESS>"
  exit 1
fi

echo "Revoking MAC: $MAC"

# 1️⃣ Remove forwarding rule
if iptables -C FORWARD -m mac --mac-source "$MAC" -j ACCEPT 2>/dev/null; then
    iptables -D FORWARD -m mac --mac-source "$MAC" -j ACCEPT
    echo "MAC $MAC removed from FORWARD chain."
else 
  echo "Error: MAC $MAC not found in FORWARD chain."
fi

# 2️⃣ Restore HTTP redirect for this MAC
if iptables -t nat -C PREROUTING -i wlan0 -p tcp --dport 80 ! -d 192.168.50.1 -m mac --mac-source "$MAC" -j RETURN 2>/dev/null; then
iptables -t nat -D PREROUTING -i wlan0 -p tcp --dport 80 ! -d 192.168.50.1 -m mac --mac-source "$MAC" -j RETURN
fi

echo "MAC $MAC revoked. Internet access blocked and captive portal restored."
