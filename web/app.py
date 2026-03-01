"""
Web App - CTF Platform with Admin Panel, Timer, Certificate Generator
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template_string, redirect
from functools import wraps
from dotenv import load_dotenv
load_dotenv()

from ctf_core.config import Config
from ctf_core.challenge_manager import ChallengeManager
from ctf_core.flag_validator import FlagValidator
from ctf_core.scoreboard import Scoreboard
from ctf_core.auth import AuthManager

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
nav a:hover,nav a.active{color:var(--green)}
.container{max-width:500px;margin:4rem auto;padding:0 1rem}
.wide{max-width:1100px;margin:2rem auto;padding:0 1rem}
.card{background:var(--card);border:1px solid var(--border);border-radius:4px;padding:2rem}
.card h2{font-family:'Orbitron',sans-serif;color:var(--green);margin-bottom:1.5rem;font-size:1.1rem;letter-spacing:.1em}
.form-group{margin-bottom:1.2rem}
.form-group label{display:block;font-size:.75rem;color:#6a8;letter-spacing:.1em;margin-bottom:.4rem}
.form-group input,.form-group select{width:100%;padding:.75rem 1rem;background:var(--bg);border:1px solid var(--border);color:#cde;font-family:'Share Tech Mono',monospace;font-size:.9rem;border-radius:2px;outline:none;transition:border-color .2s}
.form-group input:focus{border-color:var(--green)}
.form-group input::placeholder{color:#3a5a4a}
.btn{padding:.75rem 1.5rem;font-family:'Share Tech Mono',monospace;font-size:.85rem;letter-spacing:.1em;border:1px solid var(--green);background:transparent;color:var(--green);cursor:pointer;border-radius:2px;transition:background .2s}
.btn:hover{background:rgba(0,255,136,.1)}
.btn-full{width:100%;margin-top:.5rem}
.btn-red{border-color:var(--red)!important;color:var(--red)!important}
.btn-red:hover{background:rgba(255,0,60,.1)!important}
.btn-blue{border-color:var(--blue)!important;color:var(--blue)!important}
.btn-blue:hover{background:rgba(0,212,255,.1)!important}
.btn-sm{padding:.4rem .8rem;font-size:.75rem}
.alert{padding:.75rem 1rem;border-radius:2px;margin-bottom:1rem;font-size:.85rem}
.alert-error{background:rgba(255,0,60,.1);border:1px solid rgba(255,0,60,.3);color:var(--red)}
.alert-success{background:rgba(0,255,136,.1);border:1px solid rgba(0,255,136,.3);color:var(--green)}
.alert-info{background:rgba(0,212,255,.1);border:1px solid rgba(0,212,255,.3);color:var(--blue)}
.link{color:var(--green);text-decoration:none;font-size:.8rem}
.link:hover{text-decoration:underline}
.text-center{text-align:center;margin-top:1rem}
table{width:100%;border-collapse:collapse}
th{text-align:left;padding:.75rem 1rem;font-size:.75rem;letter-spacing:.15em;color:var(--green);border-bottom:1px solid var(--border)}
td{padding:.75rem 1rem;border-bottom:1px solid rgba(26,58,74,.5);font-size:.85rem}
tr:hover td{background:rgba(0,255,136,.03)}
.badge{font-size:.7rem;padding:2px 8px;border-radius:2px;letter-spacing:.1em}
.badge-green{background:rgba(0,255,136,.1);color:#6f6;border:1px solid rgba(0,255,136,.3)}
.badge-red{background:rgba(255,0,60,.1);color:var(--red);border:1px solid rgba(255,0,60,.3)}
.badge-blue{background:rgba(0,212,255,.1);color:var(--blue);border:1px solid rgba(0,212,255,.3)}
.badge-yellow{background:rgba(255,200,0,.1);color:#fb0;border:1px solid rgba(255,200,0,.3)}
.section-title{font-family:'Orbitron',sans-serif;font-size:1rem;color:var(--green);letter-spacing:.2em;margin-bottom:1.5rem;padding-bottom:.5rem;border-bottom:1px solid var(--border)}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:2rem}
.stat-card{background:var(--card);border:1px solid var(--border);border-radius:4px;padding:1.5rem;text-align:center}
.stat-value{font-family:'Orbitron',sans-serif;font-size:2rem;color:var(--green)}
.stat-label{font-size:.75rem;color:#6a8;letter-spacing:.1em;margin-top:.25rem}
"""

