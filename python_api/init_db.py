import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "sbvm_wifi.db")

# DATABASE = "/home/sbvm/python_api/sbvm_wifi.db"

def init_db():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("PRAGMA journal_mode=WAL;")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_time (
            mac_address TEXT NOT NULL,
            ip_address TEXT,
            expires DATETIME NOT NULL,
            PRIMARY KEY (mac_address)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vouchers (
            voucher_code TEXT PRIMARY KEY,
            redeemed INTEGER DEFAULT 0,
            redeemed_by TEXT,
            redeemed_at DATETIME
        )
    """)

    vouchers = ["123456", "VC001", "VC002"]
    for v in vouchers:
        cursor.execute("INSERT OR IGNORE INTO vouchers (voucher_code) VALUES (?)", (v,))

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaderboards (
            email TEXT PRIMARY KEY,
            vouchers_redeemed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DATABASE}")

if __name__ == "__main__":
    init_db()
