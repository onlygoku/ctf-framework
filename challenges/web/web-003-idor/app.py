"""
WEB-003: Frieza's Secret Files (IDOR)
Category: Web | Difficulty: Intermediate | Points: 250
Flag: CTF{id0r_acc3ss_c0ntr0l_byp4ss}
Run: pip install flask && python app.py
Access: http://localhost:5003
Login with: goku / kakarot  then change file ID to 1003
"""
from flask import Flask, request, render_template_string, session, jsonify

app = Flask(__name__)
app.secret_key = "planet-vegeta-destroyed"

USERS = {
    "goku":   {"password":"kakarot", "id":1001},
    "krillin":{"password":"baldguy", "id":1002},
}
FILES = {
    1001: {"name":"training_notes.txt",   "content":"My training schedule.\nNothing special here. Keep training!"},
    1002: {"name":"destructo_disc.txt",   "content":"Perfecting the Destructo Disc.\nStill working on it..."},
    1003: {"name":"CLASSIFIED_PLANS.txt", "content":"Planet conquest schedule:\n- Monday: Namek\n- Tuesday: Earth\n\nAlso stored here: CTF{id0r_acc3ss_c0ntr0l_byp4ss}"},
}

HTML = """<!DOCTYPE html><html><head><title>Frieza Corp Files</title>
<style>
body{background:#0a0500;color:#f5e6c8;font-family:monospace;padding:2rem;max-width:600px}
h1{color:#ffd700}
input{background:#1a0800;border:1px solid #ff6a00;color:#ffd700;padding:.5rem;width:220px;font-family:monospace}
button{background:#ff6a00;border:none;color:#fff;padding:.5rem 1rem;cursor:pointer}
.card{background:#1a0800;border:1px solid #ff6a0044;padding:1rem;margin:.5rem 0}
.hint{color:#5a3a20;font-size:.8rem;margin-top:2rem;border-top:1px solid #ff6a0022;padding-top:1rem}
pre{color:#f5e6c8;white-space:pre-wrap;margin:0}
</style></head><body>
<h1>🪐 Frieza Corp File System</h1>
{% if not logged_in %}
  <p style="color:#a08060">Login to access your personal files.</p>
  <input id="u" placeholder="username"/><br><br>
  <input id="p" type="password" placeholder="password"/><br><br>
  <button onclick="login()">LOGIN</button>
  <div id="msg" style="color:#ff4444;margin-top:.5rem"></div>
  <div class="hint">💡 Credentials: goku / kakarot</div>
{% else %}
  <p>Welcome <strong style="color:#ffd700">{{ username }}</strong> — your file ID is <code style="color:#ff6a00">{{ uid }}</code></p>
  <button onclick="logout()" style="background:#333;margin-bottom:1rem">LOGOUT</button>
  <h3 style="color:#ff6a00">Access file by ID:</h3>
  <input id="fid" placeholder="file id..." value="{{ uid }}"/>
  <button onclick="getFile()">GET FILE</button>
  <div id="out" style="margin-top:1rem"></div>
  <div class="hint">💡 You should only be able to see your own files... right?<br>💡 Try changing the ID in the request</div>
{% endif %}
<script>
async function login(){
  const r=await fetch('/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({u:document.getElementById('u').value,p:document.getElementById('p').value})});
  const d=await r.json();
  if(d.ok) location.reload(); else document.getElementById('msg').textContent='Invalid credentials';
}
async function logout(){await fetch('/logout',{method:'POST'});location.reload();}
async function getFile(){
  const id=document.getElementById('fid').value;
  const r=await fetch('/file/'+id);
  const d=await r.json();
  if(d.error){document.getElementById('out').innerHTML='<p style="color:#ff4444">'+d.error+'</p>';return;}
  document.getElementById('out').innerHTML='<div class="card"><strong style="color:#ff6a00">'+d.name+'</strong><hr style="border-color:#ff6a0022;margin:.5rem 0"><pre>'+d.content+'</pre></div>';
}
</script></body></html>"""

@app.route("/")
def index():
    return render_template_string(HTML, logged_in="user" in session,
        username=session.get("user",""), uid=session.get("uid",""))

@app.route("/login", methods=["POST"])
def login():
    d = request.get_json()
    u = USERS.get(d.get("u",""))
    if u and u["password"] == d.get("p",""):
        session["user"] = d["u"]; session["uid"] = u["id"]
        return jsonify({"ok": True})
    return jsonify({"ok": False})

@app.route("/logout", methods=["POST"])
def logout():
    session.clear(); return jsonify({"ok": True})

@app.route("/file/<int:file_id>")
def get_file(file_id):
    if "user" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    # INTENTIONALLY VULNERABLE — no ownership check
    f = FILES.get(file_id)
    if not f: return jsonify({"error": "File not found"})
    return jsonify(f)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=False)