from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

valid_vouchers = {
    "123456": False,
    "VC001": False,
    "VC002": False,
}

def get_mac_from_ip(ip):
    try:
        # Ping once to refresh ARP cache (optional)
        subprocess.run(['ping', '-c', '1', '-W', '1', ip],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        with open('/proc/net/arp', 'r') as arp_table:
            lines = arp_table.readlines()[1:]  # Skip header
            for line in lines:
                parts = line.split()
                if parts[0] == ip and parts[3] != "00:00:00:00:00:00":
                    return parts[3].lower()
    except Exception as e:
        print(f"Error retrieving MAC for IP {ip}: {e}")
    return None

@app.route('/api/redeem', methods=['POST'])
def redeem():
    data = request.get_json()
    voucher = data.get('voucher')
    print(f"Voucher received: {voucher}")

    if voucher not in valid_vouchers:
        return jsonify({'error': 'Invalid voucher'}), 400

    if valid_vouchers[voucher]:
        return jsonify({'error': 'Voucher already redeemed'}), 400

    # Get client IP (direct or via proxy header)
    client_ip = request.headers.get('X-Real-IP', request.remote_addr)
    print(f"Client IP: {client_ip}")

    # Resolve MAC from IP
    mac = get_mac_from_ip(client_ip)
    if not mac:
        return jsonify({'error': 'Could not determine MAC address'}), 400
    print(f"Whitelisting MAC address: {mac}")

    # Run your whitelist script
    try:
        subprocess.run(['sudo', '/home/sbvm/captive_portal/python_api/actions/allow_mac.sh', mac], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running whitelist script: {e}")
        return jsonify({'error': 'Failed to whitelist MAC address'}), 500

    # Nudge the client to trigger captive portal detection
    try:
        # Refresh ARP table
        arp_output = subprocess.check_output(["arp", "-n"]).decode()
        client_ip = None
        for line in arp_output.splitlines():
            if mac.lower() in line.lower():
                client_ip = line.split()[0]
                break  # stop after first match
        if client_ip:
            subprocess.run(["curl", "-s", f"http://{client_ip}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Could not nudge client: {e}")

    valid_vouchers[voucher] = True
    return jsonify({'message': f'Voucher redeemed and MAC {mac} whitelisted.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
