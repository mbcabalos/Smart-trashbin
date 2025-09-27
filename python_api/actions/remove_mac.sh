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
iptables -D FORWARD -m mac --mac-source "$MAC" -j ACCEPT 2>/dev/null

# 2️⃣ Restore HTTP redirect for this MAC
iptables -t nat -D PREROUTING -i wlan0 -p tcp --dport 80 ! -d 192.168.50.1 -m mac --mac-source "$MAC" -j RETURN 2>/dev/null

echo "MAC $MAC revoked. Internet access blocked and captive portal restored."