TIMER_JS = """
function updateTimer() {
  const start = new Date("{{ start_time }}").getTime();
  const end = new Date("{{ end_time }}").getTime();
  const now = new Date().getTime();
  const timerEl = document.getElementById('timer');
  const timerLabel = document.getElementById('timer-label');
  if (!timerEl) return;
  if (!start || isNaN(start)) { timerEl.textContent = 'OPEN'; return; }
  if (now < start) {
    const diff = start - now;
    timerLabel.textContent = 'STARTS IN';
    timerEl.textContent = formatTime(diff);
  } else if (now < end) {
    const diff = end - now;
    timerLabel.textContent = 'TIME LEFT';
    timerEl.textContent = formatTime(diff);
    timerEl.style.color = diff < 3600000 ? 'var(--red)' : 'var(--green)';
  } else {
    timerLabel.textContent = 'CTF ENDED';
    timerEl.textContent = '00:00:00';
    timerEl.style.color = 'var(--red)';
  }
}
function formatTime(ms) {
  const h = Math.floor(ms/3600000);
  const m = Math.floor((ms%3600000)/60000);
  const s = Math.floor((ms%60000)/1000);
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
}
updateTimer();
setInterval(updateTimer, 1000);
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
      <input type="text" id="team" placeholder="your_team_name"/></div>
    <div class="form-group"><label>PASSWORD</label>
      <input type="password" id="password" placeholder="••••••••"/></div>
    <button class="btn btn-full" onclick="login()">LOGIN →</button>
    <div class="text-center"><a href="/register" class="link">No account? Register here</a></div>
  </div>
</div>
<script>
async function login() {
  const team = document.getElementById('team').value.trim();
  const password = document.getElementById('password').value;
  document.querySelectorAll('.alert').forEach(m=>m.remove());
  if (!team || !password) return showAlert('Fill in all fields','error');
  const r = await fetch('/api/v1/auth/login', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({team_name:team, password})
  });
  const data = await r.json();
  if (data.success) {
    localStorage.setItem('ctf_token', data.token);
    localStorage.setItem('ctf_team', data.team);
    localStorage.setItem('ctf_is_admin', data.is_admin);
    window.location.href = data.is_admin ? '/admin' : '/';
  } else {
    showAlert(data.message, 'error');
  }
}
function showAlert(msg, type) {
  document.querySelector('.card').insertAdjacentHTML('afterbegin',
    `<div class="alert alert-${type}">${msg}</div>`);
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
    <button class="btn btn-full" onclick="register()">CREATE TEAM →</button>
    <div class="text-center"><a href="/login" class="link">Already registered? Login</a></div>
  </div>
</div>
<script>
async function register() {
  const name = document.getElementById('name').value.trim();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const confirm = document.getElementById('confirm').value;
  const country = document.getElementById('country').value.trim();
  document.querySelectorAll('.alert').forEach(m=>m.remove());
  if (!name||!email||!password) return showAlert('Fill in all required fields','error');
  if (password!==confirm) return showAlert('Passwords do not match','error');
  if (password.length<8) return showAlert('Password must be at least 8 characters','error');
  const r = await fetch('/api/v1/auth/register', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({team_name:name, email, password, country})
  });
  const data = await r.json();
  showAlert(data.message, data.success?'success':'error');
  if (data.success) setTimeout(()=>window.location.href='/login', 2000);
}
function showAlert(msg,type) {
  document.querySelector('.card').insertAdjacentHTML('afterbegin',
    `<div class="alert alert-${type}">${msg}</div>`);
}
document.addEventListener('keydown', e => { if(e.key==='Enter') register(); });
</script></body></html>"""

VERIFY_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Verify - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + """</style></head><body>
<header class="header"><a class="logo" href="/">{{ ctf_name }}<span>//</span>CTF</a></header>
<div class="container"><div class="card" style="text-align:center">
  <h2>// EMAIL VERIFICATION</h2><br>
  {% if success %}
    <div class="alert alert-success">{{ message }}</div><br>
    <a href="/login" class="btn">GO TO LOGIN →</a>
  {% else %}
    <div class="alert alert-error">{{ message }}</div>
  {% endif %}
</div></div></body></html>"""

