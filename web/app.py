"""
Web App - CTF Platform with auth, email verification, bruteforce protection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template_string, redirect, url_for, make_response
from functools import wraps
from dotenv import load_dotenv
load_dotenv()

from ctf_core.config import Config
from ctf_core.challenge_manager import ChallengeManager
from ctf_core.flag_validator import FlagValidator
from ctf_core.scoreboard import Scoreboard
from ctf_core.auth import AuthManager

# ── HTML Pages ────────────────────────────────────────────────────────────────

BASE_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');
:root{--green:#00ff88;--red:#ff003c;--blue:#00d4ff;--bg:#050a0f;--card:#0a1520;--border:#1a3a4a}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:#cde;font-family:'Share Tech Mono',monospace;min-height:100vh}
body::before{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,136,.015) 2px,rgba(0,255,136,.015) 4px);pointer-events:none;z-index:0}
.header{border-bottom:1px solid var(--border);padding:1.5rem 2rem;display:flex;align-items:center;justify-content:space-between;background:rgba(0,255,136,.03);position:sticky;top:0;z-index:100;backdrop-filter:blur(8px)}
.logo{font-family:'Orbitron',sans-serif;font-weight:900;font-size:1.4rem;color:var(--green);text-shadow:0 0 20px rgba(0,255,136,.5);letter-spacing:.1em;text-decoration:none}
.logo span{color:var(--red)}
nav a{color:#7aa;text-decoration:none;margin-left:1.5rem;font-size:.8rem;letter-spacing:.1em;transition:color .2s}
nav a:hover{color:var(--green)}
nav a.active{color:var(--green)}
.container{max-width:500px;margin:4rem auto;padding:0 1rem}
.card{background:var(--card);border:1px solid var(--border);border-radius:4px;padding:2rem}
.card h2{font-family:'Orbitron',sans-serif;color:var(--green);margin-bottom:1.5rem;font-size:1.1rem;letter-spacing:.1em}
.form-group{margin-bottom:1.2rem}
.form-group label{display:block;font-size:.75rem;color:#6a8;letter-spacing:.1em;margin-bottom:.4rem}
.form-group input,.form-group select{width:100%;padding:.75rem 1rem;background:var(--bg);border:1px solid var(--border);color:#cde;font-family:'Share Tech Mono',monospace;font-size:.9rem;border-radius:2px;outline:none;transition:border-color .2s}
.form-group input:focus,.form-group select:focus{border-color:var(--green)}
.form-group input::placeholder{color:#3a5a4a}
.btn{width:100%;padding:.85rem;font-family:'Share Tech Mono',monospace;font-size:.9rem;letter-spacing:.15em;border:1px solid var(--green);background:transparent;color:var(--green);cursor:pointer;border-radius:2px;transition:background .2s;margin-top:.5rem}
.btn:hover{background:rgba(0,255,136,.1)}
.btn-red{border-color:var(--red);color:var(--red)}
.btn-red:hover{background:rgba(255,0,60,.1)}
.alert{padding:.75rem 1rem;border-radius:2px;margin-bottom:1rem;font-size:.85rem}
.alert-error{background:rgba(255,0,60,.1);border:1px solid rgba(255,0,60,.3);color:var(--red)}
.alert-success{background:rgba(0,255,136,.1);border:1px solid rgba(0,255,136,.3);color:var(--green)}
.alert-info{background:rgba(0,212,255,.1);border:1px solid rgba(0,212,255,.3);color:var(--blue)}
.link{color:var(--green);text-decoration:none;font-size:.8rem}
.link:hover{text-decoration:underline}
.text-center{text-align:center;margin-top:1rem}
.divider{border:none;border-top:1px solid var(--border);margin:1.5rem 0}
"""

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Login - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + """</style></head><body>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span>//</span>CTF</a>
  <nav><a href="/login" class="active">LOGIN</a><a href="/register">REGISTER</a></nav>
</header>
<div class="container">
  <div class="card">
    <h2>// TEAM LOGIN</h2>
    {% if error %}<div class="alert alert-error">{{ error }}</div>{% endif %}
    {% if success %}<div class="alert alert-success">{{ success }}</div>{% endif %}
    <div class="form-group"><label>TEAM NAME</label>
      <input type="text" id="team" placeholder="your_team_name" /></div>
    <div class="form-group"><label>PASSWORD</label>
      <input type="password" id="password" placeholder="••••••••" /></div>
    <button class="btn" onclick="login()">LOGIN →</button>
    <div class="text-center">
      <a href="/register" class="link">No account? Register here</a><br><br>
      <a href="/resend-verification" class="link">Resend verification email</a>
    </div>
  </div>
</div>
<script>
async function login() {
  const team = document.getElementById('team').value.trim();
  const password = document.getElementById('password').value;
  if (!team || !password) return alert('Fill in all fields');
  const r = await fetch('/api/v1/auth/login', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({team_name: team, password})
  });
  const data = await r.json();
  if (data.success) {
    localStorage.setItem('ctf_token', data.token);
    localStorage.setItem('ctf_team', data.team);
    window.location.href = '/';
  } else {
    document.querySelector('.card').insertAdjacentHTML('afterbegin',
      `<div class="alert alert-error">${data.message}</div>`);
  }
}
document.addEventListener('keydown', e => { if(e.key==='Enter') login(); });
</script></body></html>"""

