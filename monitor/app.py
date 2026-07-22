from flask import Flask, request, render_template_string
import pymysql

app = Flask(__name__)
DB = dict(host='roundcubemail-mysql', user='roundcube', password='123', database='roundcubemail')

TEMPLATE = '''
<h2>Email Monitor</h2>
<form method="get">
  Search subject: <input name="q" value="{{q}}">
  Account: <input name="acc" value="{{acc}}">
  <button type="submit">Filter</button>
</form>
<table border=1 cellpadding=5>
<tr><th>Account</th><th>From</th><th>To</th><th>Subject</th><th>Sent</th><th>Synced</th></tr>
{% for row in rows %}
<tr><td>{{row[0]}}</td><td>{{row[1]}}</td><td>{{row[2]}}</td><td>{{row[3]}}</td><td>{{row[4]}}</td><td>{{row[5]}}</td></tr>
{% endfor %}
</table>
'''

@app.route('/')
def index():
    q = request.args.get('q', '')
    acc = request.args.get('acc', '')
    conn = pymysql.connect(**DB)
    cur = conn.cursor()
    cur.execute(
        "SELECT account_email, from_addr, to_addr, subject, sent_date, synced_at FROM email_log "
        "WHERE subject LIKE %s AND account_email LIKE %s ORDER BY sent_date DESC LIMIT 200",
        (f"%{q}%", f"%{acc}%")
    )
    rows = cur.fetchall()
    conn.close()
    return render_template_string(TEMPLATE, rows=rows, q=q, acc=acc)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
