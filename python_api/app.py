import os
import threading, time, subprocess
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, timedelta
from gen_voucher import generate_and_store_voucher
from init_db import init_db


init_db()


# DATABASE = "/home/sbvm/python_api/sbvm_wifi.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "sbvm_wifi.db")
REMOVE_SCRIPT = os.path.join(BASE_DIR, "actions", "remove_mac.sh")
ALLOW_SCRIPT = os.path.join(BASE_DIR, "actions", "allow_mac.sh")

ACCESS_DURATION_MINUTES = 5
API_KEY = "DJMSBVMPROJ2025"


app = Flask(__name__)


def get_mac_from_ip(ip):
    try:
        # Ping once to refresh ARP cache (optional)
        subprocess.run(['ping', '-c', '1', '-W', '1', ip],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        with open('/proc/net/arp', 'r') as arp_table:
            lines = arp_table.readlines()[1:]
            for line in lines:
                parts = line.split()
                if parts[0] == ip and parts[3] != "00:00:00:00:00:00":
                    return parts[3].lower()
    except Exception as e:
        print(f"Error retrieving MAC for IP {ip}: {e}")
    return None

def get_ip_from_mac(mac):
    try:
        with open("/var/lib/misc/dnsmasq.leases") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 3 and parts[1].lower() == mac.lower():
                    return parts[2]
    except Exception as e:
        print(f"Error reading dnsmasq leases: {e}")
    return None

@app.route('/api/generate_voucher', methods=['POST'])
def generate_voucher_endpoint():
    key = request.headers.get("X-API-KEY")
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    code = generate_and_store_voucher()
    if code:
        return jsonify({"voucher": code, "message": "Voucher generated successfully"}), 200
    else:
        return jsonify({"error": "Failed to generate a unique voucher"}), 500

@app.route('/api/redeem', methods=['POST'])
def redeem():
    data = request.get_json()
    voucher = data.get('voucher')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Check voucher validity
    cursor.execute("SELECT redeemed FROM vouchers WHERE voucher_code = ?", (voucher,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Invalid voucher'}), 400
    if row[0]:
        conn.close()
        return jsonify({'error': 'Voucher already redeemed'}), 400

    client_ip = request.headers.get('X-Real-IP', request.remote_addr)
    mac = get_mac_from_ip(client_ip)
    if not mac:
        conn.close()
        return jsonify({'error': 'Could not determine MAC address'}), 400

    now = datetime.now()

    # Check if MAC already exists in SQLite
    cursor.execute("SELECT expires FROM access_time WHERE mac_address = ?", (mac,))
    row = cursor.fetchone()
    if row:
        # MAC exists, just extend expiry
        current_expiry = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
        new_expiry = max(now, current_expiry) + timedelta(minutes=ACCESS_DURATION_MINUTES)
        cursor.execute("UPDATE access_time SET expires=? WHERE mac_address=?", (new_expiry, mac))
        message = "Enjoy your extra 5 minutes of internet service."
        print(f"Extended expiry for MAC {mac} until {new_expiry}")
    else:
        # First-time redemption: whitelist MAC
        try:
            subprocess.run(["sudo", ALLOW_SCRIPT, mac], check=True)
        except subprocess.CalledProcessError as e:
            conn.close()
            return jsonify({'error': 'Failed to whitelist MAC address'}), 500

        new_expiry = now + timedelta(minutes=ACCESS_DURATION_MINUTES)
        cursor.execute(
            "INSERT INTO access_time (mac_address, ip_address, expires) VALUES (?, ?, ?)",
            (mac, client_ip, new_expiry)
        )
        message = f"Voucher redeemed. MAC {mac} whitelisted until {new_expiry.strftime('%H:%M:%S')}"
        print(f"Whitelisted MAC {mac} until {new_expiry}")

    # Mark voucher as redeemed
    cursor.execute(
        "UPDATE vouchers SET redeemed = 1, redeemed_by = ?, redeemed_at = ? WHERE voucher_code = ?",
        (mac, now, voucher)
    )

    conn.commit()
    conn.close()

    # Nudge client
    try:
        subprocess.run(["curl", "-s", f"http://{client_ip}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Could not nudge client: {e}")

    return jsonify({'message': message})



def expiry_watcher():
    while True:
        time.sleep(60)
        now = datetime.now()
        conn = sqlite3.connect('sbvm_wifi.db')
        cur = conn.cursor()
        cur.execute("SELECT mac_address, ip_address, expires FROM access_time")
        rows = cur.fetchall()
        print("Starting nudge")

        for mac, ip, exp_str in rows:
            expiry = datetime.fromisoformat(exp_str)

            if expiry <= now:
                subprocess.run(
                    ["sudo", REMOVE_SCRIPT, mac],
                    check=True
                )
                cur.execute("DELETE FROM access_time WHERE mac_address=?", (mac,))  
        conn.commit()
        conn.close()



if __name__ == '__main__':
    threading.Thread(target=expiry_watcher, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