ADMIN_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Admin - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + """
.tabs{display:flex;margin-bottom:2rem}
.tab{padding:.75rem 1.5rem;cursor:pointer;border:1px solid var(--border);border-right:none;font-size:.8rem;letter-spacing:.1em;color:#6a8;transition:all .2s}
.tab:last-child{border-right:1px solid var(--border)}
.tab:hover,.tab.active{color:var(--green);background:rgba(0,255,136,.08)}
.panel{display:none}.panel.active{display:block}
</style></head><body>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span>//</span>CTF</a>
  <nav>
    <a href="/" >SITE</a>
    <a href="/admin" class="active">ADMIN</a>
    <span style="color:var(--green);margin-left:1.5rem;font-size:.8rem">👑 {{ admin_name }}</span>
    <button onclick="logout()" style="margin-left:1rem;background:none;border:1px solid #4a3a3a;color:#8a6a6a;padding:4px 10px;cursor:pointer;font-family:'Share Tech Mono',monospace;font-size:.75rem;border-radius:2px;">LOGOUT</button>
  </nav>
</header>
<div class="wide">
  <div class="grid-2" style="grid-template-columns:repeat(4,1fr)">
    <div class="stat-card"><div class="stat-value" id="stat-teams">-</div><div class="stat-label">TEAMS</div></div>
    <div class="stat-card"><div class="stat-value" id="stat-challenges">-</div><div class="stat-label">CHALLENGES</div></div>
    <div class="stat-card"><div class="stat-value" id="stat-solves">-</div><div class="stat-label">SOLVES</div></div>
    <div class="stat-card"><div class="stat-value" id="stat-verified">-</div><div class="stat-label">VERIFIED</div></div>
  </div>

  <div class="tabs">
    <div class="tab active" onclick="switchTab('teams')" id="tab-teams">TEAMS</div>
    <div class="tab" onclick="switchTab('challenges')" id="tab-challenges">CHALLENGES</div>
    <div class="tab" onclick="switchTab('solves')" id="tab-solves">SOLVE FEED</div>
  </div>

  <div class="panel active" id="panel-teams">
    <div class="section-title">// ALL TEAMS</div>
    <div style="margin-bottom:1rem">
      <input id="search" placeholder="Search team..." 
             style="padding:.5rem 1rem;background:var(--card);border:1px solid var(--border);color:#cde;font-family:'Share Tech Mono',monospace;border-radius:2px;width:300px"
             oninput="filterTeams()"/>
    </div>
    <table>
      <thead><tr>
        <th>TEAM</th><th>EMAIL</th><th>COUNTRY</th>
        <th>SCORE</th><th>SOLVES</th><th>STATUS</th><th>ACTIONS</th>
      </tr></thead>
      <tbody id="teams-body"></tbody>
    </table>
  </div>

  <div class="panel" id="panel-challenges">
    <div class="section-title">// CHALLENGES</div>
    <table>
      <thead><tr><th>NAME</th><th>CATEGORY</th><th>POINTS</th><th>DIFFICULTY</th><th>SOLVES</th><th>FLAG</th></tr></thead>
      <tbody id="challenges-body"></tbody>
    </table>
  </div>

  <div class="panel" id="panel-solves">
    <div class="section-title">// SOLVE FEED</div>
    <table>
      <thead><tr><th>TIME</th><th>TEAM</th><th>CHALLENGE</th><th>POINTS</th><th>FIRST BLOOD</th></tr></thead>
      <tbody id="solves-body"></tbody>
    </table>
  </div>
</div>

<script>
const token = localStorage.getItem('ctf_token');
let allTeams = [];

async function api(path, opts={}) {
  const headers = {'Content-Type':'application/json','Authorization':`Bearer ${token}`};
  return (await fetch('/api/v1'+path, {headers,...opts})).json();
}

async function loadStats() {
  const [teams, challenges, feed] = await Promise.all([
    api('/admin/teams'), api('/challenges'), api('/feed')
  ]);
  allTeams = teams.teams || [];
  document.getElementById('stat-teams').textContent = allTeams.length;
  document.getElementById('stat-challenges').textContent = (challenges.challenges||[]).length;
  document.getElementById('stat-solves').textContent = (feed.events||[]).length;
  document.getElementById('stat-verified').textContent = allTeams.filter(t=>t.verified).length;
  renderTeams(allTeams);

  const cb = document.getElementById('challenges-body');
  cb.innerHTML = (challenges.challenges||[]).map(c=>`<tr>
    <td>${c.name}</td>
    <td><span class="badge badge-blue">${c.category}</span></td>
    <td style="color:var(--green)">${c.points}</td>
    <td>${c.difficulty}</td>
    <td>${c.solves}</td>
    <td style="color:#4a8a6a;font-size:.75rem">${c.id}</td>
  </tr>`).join('');

  const sb = document.getElementById('solves-body');
  sb.innerHTML = (feed.events||[]).map(e=>`<tr>
    <td style="color:#4a8a6a">${e.timestamp}</td>
    <td style="color:var(--blue)">${e.team}</td>
    <td>${e.challenge}</td>
    <td style="color:var(--green)">+${e.points}</td>
    <td>${e.first_blood?'🩸 YES':''}</td>
  </tr>`).join('');
}

function renderTeams(teams) {
  const tbody = document.getElementById('teams-body');
  tbody.innerHTML = teams.map(t=>`<tr>
    <td style="color:#eef;font-weight:bold">${t.name}</td>
    <td style="color:#6a8;font-size:.8rem">${t.email}</td>
    <td>${t.country||'-'}</td>
    <td style="color:var(--green)">${t.score}</td>
    <td>${t.solves}</td>
    <td>
      ${t.verified?'<span class="badge badge-green">VERIFIED</span>':'<span class="badge badge-yellow">UNVERIFIED</span>'}
      ${t.banned?'<span class="badge badge-red" style="margin-left:4px">BANNED</span>':''}
    </td>
    <td>
      <button class="btn btn-sm ${t.banned?'btn-blue':'btn-red'}" 
              onclick="${t.banned?`unbanTeam('${t.name}')`:`banTeam('${t.name}')`}">
        ${t.banned?'UNBAN':'BAN'}
      </button>
      <button class="btn btn-sm" style="margin-left:4px" onclick="resetScore('${t.name}')">RESET</button>
      <button class="btn btn-sm btn-red" style="margin-left:4px" onclick="deleteTeam('${t.name}')">DELETE</button>
    </td>
  </tr>`).join('');
}

function filterTeams() {
  const q = document.getElementById('search').value.toLowerCase();
  renderTeams(allTeams.filter(t=>t.name.toLowerCase().includes(q)||t.email.toLowerCase().includes(q)));
}

async function banTeam(name) {
  if (!confirm(`Ban team ${name}?`)) return;
  await api('/admin/teams/ban', {method:'POST', body:JSON.stringify({team_name:name})});
  loadStats();
}

async function unbanTeam(name) {
  await api('/admin/teams/unban', {method:'POST', body:JSON.stringify({team_name:name})});
  loadStats();
}

async function resetScore(name) {
  if (!confirm(`Reset score for ${name}?`)) return;
  await api('/admin/teams/reset', {method:'POST', body:JSON.stringify({team_name:name})});
  loadStats();
}

async function deleteTeam(name) {
  if (!confirm(`DELETE team ${name}? This cannot be undone!`)) return;
  await api('/admin/teams/delete', {method:'POST', body:JSON.stringify({team_name:name})});
  loadStats();
}

function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  document.getElementById('panel-'+name).classList.add('active');
}

function logout() {
  fetch('/api/v1/auth/logout',{method:'POST',headers:{'Authorization':`Bearer ${token}`}});
  localStorage.clear();
  window.location.href='/login';
}

loadStats();
setInterval(loadStats, 30000);
</script></body></html>"""

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ ctf_name }}</title>
<style>
""" + BASE_STYLE + """
.hero{text-align:center;padding:3rem 2rem 1rem}
.hero h1{font-family:'Orbitron',sans-serif;font-size:clamp(2rem,5vw,4rem);font-weight:900;background:linear-gradient(135deg,var(--green),var(--blue));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:1rem}
.hero p{color:#6a8;max-width:600px;margin:0 auto 1.5rem;line-height:1.8}
.timer-box{display:inline-block;background:var(--card);border:1px solid var(--border);border-radius:4px;padding:1rem 2rem;margin-bottom:1.5rem}
.timer-label{font-size:.7rem;color:#6a8;letter-spacing:.2em;margin-bottom:.25rem}
.timer{font-family:'Orbitron',sans-serif;font-size:2.5rem;color:var(--green);letter-spacing:.1em}
.stats-bar{display:flex;justify-content:center;gap:3rem;padding:1.5rem;background:var(--card);border:1px solid var(--border);border-radius:4px;max-width:700px;margin:0 auto 2rem}
.stat{text-align:center}
.stat-value{font-family:'Orbitron',sans-serif;font-size:2rem;color:var(--green)}
.stat-label{font-size:.75rem;color:#6a8;letter-spacing:.1em}
.section{padding:2rem;max-width:1200px;margin:0 auto}
.section-title{font-family:'Orbitron',sans-serif;font-size:1.1rem;color:var(--green);letter-spacing:.2em;margin-bottom:1.5rem;padding-bottom:.5rem;border-bottom:1px solid var(--border)}
.challenges-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1rem}
.challenge-card{background:var(--card);border:1px solid var(--border);border-radius:4px;padding:1.25rem;cursor:pointer;transition:border-color .2s,transform .2s;position:relative;overflow:hidden}
.challenge-card:hover{border-color:var(--green);transform:translateY(-2px)}
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
.ch-desc{font-size:.78rem;color:#7a9a8a;margin-top:.5rem;line-height:1.5}
.ch-solves{font-size:.75rem;color:#6a8;margin-top:.5rem}
.solved-badge{position:absolute;top:.75rem;right:.75rem;background:rgba(0,255,136,.15);border:1px solid rgba(0,255,136,.3);color:var(--green);font-size:.65rem;padding:2px 6px;border-radius:2px}
.scoreboard-table table{width:100%;border-collapse:collapse}
.modal-overlay{position:fixed;inset:0;background:rgba(5,10,15,.92);display:none;align-items:center;justify-content:center;z-index:1000}
.modal-overlay.active{display:flex}
.modal{background:var(--card);border:1px solid var(--border);border-radius:4px;padding:2rem;max-width:520px;width:90%}
.modal h2{font-family:'Orbitron',sans-serif;color:var(--green);margin-bottom:.5rem}
.modal-desc{color:#6a8;margin-bottom:1.5rem;line-height:1.7;font-size:.85rem}
.flag-input{width:100%;padding:.75rem 1rem;background:var(--bg);border:1px solid var(--border);color:var(--green);font-family:'Share Tech Mono',monospace;font-size:.95rem;border-radius:2px;outline:none;transition:border-color .2s}
.flag-input:focus{border-color:var(--green)}
.flag-input::placeholder{color:#3a5a4a}
.btn-row{display:flex;gap:.75rem;margin-top:1rem}
.result-msg{margin-top:1rem;padding:.75rem;border-radius:2px;font-size:.9rem;display:none}
.result-msg.correct{background:rgba(0,255,136,.1);border:1px solid rgba(0,255,136,.3);color:var(--green)}
.result-msg.wrong{background:rgba(255,0,60,.1);border:1px solid rgba(255,0,60,.3);color:var(--red)}
.tabs{display:flex;margin-bottom:2rem}
.tab{padding:.75rem 1.5rem;cursor:pointer;border:1px solid var(--border);border-right:none;font-size:.8rem;letter-spacing:.1em;color:#6a8;transition:all .2s}
.tab:last-child{border-right:1px solid var(--border)}
.tab:hover,.tab.active{color:var(--green);background:rgba(0,255,136,.08)}
.panel{display:none}.panel.active{display:block}
.live-feed{max-height:350px;overflow-y:auto}
.feed-item{padding:.6rem 0;border-bottom:1px solid rgba(26,58,74,.4);font-size:.85rem;display:flex;gap:.75rem;align-items:center;flex-wrap:wrap}
.feed-time{color:#4a7a6a;flex-shrink:0}
.feed-team{color:var(--blue)}
.feed-pts{color:var(--green);margin-left:auto}
.user-bar{display:flex;align-items:center;gap:.75rem}
.user-badge{font-size:.75rem;color:var(--green);border:1px solid rgba(0,255,136,.3);padding:4px 10px;border-radius:2px}
.logout-btn{font-size:.75rem;color:#8a6a6a;cursor:pointer;border:1px solid #4a3a3a;padding:4px 10px;border-radius:2px;background:none;font-family:'Share Tech Mono',monospace;transition:all .2s}
.logout-btn:hover{color:var(--red);border-color:var(--red)}
.login-prompt{background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.2);border-radius:4px;padding:1.5rem;text-align:center;margin-bottom:2rem}
.login-prompt p{color:#6a8;margin-bottom:1rem;font-size:.9rem}
.login-prompt a{color:var(--green);text-decoration:none;border:1px solid var(--green);padding:.5rem 1.5rem;border-radius:2px;margin:0 .5rem;font-size:.85rem;transition:background .2s}
.login-prompt a:hover{background:rgba(0,255,136,.1)}
.cert-btn{background:none;border:1px solid var(--blue);color:var(--blue);padding:.5rem 1rem;font-family:'Share Tech Mono',monospace;font-size:.8rem;cursor:pointer;border-radius:2px;transition:background .2s}
.cert-btn:hover{background:rgba(0,212,255,.1)}
</style>
</head>
<body>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span>//</span>CTF</a>
  <nav>
    <a href="#" onclick="switchTab('challenges')" >CHALLENGES</a>
    <a href="#" onclick="switchTab('scoreboard')">SCOREBOARD</a>
    <a href="#" onclick="switchTab('feed')">LIVE FEED</a>
    <div class="user-bar" id="user-bar" style="display:none">
      <span class="user-badge" id="user-name"></span>
      <a id="admin-link" href="/admin" style="display:none;color:var(--red);font-size:.75rem;margin-left:.5rem;text-decoration:none;border:1px solid rgba(255,0,60,.3);padding:4px 10px;border-radius:2px;">👑 ADMIN</a>
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
  <div class="timer-box">
    <div class="timer-label" id="timer-label">TIME LEFT</div>
    <div class="timer" id="timer">--:--:--</div>
  </div>
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
    <div class="scoreboard-table">
      <table>
        <thead><tr><th>RANK</th><th>TEAM</th><th>SCORE</th><th>SOLVES</th><th>LAST SOLVE</th><th></th></tr></thead>
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
      <button class="btn" onclick="submitFlag()">SUBMIT FLAG</button>
      <button class="btn btn-red" onclick="closeModal()">CANCEL</button>
    </div>
    <div class="result-msg" id="result-msg"></div>
  </div>
</div>

<script>
let currentChallenge = null;
const token = localStorage.getItem('ctf_token');
const team = localStorage.getItem('ctf_team');
const isAdmin = localStorage.getItem('ctf_is_admin') === 'true';

if (token && team) {
  document.getElementById('user-bar').style.display = 'flex';
  document.getElementById('user-name').textContent = team;
  document.getElementById('auth-links').style.display = 'none';
  if (isAdmin) document.getElementById('admin-link').style.display = 'inline-block';
}

async function api(path, opts={}) {
  const headers = {'Content-Type':'application/json'};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return (await fetch('/api/v1'+path, {headers,...opts})).json();
}

async function loadChallenges() {
  const data = await api('/challenges');
  const myData = token ? await api('/me/solves') : {solves:[]};
  const mySolves = new Set((myData.solves||[]).map(s=>s.challenge_id));
  const grid = document.getElementById('challenges-grid');
  const prompt = document.getElementById('login-prompt-box');

  if (!token) {
    prompt.innerHTML = `<div class="login-prompt">
      <p>🔐 Login to submit flags and compete</p>
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
      const solved = mySolves.has(ch.id);
      const card = document.createElement('div');
      card.className = 'challenge-card';
      if (solved) card.style.borderColor = 'rgba(0,255,136,.4)';
      card.innerHTML = `
        ${solved?'<div class="solved-badge">✓ SOLVED</div>':''}
        <div class="ch-header"><div class="ch-name">${ch.name}</div><div class="ch-points">${ch.points}pts</div></div>
        <div class="ch-meta"><span class="tag tag-cat">${ch.category}</span><span class="tag tag-${ch.difficulty}">${ch.difficulty}</span></div>
        <div class="ch-desc">${ch.description||''}</div>
        <div class="ch-solves">${ch.solves} solve${ch.solves!==1?'s':''}</div>`;
      card.onclick = () => token ? openModal(ch) : window.location.href='/login';
      grid.appendChild(card);
    });
  });
}

async function loadScoreboard() {
  const data = await api('/scoreboard');
  const ranks = ['🥇','🥈','🥉'];
  const cls = ['rank-gold','rank-silver','rank-bronze'];
  document.getElementById('stat-teams').textContent = data.scores?.length||0;
  const tbody = document.getElementById('scoreboard-body');
  if (!data.scores?.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="color:#4a8a6a;padding:1rem;">No teams yet.</td></tr>';
    return;
  }
  tbody.innerHTML = data.scores.map((e,i)=>`<tr>
    <td style="color:${i===0?'#ffd700':i===1?'#c0c0c0':i===2?'#cd7f32':'#cde'}">${ranks[i]||(i+1)}</td>
    <td style="font-weight:bold">${e.team}</td>
    <td style="color:var(--green);font-family:Orbitron,sans-serif">${e.score}</td>
    <td>${e.solves}</td>
    <td style="color:#4a8a6a;font-size:.8rem">${e.last_solve}</td>
    <td><button class="cert-btn" onclick="getCertificate('${e.team}','${i+1}')">🏆 CERT</button></td>
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
  feed.innerHTML = data.events.map(e=>`
    <div class="feed-item">
      <span class="feed-time">[${e.timestamp}]</span>
      <span class="feed-team">${e.team}</span>
      <span style="color:#4a8a6a">solved</span>
      <span>${e.challenge}</span>
      ${e.first_blood?'<span style="color:var(--red)">🩸 FIRST BLOOD</span>':''}
      <span class="feed-pts">+${e.points}</span>
    </div>`).join('');
}

function getCertificate(teamName, rank) {
  window.open(`/certificate/${teamName}?rank=${rank}`, '_blank');
}

function openModal(ch) {
  currentChallenge = ch;
  document.getElementById('modal-title').textContent = ch.name;
  document.getElementById('modal-desc').textContent = ch.description||'Find the flag!';
  document.getElementById('flag-input').value = '';
  document.getElementById('result-msg').style.display = 'none';
  document.getElementById('modal').classList.add('active');
  setTimeout(()=>document.getElementById('flag-input').focus(),100);
}

function closeModal() {
  document.getElementById('modal').classList.remove('active');
  currentChallenge = null;
}

async function submitFlag() {
  if (!currentChallenge) return;
  const flag = document.getElementById('flag-input').value.trim();
  if (!flag) return;
  const r = await fetch('/api/v1/submit',{
    method:'POST', headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`},
    body: JSON.stringify({challenge_id:currentChallenge.id, flag, team})
  });
  const data = await r.json();
  const msg = document.getElementById('result-msg');
  msg.style.display = 'block';
  msg.className = 'result-msg '+(data.correct?'correct':'wrong');
  msg.textContent = data.message;
  if (data.correct) setTimeout(()=>{closeModal();loadChallenges();loadScoreboard();loadFeed();},1800);
}

function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  document.getElementById('panel-'+name).classList.add('active');
  if(name==='scoreboard') loadScoreboard();
  if(name==='feed') loadFeed();
}

function logout() {
  fetch('/api/v1/auth/logout',{method:'POST',headers:{'Authorization':`Bearer ${token}`}});
  localStorage.clear();
  window.location.href='/login';
}

document.getElementById('flag-input')?.addEventListener('keydown',e=>{if(e.key==='Enter')submitFlag();});
document.getElementById('modal')?.addEventListener('click',e=>{if(e.target===document.getElementById('modal'))closeModal();});

loadChallenges();
loadFeed();
setInterval(()=>{loadScoreboard();loadFeed();},30000);
</script>
<script>""" + TIMER_JS + """</script>
</body>
</html>"""

CERT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Certificate - {{ team }}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{background:#050a0f;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:2rem;font-family:'Share Tech Mono',monospace}
.cert{background:linear-gradient(135deg,#0a1520,#050a0f);border:2px solid #00ff88;border-radius:8px;padding:4rem;max-width:800px;width:100%;text-align:center;position:relative;overflow:hidden}
.cert::before{content:'';position:absolute;inset:8px;border:1px solid rgba(0,255,136,.3);border-radius:4px;pointer-events:none}
.cert::after{content:'';position:absolute;inset:0;background:repeating-linear-gradient(45deg,transparent,transparent 10px,rgba(0,255,136,.02) 10px,rgba(0,255,136,.02) 11px);pointer-events:none}
.corner{position:absolute;width:20px;height:20px;border-color:#00ff88;border-style:solid}
.corner-tl{top:16px;left:16px;border-width:2px 0 0 2px}
.corner-tr{top:16px;right:16px;border-width:2px 2px 0 0}
.corner-bl{bottom:16px;left:16px;border-width:0 0 2px 2px}
.corner-br{bottom:16px;right:16px;border-width:0 2px 2px 0}
.cert-logo{font-family:'Orbitron',sans-serif;font-size:1rem;color:rgba(0,255,136,.5);letter-spacing:.3em;margin-bottom:2rem}
.cert-title{font-family:'Orbitron',sans-serif;font-size:2.5rem;font-weight:900;color:#00ff88;text-shadow:0 0 30px rgba(0,255,136,.5);margin-bottom:.5rem}
.cert-subtitle{color:rgba(0,212,255,.7);font-size:.9rem;letter-spacing:.2em;margin-bottom:3rem}
.cert-text{color:#6a8;font-size:.9rem;margin-bottom:.75rem;letter-spacing:.05em}
.cert-name{font-family:'Orbitron',sans-serif;font-size:2rem;font-weight:700;color:#fff;text-shadow:0 0 20px rgba(255,255,255,.3);margin:1rem 0;padding:.75rem 2rem;border:1px solid rgba(0,255,136,.4);display:inline-block;background:rgba(0,255,136,.05);border-radius:4px}
.cert-rank{font-family:'Orbitron',sans-serif;font-size:3rem;color:#ffd700;text-shadow:0 0 20px rgba(255,215,0,.5);margin:1rem 0}
.cert-details{display:flex;justify-content:center;gap:3rem;margin:2rem 0;padding:1.5rem;border-top:1px solid rgba(26,58,74,.8);border-bottom:1px solid rgba(26,58,74,.8)}
.cert-detail{text-align:center}
.cert-detail-value{font-family:'Orbitron',sans-serif;font-size:1.5rem;color:#00ff88}
.cert-detail-label{font-size:.7rem;color:#4a8a6a;letter-spacing:.15em;margin-top:.25rem}
.cert-footer{margin-top:2rem;color:#4a6a5a;font-size:.75rem;letter-spacing:.1em}
.cert-id{color:#2a4a3a;font-size:.65rem;margin-top:.5rem}
.print-btn{margin-top:2rem;padding:.75rem 2rem;background:transparent;border:1px solid #00ff88;color:#00ff88;font-family:'Share Tech Mono',monospace;font-size:.85rem;cursor:pointer;border-radius:2px;letter-spacing:.1em;transition:background .2s}
.print-btn:hover{background:rgba(0,255,136,.1)}
@media print{.print-btn{display:none}body{background:#fff}.cert{border-color:#000;background:#fff}.cert-title{color:#000;text-shadow:none}.cert-name{color:#000;border-color:#000}.cert-rank{color:#c0a000}.cert-details{border-color:#ccc}.cert-logo,.cert-subtitle,.cert-text,.cert-footer{color:#666}}
</style>
</head>
<body>
<div class="cert">
  <div class="corner corner-tl"></div>
  <div class="corner corner-tr"></div>
  <div class="corner corner-bl"></div>
  <div class="corner corner-br"></div>
  <div class="cert-logo">{{ ctf_name | upper }} // CTF</div>
  <div class="cert-title">CERTIFICATE</div>
  <div class="cert-subtitle">OF ACHIEVEMENT</div>
  <div class="cert-text">This certifies that</div>
  <div class="cert-name">{{ team }}</div>
  <div class="cert-text">has successfully competed in</div>
  <div class="cert-text" style="color:#00ff88;font-size:1.1rem;letter-spacing:.1em">{{ ctf_name }}</div>
  <div class="cert-rank">{{ rank_emoji }} #{{ rank }}</div>
  <div class="cert-details">
    <div class="cert-detail">
      <div class="cert-detail-value">{{ score }}</div>
      <div class="cert-detail-label">POINTS</div>
    </div>
    <div class="cert-detail">
      <div class="cert-detail-value">{{ solves }}</div>
      <div class="cert-detail-label">SOLVES</div>
    </div>
    <div class="cert-detail">
      <div class="cert-detail-value">{{ rank }}</div>
      <div class="cert-detail-label">RANK</div>
    </div>
  </div>
  <div class="cert-footer">{{ ctf_name }} — {{ date }}</div>
  <div class="cert-id">Certificate ID: {{ cert_id }}</div>
  <button class="print-btn" onclick="window.print()">🖨️ PRINT / SAVE AS PDF</button>
</div>
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
            if not get_current_team():
                return jsonify({"error": "Login required"}), 401
            return f(*args, **kwargs)
        return wrapper

    def require_admin(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            team = get_current_team()
            if not team or not auth.is_admin(team):
                return jsonify({"error": "Admin required"}), 403
            return f(*args, **kwargs)
        return wrapper

    # ── Page Routes ──────────────────────────────────────────────────────
    @app.route("/")
    def index():
        return render_template_string(INDEX_HTML,
            ctf_name=config.ctf_name,
            ctf_description=config.ctf_description,
            start_time=config.start_time,
            end_time=config.end_time)

    @app.route("/login")
    def login_page():
        return render_template_string(LOGIN_HTML,
            ctf_name=config.ctf_name, error=None, success=None)

    @app.route("/register")
    def register_page():
        return render_template_string(REGISTER_HTML,
            ctf_name=config.ctf_name, error=None)

    @app.route("/verify/<token>")
    def verify_email(token):
        result = auth.verify_email(token)
        return render_template_string(VERIFY_HTML,
            ctf_name=config.ctf_name,
            success=result.success, message=result.message)

    @app.route("/admin")
    def admin_page():
        return render_template_string(ADMIN_HTML,
            ctf_name=config.ctf_name,
            admin_name=config.admin_username)

    @app.route("/certificate/<team_name>")
    def certificate(team_name):
        import hashlib
        from datetime import datetime
        rank = int(request.args.get("rank", 1))
        info = auth.get_team_info(team_name)
        if not info:
            scores = scoreboard.get_top(100)
            score = next((s.score for s in scores if s.team == team_name), 0)
            solves = next((s.solves for s in scores if s.team == team_name), 0)
        else:
            score = info.get("score", 0)
            solves = info.get("solves", 0)

        rank_emojis = {1: "🥇", 2: "🥈", 3: "🥉"}
        rank_emoji = rank_emojis.get(rank, "🏅")
        cert_id = hashlib.md5(f"{team_name}{rank}{config.ctf_name}".encode()).hexdigest()[:12].upper()

        return render_template_string(CERT_HTML,
            ctf_name=config.ctf_name,
            team=team_name,
            rank=rank,
            rank_emoji=rank_emoji,
            score=score,
            solves=solves,
            date=datetime.now().strftime("%B %d, %Y"),
            cert_id=cert_id)

    # ── Auth API ─────────────────────────────────────────────────────────
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
        is_admin = auth.is_admin(result.team) if result.success else False
        return jsonify({"success": result.success, "message": result.message,
                        "token": result.token, "team": result.team,
                        "is_admin": is_admin})

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

    # ── Challenge API ─────────────────────────────────────────────────────
    @app.route("/api/v1/challenges")
    def api_challenges():
        return jsonify({"challenges": [
            {"id": c.id, "name": c.name, "category": c.category,
             "points": c.points, "difficulty": c.difficulty,
             "description": c.description, "solves": c.solves}
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
             "points": e.points, "timestamp": e.timestamp,
             "first_blood": e.first_blood}
            for e in scoreboard.get_solve_feed()
        ]})

    @app.route("/api/v1/me")
    @require_auth
    def api_me():
        team = get_current_team()
        info = auth.get_team_info(team)
        return jsonify({"team": info})

    @app.route("/api/v1/me/solves")
    def api_me_solves():
        team = get_current_team()
        if not team:
            return jsonify({"solves": []})
        solves = validator.get_team_solves(team)
        return jsonify({"solves": [
            {"challenge_id": r[0], "points": r[1],
             "first_blood": bool(r[2])} for r in solves
        ]})

    # ── Admin API ─────────────────────────────────────────────────────────
    @app.route("/api/v1/admin/teams")
    @require_admin
    def api_admin_teams():
        return jsonify({"teams": auth.get_all_teams()})

    @app.route("/api/v1/admin/teams/ban", methods=["POST"])
    @require_admin
    @require_json
    def api_ban_team():
        d = request.get_json()
        auth.ban_team(d.get("team_name",""))
        return jsonify({"success": True})

    @app.route("/api/v1/admin/teams/unban", methods=["POST"])
    @require_admin
    @require_json
    def api_unban_team():
        d = request.get_json()
        auth.unban_team(d.get("team_name",""))
        return jsonify({"success": True})

    @app.route("/api/v1/admin/teams/delete", methods=["POST"])
    @require_admin
    @require_json
    def api_delete_team():
        d = request.get_json()
        auth.delete_team(d.get("team_name",""))
        return jsonify({"success": True})

    @app.route("/api/v1/admin/teams/reset", methods=["POST"])
    @require_admin
    @require_json
    def api_reset_team():
        d = request.get_json()
        auth.reset_team_score(d.get("team_name",""))
        return jsonify({"success": True})

    @app.errorhandler(404)
    def not_found(e): return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e): return jsonify({"error": "Internal server error"}), 500

    # Auto seed
    def auto_seed():
        import os
        os.makedirs("challenges", exist_ok=True)
        for cat in ["web","pwn","crypto","forensics","reverse","misc"]:
            os.makedirs(f"challenges/{cat}", exist_ok=True)
        try:
            existing = manager.list_challenges()
            if len(existing) >= 1:
                return
            challenges = [
                ("web","SQL Injection 101",100,"easy","A login form is hiding something. Can you bypass authentication and retrieve the admin flag?"),
                ("web","JWT Bypass",200,"medium","This API uses JSON Web Tokens for authentication. The dev made a classic mistake."),
                ("crypto","Broken RSA",200,"medium","We intercepted an RSA-encrypted message. The developer reused primes across two public keys."),
                ("pwn","Buffer Overflow",300,"hard","A vulnerable C binary is running on the server. Overflow the buffer and hijack execution."),
                ("reverse","Crack Me",150,"easy","A Python binary checks your input against a secret key using XOR encoding. Reverse it!"),
                ("forensics","Hidden Message",250,"hard","We captured a suspicious image file. Something is hidden inside."),
            ]
            for category, name, points, difficulty, desc in challenges:
                ch = manager.create_challenge(category, name, points, difficulty, description=desc)
                print(f"[SEED] ✅ {ch.name} — {ch.flag}")
        except Exception as e:
            print(f"[SEED] Error: {e}")

    auto_seed()

    return app