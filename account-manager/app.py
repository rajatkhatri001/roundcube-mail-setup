from flask import Flask, request, redirect, render_template_string
import pymysql, secrets

app = Flask(__name__)
DB = dict(host='roundcubemail-mysql', user='roundcube', password='123', database='roundcubemail')

TEMPLATE = '''
<h2>Mirrored Hostinger Accounts</h2>
<form method="post" action="/add">
  Email: <input name="email" required><br>
  Hostinger Password: <input name="password" type="password" required><br>
  <button type="submit">Add & Start Mirroring</button>
</form>
<hr>
<table border=1 cellpadding=5>
<tr><th>Email</th><th>Active</th><th>Created</th><th>Action</th></tr>
{% for acc in accounts %}
<tr><td>{{acc[0]}}</td><td>{{acc[1]}}</td><td>{{acc[2]}}</td>
<td><a href="/toggle/{{acc[0]}}">Toggle Active</a></td></tr>
{% endfor %}
</table>
'''

@app.route('/')
def index():
    conn = pymysql.connect(**DB)
    cur = conn.cursor()
    cur.execute("SELECT email, active, created_at FROM mirror_accounts")
    accounts = cur.fetchall()
    conn.close()
    return render_template_string(TEMPLATE, accounts=accounts)

@app.route('/add', methods=['POST'])
def add():
    email_addr = request.form['email']
    hostinger_pw = request.form['password']
    local_pw = secrets.token_hex(8)
    conn = pymysql.connect(**DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO mirror_accounts (email, hostinger_password, local_password) VALUES (%s,%s,%s)",
                (email_addr, hostinger_pw, local_pw))
    cur.execute("INSERT INTO dovecot_users (email, password, home) VALUES (%s,%s,%s)",
                (email_addr, local_pw, f"/var/mail/{email_addr}"))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/toggle/<email_addr>')
def toggle(email_addr):
    conn = pymysql.connect(**DB)
    cur = conn.cursor()
    cur.execute("UPDATE mirror_accounts SET active = 1-active WHERE email=%s", (email_addr,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