REGISTER_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Register - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + """</style></head><body>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span>//</span>CTF</a>
  <nav><a href="/login">LOGIN</a><a href="/register" class="active">REGISTER</a></nav>
</header>
<div class="container">
  <div class="card">
    <h2>// REGISTER TEAM</h2>
    {% if error %}<div class="alert alert-error">{{ error }}</div>{% endif %}
    <div class="form-group"><label>TEAM NAME</label>
      <input type="text" id="name" placeholder="your_team_name" maxlength="32"/></div>
    <div class="form-group"><label>EMAIL</label>
      <input type="email" id="email" placeholder="team@email.com"/></div>
    <div class="form-group"><label>PASSWORD</label>
      <input type="password" id="password" placeholder="min 8 characters"/></div>
    <div class="form-group"><label>CONFIRM PASSWORD</label>
      <input type="password" id="confirm" placeholder="repeat password"/></div>
    <div class="form-group"><label>COUNTRY (optional)</label>
      <input type="text" id="country" placeholder="India"/></div>
    <button class="btn" onclick="register()">CREATE TEAM →</button>
    <div class="text-center"><a href="/login" class="link">Already have an account? Login</a></div>
  </div>
</div>
<script>
async function register() {
  const name = document.getElementById('name').value.trim();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const confirm = document.getElementById('confirm').value;
  const country = document.getElementById('country').value.trim();
  const msgs = document.querySelectorAll('.alert');
  msgs.forEach(m => m.remove());
  if (!name || !email || !password) return showAlert('Fill in all required fields', 'error');
  if (password !== confirm) return showAlert('Passwords do not match', 'error');
  if (password.length < 8) return showAlert('Password must be at least 8 characters', 'error');
  const r = await fetch('/api/v1/auth/register', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({team_name: name, email, password, country})
  });
  const data = await r.json();
  showAlert(data.message, data.success ? 'success' : 'error');
  if (data.success) setTimeout(() => window.location.href = '/login', 3000);
}
function showAlert(msg, type) {
  document.querySelector('.card').insertAdjacentHTML('afterbegin',
    `<div class="alert alert-${type}">${msg}</div>`);
}
document.addEventListener('keydown', e => { if(e.key==='Enter') register(); });
</script></body></html>"""

VERIFY_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Verify - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + """</style></head><body>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span>//</span>CTF</a>
</header>
<div class="container">
  <div class="card" style="text-align:center">
    <h2>// EMAIL VERIFICATION</h2><br>
    {% if success %}
      <div class="alert alert-success">{{ message }}</div>
      <br><a href="/login" class="btn" style="display:inline-block;width:auto;padding:.75rem 2rem;text-decoration:none;">GO TO LOGIN →</a>
    {% else %}
      <div class="alert alert-error">{{ message }}</div>
      <br><a href="/resend-verification" class="link">Resend verification email</a>
    {% endif %}
  </div>
</div></body></html>"""

