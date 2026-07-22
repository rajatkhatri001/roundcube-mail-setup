IMAP (reading — goes to local Dovecot mirror):

Field	Value
Incoming mail server	dovecot
Security	None (not SSL/TLS)
Port	143
Username	user@asituj.com
Password	the local mirror password (from dovecot_users table, not the Hostinger password)

SMTP (sending — still goes directly to Hostinger, unmirrored):

Field	Value
Outgoing mail server	smtp.hostinger.com
Security	SSL/TLS (not STARTTLS)
Port	465
Authorization	Not "As IMAP" — needs its own separate Hostinger credentials, since IMAP now points to the local mirror, not Hostinger


docker exec -it roundcube-db mariadb -u roundcube -p123 roundcubemail -e "SELECT email, local_password FROM mirror_accounts WHERE email='user@asituj.com';"


docker exec -it roundcube-db mariadb -u roundcube -p123 roundcubemail -e "SELECT * FROM dovecot_users WHERE email='user@asituj.com';"   

docker exec -it roundcube-db mariadb -u roundcube -p123 roundcubemail -e "SELECT email, password FROM dovecot_users WHERE email='user@asituj.com';"


docker exec -it roundcube-db mariadb -u roundcube -p123 roundcubemail -e "SELECT email FROM mirror_accounts;"
docker exec -it roundcube-db mariadb -u roundcube -p123 roundcubemail -e "SELECT email FROM dovecot_users;"


TO Delete the User From the Database

docker exec -it roundcube-db mariadb -u roundcube -p123 roundcubemail -e "DELETE FROM mirror_accounts WHERE email='user@asituj.com';"
docker exec -it roundcube-db mariadb -u roundcube -p123 roundcubemail -e "DELETE FROM dovecot_users WHERE email='user@asituj.com';"



TO Check the User password From the Database

docker exec -it roundcube-db mariadb -u roundcube -p123 roundcubemail -e "SELECT email, password FROM dovecot_users WHERE email='user@asituj.com';"


TO Test the local Password 
docker exec -it local-dovecot doveadm auth test user@asituj.com





To create the database and tables



docker exec -it roundcube-db mariadb -u roundcube -p123 roundcubemail << 'EOF'
CREATE TABLE IF NOT EXISTS mirror_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hostinger_password VARCHAR(255) NOT NULL,
    local_password VARCHAR(255) NOT NULL,
    imap_host VARCHAR(255) DEFAULT 'imap.hostinger.com',
    imap_port INT DEFAULT 993,
    active TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS email_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_email VARCHAR(255) NOT NULL,
    message_uid VARCHAR(64),
    from_addr VARCHAR(255),
    to_addr VARCHAR(255),
    subject VARCHAR(500),
    sent_date DATETIME,
    synced_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_account (account_email),
    INDEX idx_date (sent_date)
);

CREATE TABLE IF NOT EXISTS dovecot_users (
    email VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    home VARCHAR(255) NOT NULL
);
EOF
