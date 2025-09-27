#!/bin/bash

# Usage: sudo ./whitelist_mac.sh AA:BB:CC:DD:EE:FF

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

MAC="$1"
if [ -z "$MAC" ]; then
  echo "Usage: $0 <MAC_ADDRESS>"
  exit 1
fi

echo "Whitelisting MAC: $MAC"

# 1️⃣ Allow forwarding for this MAC
iptables -I FORWARD -m mac --mac-source "$MAC" -j ACCEPT

# 2️⃣ Exclude this MAC from HTTP redirect
iptables -t nat -C PREROUTING -i wlan0 -p tcp --dport 80 ! -d 192.168.50.1 -m mac --mac-source "$MAC" -j RETURN 2>/dev/null || \
iptables -t nat -I PREROUTING -i wlan0 -p tcp --dport 80 ! -d 192.168.50.1 -m mac --mac-source "$MAC" -j RETURN

echo "MAC $MAC successfully whitelisted. Device now has full internet access."
