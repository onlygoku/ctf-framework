"""
WEB-001: Dragon Ball Database (SQL Injection)
Category: Web | Difficulty: Intermediate | Points: 200
Flag: CTF{sqli_union_s3lect_p0wer}
Run: pip install flask && python app.py
Access: http://localhost:5001
Solution: ' UNION SELECT 1,flag,3,4 FROM secrets--
"""
from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)
DB = "/tmp/dbz_warriors.db"

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS warriors (id INTEGER PRIMARY KEY, name TEXT, power_level INTEGER, race TEXT);
        CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY, flag TEXT);
        INSERT OR IGNORE INTO warriors VALUES (1,'Goku',9001,'Saiyan');
        INSERT OR IGNORE INTO warriors VALUES (2,'Vegeta',8000,'Saiyan');
        INSERT OR IGNORE INTO warriors VALUES (3,'Piccolo',3500,'Namekian');
        INSERT OR IGNORE INTO warriors VALUES (4,'Frieza',12000,'Unknown');
        INSERT OR IGNORE INTO warriors VALUES (5,'Krillin',1800,'Human');
        INSERT OR IGNORE INTO secrets VALUES (1,'CTF{sqli_union_s3lect_p0wer}');
    """)
    con.commit(); con.close()

HTML = """<!DOCTYPE html><html><head><title>DBZ Warrior Database</title>
<style>
body{background:#0a0500;color:#f5e6c8;font-family:monospace;padding:2rem}
h1{color:#ffd700}
input{background:#1a0800;border:1px solid #ff6a00;color:#ffd700;padding:.5rem 1rem;font-family:monospace;width:320px}
button{background:#ff6a00;border:none;color:#fff;padding:.5rem 1.5rem;cursor:pointer}
table{border-collapse:collapse;margin-top:1.5rem;width:100%}
th{background:#1a0800;color:#ff6a00;padding:.5rem 1rem;border:1px solid #ff6a0044;text-align:left}
td{padding:.5rem 1rem;border:1px solid #ff6a0022}
.error{color:#ff4444;margin-top:.5rem}
.hint{color:#5a3a20;font-size:.8rem;margin-top:2rem;border-top:1px solid #ff6a0022;padding-top:1rem}
.query{color:#443322;font-size:.75rem;margin-top:.4rem}
</style></head><body>
<h1>🐉 DBZ Warrior Database</h1>
<p style="color:#a08060">Search for warriors by name:</p>
<form method="GET">
  <input name="search" placeholder="Enter warrior name..." value="{{ search }}"/>
  <button type="submit">⚡ SEARCH</button>
</form>
<div class="query">Query: SELECT id, name, power_level, race FROM warriors WHERE name LIKE '%{{ search }}%'</div>
{% if error %}<div class="error">DB Error: {{ error }}</div>{% endif %}
{% if results %}
<table>
  <tr><th>ID</th><th>Name</th><th>Power Level</th><th>Race</th></tr>
  {% for row in results %}
  <tr><td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td></tr>
  {% endfor %}
</table>
{% elif search %}<p style="color:#5a3a20;margin-top:1rem">No warriors found.</p>{% endif %}
<div class="hint">💡 The database has more than one table...<br>💡 SQLite stores table names in <code>sqlite_master</code></div>
</body></html>"""

@app.route("/")
def index():
    search = request.args.get("search", "")
    results, error = [], ""
    if search:
        try:
            con = sqlite3.connect(DB)
            # INTENTIONALLY VULNERABLE
            cur = con.cursor()
            cur.execute(f"SELECT id, name, power_level, race FROM warriors WHERE name LIKE '%{search}%'")
            results = cur.fetchall()
            con.close()
        except Exception as e:
            error = str(e)
    return render_template_string(HTML, search=search, results=results, error=error)

init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)