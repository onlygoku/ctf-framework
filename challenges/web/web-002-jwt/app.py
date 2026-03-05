"""
WEB-002: Saiyan Auth Bypass (JWT None Algorithm)
Category: Web | Difficulty: Advanced | Points: 350
Flag: CTF{jwt_n0n3_alg_byp4ss}
Run: pip install flask && python app.py
Access: http://localhost:5002
Solution: forge JWT with {"alg":"none"} and {"role":"supreme_kai"}
"""
from flask import Flask, request, render_template_string, jsonify
import json, base64, hmac, hashlib

app = Flask(__name__)
SECRET = "kamehameha123"

def b64e(data):
    if isinstance(data, str): data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def b64d(data):
    data += '=' * (4 - len(data) % 4)
    return base64.urlsafe_b64decode(data)

def make_token(username, role="warrior"):
    h = b64e(json.dumps({"alg":"HS256","typ":"JWT"}))
    p = b64e(json.dumps({"user":username,"role":role}))
    s = b64e(hmac.new(SECRET.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest())
    return f"{h}.{p}.{s}"

def verify_token(token):
    try:
        parts = token.split(".")
        if len(parts) != 3: return None
        header  = json.loads(b64d(parts[0]))
        payload = json.loads(b64d(parts[1]))
        alg = header.get("alg","").lower()
        if alg == "none":
            return payload  # VULNERABLE: skips signature check
        elif alg == "hs256":
            expected = b64e(hmac.new(SECRET.encode(), f"{parts[0]}.{parts[1]}".encode(), hashlib.sha256).digest())
            if expected == parts[2]:
                return payload
        return None
    except:
        return None

HTML = """<!DOCTYPE html><html><head><title>Saiyan Auth Portal</title>
<style>
body{background:#0a0500;color:#f5e6c8;font-family:monospace;padding:2rem;max-width:700px}
h1{color:#ffd700}
input,textarea{background:#1a0800;border:1px solid #ff6a00;color:#ffd700;padding:.5rem;width:100%;font-family:monospace;margin:.4rem 0;box-sizing:border-box}
button{background:#ff6a00;border:none;color:#fff;padding:.5rem 1.5rem;cursor:pointer;margin:.4rem 0}
.token{background:#0d0300;border:1px solid #ff6a0044;padding:.75rem;word-break:break-all;margin:.5rem 0;font-size:.8rem;color:#00ff88;min-height:2rem}
.hint{color:#5a3a20;font-size:.8rem;margin-top:2rem;border-top:1px solid #ff6a0022;padding-top:1rem}
pre{color:#ffd700;background:#0d0300;padding:1rem;overflow-x:auto}
</style></head><body>
<h1>⚡ Saiyan Authentication Portal</h1>
<p style="color:#a08060">Login as a warrior. Only <strong style="color:#ffd700">Supreme Kai</strong> can access the secret chamber.</p>
<h3 style="color:#ff6a00">Step 1 — Get Token</h3>
<input id="user" placeholder="username" value="goku"/>
<button onclick="login()">GET TOKEN</button>
<div class="token" id="tok">Your JWT will appear here...</div>
<h3 style="color:#ff6a00">Step 2 — Access Panel</h3>
<textarea id="jwt" rows="4" placeholder="Paste your JWT here..."></textarea>
<button onclick="access()">ACCESS PANEL</button>
<div id="out"></div>
<div class="hint">
  💡 Decode your JWT at <code>jwt.io</code> — examine the header carefully<br>
  💡 What happens if the algorithm is set to <code>none</code>?<br>
  💡 The role you need: <code>supreme_kai</code>
</div>
<script>
async function login(){
  const r=await fetch('/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:document.getElementById('user').value})});
  const d=await r.json();
  document.getElementById('tok').textContent=d.token||d.error;
  document.getElementById('jwt').value=d.token||'';
}
async function access(){
  const token=document.getElementById('jwt').value.trim();
  const r=await fetch('/panel',{headers:{'Authorization':'Bearer '+token}});
  const d=await r.json();
  document.getElementById('out').innerHTML='<pre>'+JSON.stringify(d,null,2)+'</pre>';
}
</script></body></html>"""

@app.route("/")
def index(): return render_template_string(HTML)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    token = make_token(data.get("username","warrior"), "warrior")
    return jsonify({"token": token, "hint": "You are a warrior. Supreme Kai role required for secrets."})

@app.route("/panel")
def panel():
    token = request.headers.get("Authorization","").replace("Bearer ","")
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    if payload.get("role") == "supreme_kai":
        return jsonify({"status": "ACCESS GRANTED", "flag": "CTF{jwt_n0n3_alg_byp4ss}", "message": "Welcome, Supreme Kai!"})
    return jsonify({"status": "ACCESS DENIED", "message": f"You are a {payload.get('role')}. Not enough power level."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)