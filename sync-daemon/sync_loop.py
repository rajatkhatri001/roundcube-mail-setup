import pymysql, subprocess, time, os, email
from email.utils import parsedate_to_datetime

DB = dict(host='roundcubemail-mysql', user='roundcube', password='roundcubepass', database='roundcubemail')
SYNC_INTERVAL = 30  # seconds
BACKFILL_DAYS = 90  # 3 months

def get_accounts():
    conn = pymysql.connect(**DB)
    cur = conn.cursor()
    cur.execute("SELECT email, hostinger_password, local_password, imap_host, imap_port, last_synced_at FROM mirror_accounts WHERE active=1")
    rows = cur.fetchall()
    conn.close()
    return rows

def ensure_dovecot_user(email_addr, local_password):
    conn = pymysql.connect(**DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO dovecot_users (email, password, home) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE password=%s",
                (email_addr, local_password, f"/var/mail/{email_addr}", local_password))
    conn.commit()
    conn.close()
    os.makedirs(f"/var/mail/{email_addr}", exist_ok=True)

def initial_backfill(email_addr, hostinger_pw, local_pw, imap_host, imap_port):
    print(f"[{email_addr}] Running initial {BACKFILL_DAYS}-day backfill...")
    subprocess.run([
        "imapsync",
        "--host1", imap_host, "--user1", email_addr, "--password1", hostinger_pw, "--ssl1",
        "--host2", "dovecot", "--port2", "143", "--user2", email_addr, "--password2", local_pw,
        "--maxage", str(BACKFILL_DAYS),
        "--automap", "--syncinternaldates"
    ])

def incremental_sync(email_addr, hostinger_pw, local_pw, imap_host, imap_port):
    subprocess.run([
        "imapsync",
        "--host1", imap_host, "--user1", email_addr, "--password1", hostinger_pw, "--ssl1",
        "--host2", "dovecot", "--port2", "143", "--user2", email_addr, "--password2", local_pw,
        "--automap", "--nofoldersizes", "--useuid"
    ], timeout=25)

def log_new_messages(email_addr):
    # Scan Maildir 'new' folders and log headers into email_log
    conn = pymysql.connect(**DB)
    cur = conn.cursor()
    base = f"/var/mail/{email_addr}"
    for root, dirs, files in os.walk(base):
        if root.endswith("/new") or root.endswith("/cur"):
            for fname in files:
                path = os.path.join(root, fname)
                cur.execute("SELECT COUNT(*) FROM email_log WHERE account_email=%s AND message_uid=%s", (email_addr, fname))
                if cur.fetchone()[0] > 0:
                    continue
                try:
                    with open(path, 'rb') as f:
                        msg = email.message_from_binary_file(f)
                    subject = msg.get('Subject', '')
                    from_addr = msg.get('From', '')
                    to_addr = msg.get('To', '')
                    date_hdr = msg.get('Date')
                    sent_date = parsedate_to_datetime(date_hdr) if date_hdr else None
                    cur.execute(
                        "INSERT INTO email_log (account_email, message_uid, from_addr, to_addr, subject, sent_date) VALUES (%s,%s,%s,%s,%s,%s)",
                        (email_addr, fname, from_addr, to_addr, subject, sent_date)
                    )
                except Exception as e:
                    print(f"parse error {path}: {e}")
    conn.commit()
    conn.close()

def main():
    synced_once = set()
    while True:
        for email_addr, hpw, lpw, host, port, last_sync in get_accounts():
            ensure_dovecot_user(email_addr, lpw)
            if email_addr not in synced_once:
                initial_backfill(email_addr, hpw, lpw, host, port)
                synced_once.add(email_addr)
            else:
                try:
                    incremental_sync(email_addr, hpw, lpw, host, port)
                except subprocess.TimeoutExpired:
                    print(f"[{email_addr}] sync timed out, will retry next cycle")
            log_new_messages(email_addr)
        time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    main()
