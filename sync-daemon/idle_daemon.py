import threading, time, subprocess, pymysql

from imapclient import IMAPClient

DB = dict(host='roundcubemail-mysql', user='roundcube', password='123', database='roundcubemail')
IDLE_TIMEOUT = 25 * 60
RECONNECT_DELAY = 30

def get_accounts():
    conn = pymysql.connect(**DB)
    cur = conn.cursor()
    cur.execute("SELECT email, hostinger_password, local_password, imap_host, imap_port FROM mirror_accounts WHERE active=1")
    rows = cur.fetchall()
    conn.close()
    return rows

def run_sync(email_addr, hpw, lpw, host, port, timeout):
    try:
        subprocess.run([
            "imapsync",
            "--host1", host, "--user1", email_addr, "--password1", hpw, "--ssl1",
            "--host2", "dovecot", "--port2", "143", "--user2", email_addr, "--password2", lpw,
            "--automap", "--nofoldersizes", "--useuid"
        ], timeout=timeout, capture_output=True, text=True)
    except subprocess.TimeoutExpired:
        print(f"[{email_addr}] Sync timed out after {timeout}s, will resume next cycle", flush=True)
    except Exception as e:
        print(f"[{email_addr}] Sync error (details hidden for security): {type(e).__name__}", flush=True)

def watch_mailbox(email_addr, hpw, lpw, host, port):
    while True:
        try:
            print(f"[{email_addr}] Connecting (single login, will IDLE)...", flush=True)
            with IMAPClient(host, port=port, ssl=True) as client:
                client.login(email_addr, hpw)
                client.select_folder('INBOX')
                print(f"[{email_addr}] Logged in. Running initial full backfill (long timeout).", flush=True)
                run_sync(email_addr, hpw, lpw, host, port, timeout=1800)

                session_start = time.time()
                while True:
                    client.idle()
                    responses = client.idle_check(timeout=IDLE_TIMEOUT)
                    client.idle_done()
                    if responses:
                        print(f"[{email_addr}] New activity: {responses}", flush=True)
                        run_sync(email_addr, hpw, lpw, host, port, timeout=90)
                    if time.time() - session_start > IDLE_TIMEOUT:
                        print(f"[{email_addr}] Refreshing IDLE session", flush=True)
                        break
        except Exception as e:
            print(f"[{email_addr}] Connection error: {type(e).__name__}. Reconnecting in {RECONNECT_DELAY}s...", flush=True)
            time.sleep(RECONNECT_DELAY)

def main():
    threads = {}
    while True:
        try:
            for email_addr, hpw, lpw, host, port in get_accounts():
                if email_addr not in threads or not threads[email_addr].is_alive():
                    t = threading.Thread(target=watch_mailbox, args=(email_addr, hpw, lpw, host, port), daemon=True)
                    t.start()
                    threads[email_addr] = t
        except Exception as e:
            print(f"[main loop] Error checking accounts: {type(e).__name__}: {e}", flush=True)
        time.sleep(60)

if __name__ == "__main__":
    main()