RESEND_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Resend - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + """</style></head><body>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span>//</span>CTF</a>
</header>
<div class="container">
  <div class="card">
    <h2>// RESEND VERIFICATION</h2>
    <div class="form-group"><label>YOUR EMAIL</label>
      <input type="email" id="email" placeholder="team@email.com"/></div>
    <button class="btn" onclick="resend()">RESEND EMAIL →</button>
  </div>
</div>
<script>
async function resend() {
  const email = document.getElementById('email').value.trim();
  document.querySelectorAll('.alert').forEach(m=>m.remove());
  const r = await fetch('/api/v1/auth/resend', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({email})
  });
  const data = await r.json();
  document.querySelector('.card').insertAdjacentHTML('afterbegin',
    `<div class="alert alert-${data.success?'success':'error'}">${data.message}</div>`);
}
</script></body></html>"""

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ ctf_name }}</title>
<style>
""" + BASE_STYLE + """
.hero{text-align:center;padding:4rem 2rem 2rem}
.hero h1{font-family:'Orbitron',sans-serif;font-size:clamp(2rem,5vw,4rem);font-weight:900;background:linear-gradient(135deg,var(--green),var(--blue));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:1rem}
.hero p{color:#6a8;max-width:600px;margin:0 auto 2rem;line-height:1.8}
.stats-bar{display:flex;justify-content:center;gap:3rem;padding:1.5rem;background:var(--card);border:1px solid var(--border);border-radius:4px;max-width:700px;margin:2rem auto}
.stat{text-align:center}
.stat-value{font-family:'Orbitron',sans-serif;font-size:2rem;color:var(--green)}
.stat-label{font-size:.75rem;color:#6a8;letter-spacing:.1em}
.section{padding:3rem 2rem;max-width:1200px;margin:0 auto}
.section-title{font-family:'Orbitron',sans-serif;font-size:1.1rem;color:var(--green);letter-spacing:.2em;margin-bottom:1.5rem;padding-bottom:.5rem;border-bottom:1px solid var(--border)}
.challenges-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1rem}
.challenge-card{background:var(--card);border:1px solid var(--border);border-radius:4px;padding:1.25rem;cursor:pointer;transition:border-color .2s,transform .2s;position:relative;overflow:hidden}
.challenge-card::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(0,255,136,.05),transparent);opacity:0;transition:opacity .2s}
.challenge-card:hover{border-color:var(--green);transform:translateY(-2px)}
.challenge-card:hover::before{opacity:1}
.ch-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.75rem}
.ch-name{font-family:'Orbitron',sans-serif;font-size:.9rem;color:#eef}
.ch-points{font-family:'Orbitron',sans-serif;color:var(--green);font-size:1.1rem}
.ch-meta{display:flex;gap:.5rem;margin-bottom:.5rem;flex-wrap:wrap}
.tag{font-size:.7rem;padding:2px 8px;border-radius:2px;letter-spacing:.1em}
.tag-cat{background:rgba(0,212,255,.15);color:var(--blue);border:1px solid rgba(0,212,255,.3)}
.tag-easy{background:rgba(0,255,136,.1);color:#6f6;border:1px solid rgba(0,255,136,.3)}
.tag-medium{background:rgba(255,200,0,.1);color:#fb0;border:1px solid rgba(255,200,0,.3)}
.tag-hard{background:rgba(255,80,0,.1);color:#f80;border:1px solid rgba(255,80,0,.3)}
.tag-insane{background:rgba(255,0,60,.15);color:var(--red);border:1px solid rgba(255,0,60,.3)}
.ch-solves{font-size:.75rem;color:#6a8}
.ch-desc{font-size:.78rem;color:#7a9a8a;margin-top:.5rem;line-height:1.5}
.scoreboard table{width:100%;border-collapse:collapse}
.scoreboard th{text-align:left;padding:.75rem 1rem;font-size:.75rem;letter-spacing:.15em;color:var(--green);border-bottom:1px solid var(--border)}
.scoreboard td{padding:.75rem 1rem;border-bottom:1px solid rgba(26,58,74,.5)}
.scoreboard tr:hover td{background:rgba(0,255,136,.03)}
.rank-gold{color:#ffd700}
.rank-silver{color:#c0c0c0}
.rank-bronze{color:#cd7f32}
.modal-overlay{position:fixed;inset:0;background:rgba(5,10,15,.92);display:none;align-items:center;justify-content:center;z-index:1000}
.modal-overlay.active{display:flex}
.modal{background:var(--card);border:1px solid var(--border);border-radius:4px;padding:2rem;max-width:520px;width:90%}
.modal h2{font-family:'Orbitron',sans-serif;color:var(--green);margin-bottom:.5rem}
.modal-desc{color:#6a8;margin-bottom:1.5rem;line-height:1.7;font-size:.85rem}
.flag-input{width:100%;padding:.75rem 1rem;background:var(--bg);border:1px solid var(--border);color:var(--green);font-family:'Share Tech Mono',monospace;font-size:.95rem;border-radius:2px;outline:none;transition:border-color .2s}
.flag-input:focus{border-color:var(--green)}
.flag-input::placeholder{color:#3a5a4a}
.btn-row{display:flex;gap:.75rem;margin-top:1rem}
.btn-submit{padding:.75rem 1.5rem;font-family:'Share Tech Mono',monospace;font-size:.85rem;letter-spacing:.1em;border:1px solid var(--green);background:transparent;color:var(--green);cursor:pointer;border-radius:2px;transition:background .2s}
.btn-submit:hover{background:rgba(0,255,136,.1)}
.btn-cancel{padding:.75rem 1.5rem;font-family:'Share Tech Mono',monospace;font-size:.85rem;letter-spacing:.1em;border:1px solid #4a3a3a;background:transparent;color:#8a6a6a;cursor:pointer;border-radius:2px;transition:all .2s}
.btn-cancel:hover{background:rgba(255,0,60,.1);border-color:var(--red);color:var(--red)}
.result-msg{margin-top:1rem;padding:.75rem;border-radius:2px;font-size:.9rem;display:none}
.result-msg.correct{background:rgba(0,255,136,.1);border:1px solid rgba(0,255,136,.3);color:var(--green)}
.result-msg.wrong{background:rgba(255,0,60,.1);border:1px solid rgba(255,0,60,.3);color:var(--red)}
.tabs{display:flex;margin-bottom:2rem}
.tab{padding:.75rem 1.5rem;cursor:pointer;border:1px solid var(--border);border-right:none;font-size:.8rem;letter-spacing:.1em;color:#6a8;transition:all .2s}
.tab:last-child{border-right:1px solid var(--border)}
.tab:hover{color:var(--green)}
.tab.active{color:var(--green);background:rgba(0,255,136,.08)}
.panel{display:none}
.panel.active{display:block}
.live-feed{max-height:350px;overflow-y:auto}
.feed-item{padding:.6rem 0;border-bottom:1px solid rgba(26,58,74,.4);font-size:.85rem;display:flex;gap:.75rem;align-items:center;flex-wrap:wrap}
.feed-time{color:#4a7a6a;flex-shrink:0}
.feed-team{color:var(--blue)}
.feed-pts{color:var(--green);margin-left:auto}
.first-blood{color:var(--red)}
.user-bar{display:flex;align-items:center;gap:1rem}
.user-badge{font-size:.75rem;color:var(--green);border:1px solid rgba(0,255,136,.3);padding:4px 10px;border-radius:2px}
.logout-btn{font-size:.75rem;color:#8a6a6a;cursor:pointer;border:1px solid #4a3a3a;padding:4px 10px;border-radius:2px;background:none;font-family:'Share Tech Mono',monospace;transition:all .2s}
.logout-btn:hover{color:var(--red);border-color:var(--red)}
.login-prompt{background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.2);border-radius:4px;padding:1.5rem;text-align:center;margin-bottom:2rem}
.login-prompt p{color:#6a8;margin-bottom:1rem;font-size:.9rem}
.login-prompt a{color:var(--green);text-decoration:none;border:1px solid var(--green);padding:.5rem 1.5rem;border-radius:2px;margin:0 .5rem;font-size:.85rem;transition:background .2s}
.login-prompt a:hover{background:rgba(0,255,136,.1)}
</style>
</head>
<body>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span>//</span>CTF</a>
  <nav>
    <a href="#" onclick="switchTab('challenges')" id="nav-challenges">CHALLENGES</a>
    <a href="#" onclick="switchTab('scoreboard')" id="nav-scoreboard">SCOREBOARD</a>
    <a href="#" onclick="switchTab('feed')" id="nav-feed">LIVE FEED</a>
    <div class="user-bar" id="user-bar" style="display:none">
      <span class="user-badge" id="user-name"></span>
      <button class="logout-btn" onclick="logout()">LOGOUT</button>
    </div>
    <div id="auth-links">
      <a href="/login">LOGIN</a>
      <a href="/register">REGISTER</a>
    </div>
  </nav>
</header>

<div class="hero">
  <h1>{{ ctf_name }}</h1>
  <p>{{ ctf_description }}</p>
  <div class="stats-bar">
    <div class="stat"><div class="stat-value" id="stat-challenges">-</div><div class="stat-label">CHALLENGES</div></div>
    <div class="stat"><div class="stat-value" id="stat-teams">-</div><div class="stat-label">TEAMS</div></div>
    <div class="stat"><div class="stat-value" id="stat-solves">-</div><div class="stat-label">TOTAL SOLVES</div></div>
  </div>
</div>

<div class="section">
  <div class="tabs">
    <div class="tab active" onclick="switchTab('challenges')" id="tab-challenges">CHALLENGES</div>
    <div class="tab" onclick="switchTab('scoreboard')" id="tab-scoreboard">SCOREBOARD</div>
    <div class="tab" onclick="switchTab('feed')" id="tab-feed">LIVE FEED</div>
  </div>

  <div class="panel active" id="panel-challenges">
    <div class="section-title">// CHALLENGES</div>
    <div id="login-prompt-box"></div>
    <div class="challenges-grid" id="challenges-grid"><div style="color:#4a8a6a;padding:2rem;">Loading...</div></div>
  </div>

  <div class="panel" id="panel-scoreboard">
    <div class="section-title">// SCOREBOARD</div>
    <div class="scoreboard">
      <table>
        <thead><tr><th>RANK</th><th>TEAM</th><th>SCORE</th><th>SOLVES</th><th>LAST SOLVE</th></tr></thead>
        <tbody id="scoreboard-body"></tbody>
      </table>
    </div>
  </div>

  <div class="panel" id="panel-feed">
    <div class="section-title">// LIVE SOLVE FEED</div>
    <div class="live-feed" id="live-feed"></div>
  </div>
</div>

<div class="modal-overlay" id="modal">
  <div class="modal">
    <h2 id="modal-title">Submit Flag</h2>
    <p class="modal-desc" id="modal-desc"></p>
    <input class="flag-input" id="flag-input" placeholder="CTF{...}" type="text"/>
    <div class="btn-row">
      <button class="btn-submit" onclick="submitFlag()">SUBMIT FLAG</button>
      <button class="btn-cancel" onclick="closeModal()">CANCEL</button>
    </div>
    <div class="result-msg" id="result-msg"></div>
  </div>
</div>

<script>
let currentChallenge = null;
const token = localStorage.getItem('ctf_token');
const team = localStorage.getItem('ctf_team');

// Show user bar if logged in
if (token && team) {
  document.getElementById('user-bar').style.display = 'flex';
  document.getElementById('user-name').textContent = team;
  document.getElementById('auth-links').style.display = 'none';
}

async function api(path, opts={}) {
  const headers = {'Content-Type':'application/json'};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return (await fetch('/api/v1' + path, {headers, ...opts})).json();
}

async function loadChallenges() {
  const data = await api('/challenges');
  const grid = document.getElementById('challenges-grid');
  const prompt = document.getElementById('login-prompt-box');

  if (!token) {
    prompt.innerHTML = `<div class="login-prompt">
      <p>🔐 You must be logged in to submit flags and compete</p>
      <a href="/login">LOGIN</a><a href="/register">REGISTER</a>
    </div>`;
  }

  if (!data.challenges?.length) {
    grid.innerHTML = '<div style="color:#4a8a6a;padding:2rem;">No challenges yet.</div>';
    return;
  }

  document.getElementById('stat-challenges').textContent = data.challenges.length;
  const grouped = {};
  data.challenges.forEach(ch => { if(!grouped[ch.category]) grouped[ch.category]=[]; grouped[ch.category].push(ch); });
  grid.innerHTML = '';

  Object.entries(grouped).sort().forEach(([cat, chs]) => {
    const hdr = document.createElement('div');
    hdr.style.cssText = 'grid-column:1/-1;font-size:.75rem;letter-spacing:.2em;color:var(--blue);padding:.5rem 0;border-bottom:1px solid var(--border);margin-bottom:.5rem;';
    hdr.textContent = `// ${cat.toUpperCase()}`;
    grid.appendChild(hdr);

    chs.sort((a,b)=>a.points-b.points).forEach(ch => {
      const card = document.createElement('div');
      card.className = 'challenge-card';
      card.innerHTML = `
        <div class="ch-header"><div class="ch-name">${ch.name}</div><div class="ch-points">${ch.points}pts</div></div>
        <div class="ch-meta"><span class="tag tag-cat">${ch.category}</span><span class="tag tag-${ch.difficulty}">${ch.difficulty}</span></div>
        <div class="ch-desc">${ch.description || ''}</div>
        <div class="ch-solves" style="margin-top:.5rem">${ch.solves} solve${ch.solves!==1?'s':''}</div>`;
      card.onclick = () => token ? openModal(ch) : window.location.href='/login';
      grid.appendChild(card);
    });
  });
}

async function loadScoreboard() {
  const data = await api('/scoreboard');
  const ranks = ['🥇','🥈','🥉'];
  const cls = ['rank-gold','rank-silver','rank-bronze'];
  document.getElementById('stat-teams').textContent = data.scores?.length || 0;
  const tbody = document.getElementById('scoreboard-body');
  if (!data.scores?.length) {
    tbody.innerHTML = '<tr><td colspan="5" style="color:#4a8a6a;padding:1rem;">No teams yet.</td></tr>';
    return;
  }
  tbody.innerHTML = data.scores.map((e,i) => `<tr>
    <td class="${cls[i]||''}">${ranks[i]||(i+1)}</td>
    <td>${e.team}</td>
    <td style="color:var(--green);font-family:Orbitron,sans-serif">${e.score}</td>
    <td>${e.solves}</td>
    <td style="color:#4a8a6a;font-size:.8rem">${e.last_solve}</td>
  </tr>`).join('');
}

async function loadFeed() {
  const data = await api('/feed');
  const feed = document.getElementById('live-feed');
  if (!data.events?.length) {
    feed.innerHTML = '<div style="color:#4a8a6a;padding:1rem;">No solves yet. Be first!</div>';
    return;
  }
  document.getElementById('stat-solves').textContent = data.events.length;
  feed.innerHTML = data.events.map(e => `
    <div class="feed-item">
      <span class="feed-time">[${e.timestamp}]</span>
      <span class="feed-team">${e.team}</span>
      <span style="color:#4a8a6a">solved</span>
      <span>${e.challenge}</span>
      ${e.first_blood?'<span class="first-blood">🩸 FIRST BLOOD</span>':''}
      <span class="feed-pts">+${e.points}</span>
    </div>`).join('');
}

function openModal(ch) {
  currentChallenge = ch;
  document.getElementById('modal-title').textContent = ch.name;
  document.getElementById('modal-desc').textContent = ch.description || 'Find the flag!';
  document.getElementById('flag-input').value = '';
  document.getElementById('result-msg').style.display = 'none';
  document.getElementById('modal').classList.add('active');
  setTimeout(() => document.getElementById('flag-input').focus(), 100);
}

function closeModal() {
  document.getElementById('modal').classList.remove('active');
  currentChallenge = null;
}

async function submitFlag() {
  if (!currentChallenge) return;
  const flag = document.getElementById('flag-input').value.trim();
  if (!flag) return;
  const r = await fetch('/api/v1/submit', {
    method:'POST', headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`},
    body: JSON.stringify({challenge_id: currentChallenge.id, flag, team})
  });
  const data = await r.json();
  const msg = document.getElementById('result-msg');
  msg.style.display = 'block';
  msg.className = 'result-msg ' + (data.correct?'correct':'wrong');
  msg.textContent = data.message;
  if (data.correct) setTimeout(()=>{ closeModal(); loadChallenges(); loadScoreboard(); loadFeed(); }, 1800);
}

function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  document.getElementById('panel-'+name).classList.add('active');
  if (name==='scoreboard') loadScoreboard();
  if (name==='feed') loadFeed();
}

function logout() {
  fetch('/api/v1/auth/logout', {method:'POST', headers:{'Authorization':`Bearer ${token}`}});
  localStorage.removeItem('ctf_token');
  localStorage.removeItem('ctf_team');
  window.location.href = '/login';
}

document.getElementById('flag-input')?.addEventListener('keydown', e => { if(e.key==='Enter') submitFlag(); });
document.getElementById('modal')?.addEventListener('click', e => { if(e.target===document.getElementById('modal')) closeModal(); });

loadChallenges();
loadFeed();
setInterval(()=>{ loadScoreboard(); loadFeed(); }, 30000);
</script>
</body>
</html>"""


def create_app(config: Config = None) -> Flask:
    config = config or Config()
    app = Flask(__name__)
    app.secret_key = config.secret_key

    manager = ChallengeManager(config)
    validator = FlagValidator(config)
    scoreboard = Scoreboard(config)
    auth = AuthManager(config)

    def require_json(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json"}), 400
            return f(*args, **kwargs)
        return wrapper

    def get_current_team():
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        return auth.validate_session(token) if token else None

    def require_auth(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            team = get_current_team()
            if not team:
                return jsonify({"error": "Login required"}), 401
            return f(*args, **kwargs)
        return wrapper

    # ── Page Routes ────────────────────────────────────────────────────────
    @app.route("/")
    def index():
        return render_template_string(INDEX_HTML, ctf_name=config.ctf_name,
                                      ctf_description=config.ctf_description)

    @app.route("/login")
    def login_page():
        return render_template_string(LOGIN_HTML, ctf_name=config.ctf_name,
                                      error=None, success=None)

    @app.route("/register")
    def register_page():
        return render_template_string(REGISTER_HTML, ctf_name=config.ctf_name, error=None)

    @app.route("/verify/<token>")
    def verify_email(token):
        result = auth.verify_email(token)
        return render_template_string(VERIFY_HTML, ctf_name=config.ctf_name,
                                      success=result.success, message=result.message)

    @app.route("/resend-verification")
    def resend_page():
        return render_template_string(RESEND_HTML, ctf_name=config.ctf_name)

    # ── Auth API ───────────────────────────────────────────────────────────
    @app.route("/api/v1/auth/register", methods=["POST"])
    @require_json
    def api_register():
        d = request.get_json()
        result = auth.register(
            d.get("team_name","").strip(),
            d.get("email","").strip().lower(),
            d.get("password",""),
            d.get("country","").strip()
        )
        return jsonify({"success": result.success, "message": result.message})

    @app.route("/api/v1/auth/login", methods=["POST"])
    @require_json
    def api_login():
        d = request.get_json()
        result = auth.login(
            d.get("team_name","").strip(),
            d.get("password",""),
            request.remote_addr
        )
        return jsonify({"success": result.success, "message": result.message,
                        "token": result.token, "team": result.team})

    @app.route("/api/v1/auth/logout", methods=["POST"])
    def api_logout():
        token = request.headers.get("Authorization","").replace("Bearer ","")
        auth.logout(token)
        return jsonify({"success": True})

    @app.route("/api/v1/auth/resend", methods=["POST"])
    @require_json
    def api_resend():
        d = request.get_json()
        result = auth.resend_verification(d.get("email","").strip().lower())
        return jsonify({"success": result.success, "message": result.message})

    # ── Challenge API ──────────────────────────────────────────────────────
    @app.route("/api/v1/challenges")
    def api_challenges():
        return jsonify({"challenges": [
            {"id": c.id, "name": c.name, "category": c.category, "points": c.points,
             "difficulty": c.difficulty, "description": c.description, "solves": c.solves}
            for c in manager.list_challenges()
        ]})

    @app.route("/api/v1/submit", methods=["POST"])
    @require_json
    @require_auth
    def api_submit():
        team = get_current_team()
        d = request.get_json()
        challenge_id = d.get("challenge_id","").strip()
        flag = d.get("flag","").strip()
        if not challenge_id or not flag:
            return jsonify({"error": "Missing fields"}), 400
        result = validator.validate(challenge_id, flag, team, request.remote_addr)
        return jsonify({"correct": result.correct, "points": result.points,
                        "message": result.message, "hint": result.hint})

    @app.route("/api/v1/scoreboard")
    def api_scoreboard():
        n = min(int(request.args.get("top", 50)), 100)
        return jsonify({"scores": [
            {"rank": e.rank, "team": e.team, "score": e.score,
             "solves": e.solves, "last_solve": e.last_solve}
            for e in scoreboard.get_top(n)
        ]})

    @app.route("/api/v1/feed")
    def api_feed():
        return jsonify({"events": [
            {"team": e.team, "challenge": e.challenge, "category": e.category,
             "points": e.points, "timestamp": e.timestamp, "first_blood": e.first_blood}
            for e in scoreboard.get_solve_feed()
        ]})

    @app.route("/api/v1/me")
    @require_auth
    def api_me():
        team = get_current_team()
        info = auth.get_team_info(team)
        solves = validator.get_team_solves(team)
        return jsonify({"team": info, "solves": [
            {"challenge_id": r[0], "points": r[1], "first_blood": bool(r[2])} for r in solves
        ]})

    @app.errorhandler(404)
    def not_found(e): return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e): return jsonify({"error": "Internal server error"}), 500

    return app