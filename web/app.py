"""
Web App - CTF Platform - Dragon Ball Z Theme
"""

import sys
import os
import traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template_string
from functools import wraps
from dotenv import load_dotenv
load_dotenv()

from ctf_core.config import Config
from ctf_core.challenge_manager import ChallengeManager
from ctf_core.flag_validator import FlagValidator
from ctf_core.scoreboard import Scoreboard
from ctf_core.auth import AuthManager

BASE_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');
:root {
  --orange:#ff6a00;--yellow:#ffd700;--gold:#ffb300;--red:#ff1a1a;
  --blue:#00aaff;--white:#fff;--dark:#0a0500;--card:#120800;
  --border:#ff6a0044;--glow:#ff6a00;--ki:#ffe066;--aura:#ff4400;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  background:var(--dark);color:#f5e6c8;
  font-family:'Rajdhani',sans-serif;min-height:100vh;
  overflow-x:hidden;
}

/* ── ANIMATED BACKGROUND ── */
body::before{
  content:'';position:fixed;inset:0;z-index:0;
  background:
    radial-gradient(ellipse 80% 60% at 50% 0%, #ff6a0022 0%, transparent 70%),
    radial-gradient(ellipse 40% 40% at 80% 80%, #ffd70011 0%, transparent 60%),
    radial-gradient(ellipse 60% 40% at 20% 60%, #ff220011 0%, transparent 60%),
    linear-gradient(180deg,#0a0500 0%,#0d0300 50%,#080200 100%);
  pointer-events:none;
}
body::after{
  content:'';position:fixed;inset:0;z-index:0;
  background-image:
    radial-gradient(circle 1px at 20% 30%, #ff6a0033 0%, transparent 1px),
    radial-gradient(circle 1px at 80% 70%, #ffd70022 0%, transparent 1px),
    radial-gradient(circle 1px at 50% 50%, #ff220022 0%, transparent 1px),
    radial-gradient(circle 2px at 10% 80%, #ff6a0044 0%, transparent 2px),
    radial-gradient(circle 1px at 90% 20%, #ffd70033 0%, transparent 1px);
  animation:stardrift 20s linear infinite;
  pointer-events:none;
}
@keyframes stardrift{0%{transform:translateY(0)}100%{transform:translateY(-100px)}}

/* ── ENERGY LINES ── */
.energy-lines{
  position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden;
}
.energy-lines span{
  position:absolute;height:1px;
  background:linear-gradient(90deg,transparent,#ff6a0066,transparent);
  animation:energyflow 3s linear infinite;
  opacity:0;
}
@keyframes energyflow{
  0%{opacity:0;transform:scaleX(0) translateX(-100%)}
  20%{opacity:1}
  80%{opacity:1}
  100%{opacity:0;transform:scaleX(1) translateX(100%)}
}

/* ── HEADER ── */
.header{
  position:sticky;top:0;z-index:100;
  padding:1rem 2rem;
  display:flex;align-items:center;justify-content:space-between;
  background:linear-gradient(180deg,rgba(10,5,0,.98) 0%,rgba(10,5,0,.9) 100%);
  border-bottom:2px solid var(--orange);
  box-shadow:0 2px 30px #ff6a0044,0 0 60px #ff6a0011;
}
.header::after{
  content:'';position:absolute;bottom:-4px;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--yellow),var(--orange),var(--yellow),transparent);
  animation:headershine 3s linear infinite;
}
@keyframes headershine{0%{opacity:.3}50%{opacity:1}100%{opacity:.3}}

/* ── LOGO ── */
.logo{
  font-family:'Bangers',cursive;font-size:2rem;letter-spacing:.15em;
  text-decoration:none;
  background:linear-gradient(135deg,var(--yellow) 0%,var(--orange) 50%,var(--red) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  filter:drop-shadow(0 0 10px #ff6a0088);
  transition:filter .3s;
  position:relative;
}
.logo:hover{filter:drop-shadow(0 0 20px #ffd700)}
.logo span{
  background:linear-gradient(135deg,#fff 0%,var(--yellow) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}

/* ── POWER LEVEL BADGE ── */
.power-level{
  font-family:'Bangers',cursive;font-size:.9rem;letter-spacing:.1em;
  color:var(--yellow);border:1px solid var(--orange);
  padding:4px 12px;border-radius:2px;
  background:rgba(255,106,0,.1);
  box-shadow:0 0 10px #ff6a0033;
  animation:powerpulse 2s ease-in-out infinite;
}
@keyframes powerpulse{0%,100%{box-shadow:0 0 10px #ff6a0033}50%{box-shadow:0 0 20px #ff6a0077}}

/* ── NAV ── */
nav{display:flex;align-items:center;gap:1.5rem}
nav a{
  color:#c8a878;text-decoration:none;
  font-family:'Rajdhani',sans-serif;font-weight:700;
  font-size:.85rem;letter-spacing:.15em;
  text-transform:uppercase;
  transition:all .2s;position:relative;
}
nav a::after{
  content:'';position:absolute;bottom:-4px;left:0;right:0;height:2px;
  background:var(--orange);transform:scaleX(0);transition:transform .2s;
}
nav a:hover{color:var(--yellow);text-shadow:0 0 10px #ffd70088}
nav a:hover::after{transform:scaleX(1)}
nav a.active{color:var(--orange)}

/* ── BUTTONS ── */
.btn{
  padding:.75rem 1.75rem;
  font-family:'Bangers',cursive;font-size:1rem;letter-spacing:.15em;
  border:2px solid var(--orange);
  background:linear-gradient(135deg,rgba(255,106,0,.15),rgba(255,50,0,.05));
  color:var(--yellow);cursor:pointer;border-radius:2px;
  transition:all .2s;position:relative;overflow:hidden;
  text-transform:uppercase;
}
.btn::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,var(--orange),var(--red));
  opacity:0;transition:opacity .2s;
}
.btn:hover{color:#fff;box-shadow:0 0 20px #ff6a0066;transform:translateY(-2px)}
.btn:hover::before{opacity:.2}
.btn:active{transform:translateY(0) scale(.98)}
.btn:disabled{opacity:.4;cursor:not-allowed;transform:none}
.btn-full{width:100%;margin-top:.5rem}
.btn-red{border-color:var(--red)!important;color:var(--red)!important}
.btn-red:hover{box-shadow:0 0 20px #ff000066!important}
.btn-blue{border-color:var(--blue)!important;color:var(--blue)!important}
.btn-sm{padding:.35rem .8rem;font-size:.8rem}

/* ── KI BLAST BUTTON EFFECT ── */
.btn-ki{
  border-color:var(--yellow);
  background:linear-gradient(135deg,rgba(255,215,0,.2),rgba(255,106,0,.1));
}
.btn-ki:hover{
  box-shadow:0 0 30px #ffd70088,0 0 60px #ff6a0044;
  color:#fff;
}

/* ── FORMS ── */
.container{max-width:480px;margin:4rem auto;padding:0 1rem;position:relative;z-index:1}
.wide{max-width:1100px;margin:2rem auto;padding:0 1rem;position:relative;z-index:1}

.card{
  background:linear-gradient(135deg,rgba(18,8,0,.95),rgba(10,5,0,.98));
  border:1px solid var(--orange);border-radius:4px;padding:2rem;
  box-shadow:0 0 40px #ff6a0022,inset 0 0 40px rgba(255,106,0,.03);
  position:relative;overflow:hidden;
}
.card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,transparent,var(--orange),var(--yellow),var(--orange),transparent);
  animation:cardshine 4s linear infinite;
}
@keyframes cardshine{0%{opacity:.5}50%{opacity:1}100%{opacity:.5}}

.card h2{
  font-family:'Bangers',cursive;font-size:1.8rem;letter-spacing:.2em;
  color:var(--orange);margin-bottom:1.5rem;
  text-shadow:0 0 20px #ff6a0066;
}

.form-group{margin-bottom:1.2rem}
.form-group label{
  display:block;font-size:.75rem;color:#c8a878;
  letter-spacing:.15em;margin-bottom:.4rem;
  font-family:'Rajdhani',sans-serif;font-weight:700;text-transform:uppercase;
}
.form-group input{
  width:100%;padding:.75rem 1rem;
  background:rgba(255,106,0,.05);
  border:1px solid rgba(255,106,0,.3);
  color:#f5e6c8;font-family:'Share Tech Mono',monospace;font-size:.9rem;
  border-radius:2px;outline:none;transition:all .2s;
}
.form-group input:focus{
  border-color:var(--orange);
  box-shadow:0 0 15px rgba(255,106,0,.3);
  background:rgba(255,106,0,.08);
}
.form-group input::placeholder{color:#5a3a20}

/* ── PASSWORD TOGGLE ── */
.pw-wrap{position:relative}
.pw-wrap input{padding-right:3rem}
.pw-toggle{
  position:absolute;right:.75rem;top:50%;transform:translateY(-50%);
  background:none;border:none;color:#c8a878;cursor:pointer;font-size:1rem;
  padding:0;line-height:1;transition:color .2s;
}
.pw-toggle:hover{color:var(--yellow)}

/* ── ALERTS ── */
.alert{padding:.75rem 1rem;border-radius:2px;margin-bottom:1rem;font-size:.9rem;font-weight:600}
.alert-error{background:rgba(255,26,26,.1);border:1px solid rgba(255,26,26,.4);color:#ff6666}
.alert-success{background:rgba(255,215,0,.1);border:1px solid rgba(255,215,0,.4);color:var(--yellow)}
.alert-info{background:rgba(0,170,255,.1);border:1px solid rgba(0,170,255,.3);color:var(--blue)}

.link{color:var(--orange);text-decoration:none;font-size:.85rem;font-weight:600}
.link:hover{color:var(--yellow);text-shadow:0 0 8px #ffd70088}
.text-center{text-align:center;margin-top:1rem}

/* ── TABLES ── */
table{width:100%;border-collapse:collapse}
th{
  text-align:left;padding:.75rem 1rem;font-size:.75rem;
  letter-spacing:.15em;color:var(--orange);
  border-bottom:2px solid rgba(255,106,0,.3);
  font-family:'Bangers',cursive;font-size:.95rem;
}
td{padding:.75rem 1rem;border-bottom:1px solid rgba(255,106,0,.1);font-size:.9rem}
tr:hover td{background:rgba(255,106,0,.05)}

/* ── BADGES ── */
.badge{font-size:.7rem;padding:2px 8px;border-radius:2px;letter-spacing:.1em;font-weight:700}
.badge-green{background:rgba(0,255,100,.1);color:#00ff88;border:1px solid rgba(0,255,100,.3)}
.badge-red{background:rgba(255,26,26,.1);color:#ff4444;border:1px solid rgba(255,26,26,.3)}
.badge-blue{background:rgba(0,170,255,.1);color:var(--blue);border:1px solid rgba(0,170,255,.3)}
.badge-yellow{background:rgba(255,215,0,.1);color:var(--yellow);border:1px solid rgba(255,215,0,.3)}
.badge-orange{background:rgba(255,106,0,.15);color:var(--orange);border:1px solid rgba(255,106,0,.4)}

/* ── STAT CARDS ── */
.stat-card{
  background:linear-gradient(135deg,rgba(18,8,0,.9),rgba(10,5,0,.95));
  border:1px solid rgba(255,106,0,.3);border-radius:4px;padding:1.5rem;
  text-align:center;position:relative;overflow:hidden;
  transition:all .3s;cursor:default;
}
.stat-card:hover{
  border-color:var(--orange);
  box-shadow:0 0 20px #ff6a0044;
  transform:translateY(-3px);
}
.stat-card::after{
  content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--orange),transparent);
  transform:scaleX(0);transition:transform .3s;
}
.stat-card:hover::after{transform:scaleX(1)}
.stat-value{
  font-family:'Bangers',cursive;font-size:2.5rem;
  background:linear-gradient(135deg,var(--yellow),var(--orange));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.stat-label{font-size:.75rem;color:#c8a878;letter-spacing:.15em;margin-top:.25rem;font-weight:700;text-transform:uppercase}

/* ── SECTION TITLE ── */
.section-title{
  font-family:'Bangers',cursive;font-size:1.5rem;
  color:var(--orange);letter-spacing:.2em;
  margin-bottom:1.5rem;padding-bottom:.5rem;
  border-bottom:2px solid rgba(255,106,0,.3);
  text-shadow:0 0 15px #ff6a0055;
}

/* ── TABS ── */
.tabs{display:flex;margin-bottom:2rem;gap:0}
.tab{
  padding:.75rem 1.5rem;cursor:pointer;
  border:1px solid rgba(255,106,0,.3);border-right:none;
  font-family:'Bangers',cursive;font-size:1rem;letter-spacing:.15em;
  color:#c8a878;transition:all .2s;text-transform:uppercase;
}
.tab:last-child{border-right:1px solid rgba(255,106,0,.3)}
.tab:hover{color:var(--yellow);background:rgba(255,106,0,.1)}
.tab.active{
  color:var(--orange);
  background:rgba(255,106,0,.15);
  border-color:var(--orange);
  box-shadow:inset 0 -2px 0 var(--orange);
}
.panel{display:none}.panel.active{display:block}
"""

DBZ_ANIMATIONS = """
/* ── HERO SECTION ── */
.hero{
  text-align:center;padding:4rem 2rem 2rem;
  position:relative;z-index:1;
}

/* ── DRAGON RADAR ── */
.dragon-radar{
  position:relative;width:140px;height:140px;margin:0 auto 2rem;
}
.radar-circle{
  position:absolute;inset:0;border-radius:50%;
  border:2px solid var(--orange);
  animation:radarping 2s ease-out infinite;
}
.radar-circle:nth-child(2){animation-delay:.5s;border-color:var(--yellow)}
.radar-circle:nth-child(3){animation-delay:1s;border-color:var(--red);opacity:.5}
@keyframes radarping{
  0%{transform:scale(.3);opacity:1}
  100%{transform:scale(1.5);opacity:0}
}
.radar-dot{
  position:absolute;top:50%;left:50%;
  width:16px;height:16px;border-radius:50%;
  background:radial-gradient(circle,#fff,var(--yellow),var(--orange));
  transform:translate(-50%,-50%);
  box-shadow:0 0 20px var(--yellow),0 0 40px var(--orange);
  animation:dotpulse 1s ease-in-out infinite alternate;
}
@keyframes dotpulse{0%{transform:translate(-50%,-50%) scale(1)}100%{transform:translate(-50%,-50%) scale(1.3)}}

/* ── MAIN TITLE ── */
.hero-title{
  font-family:'Bangers',cursive;
  font-size:clamp(2.5rem,8vw,5.5rem);
  letter-spacing:.1em;
  line-height:1;
  margin-bottom:.5rem;
  background:linear-gradient(135deg,#fff 0%,var(--yellow) 30%,var(--orange) 60%,var(--red) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  filter:drop-shadow(0 0 20px #ff6a0088);
  animation:titlepulse 3s ease-in-out infinite;
}
@keyframes titlepulse{
  0%,100%{filter:drop-shadow(0 0 20px #ff6a0088)}
  50%{filter:drop-shadow(0 0 40px #ffd70088) drop-shadow(0 0 60px #ff6a0066)}
}
.hero-subtitle{
  font-family:'Bangers',cursive;font-size:1.1rem;letter-spacing:.3em;
  color:var(--orange);margin-bottom:2rem;opacity:.8;
}

/* ── POWER LEVEL DISPLAY ── */
.power-display{
  display:inline-block;
  background:rgba(0,0,0,.7);
  border:2px solid var(--orange);
  padding:.75rem 2.5rem;border-radius:4px;
  margin-bottom:2rem;
  box-shadow:0 0 30px #ff6a0044,inset 0 0 20px rgba(255,106,0,.05);
  position:relative;overflow:hidden;
}
.power-display::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(90deg,transparent,rgba(255,215,0,.05),transparent);
  animation:scanline 2s linear infinite;
}
@keyframes scanline{0%{transform:translateX(-100%)}100%{transform:translateX(100%)}}
.power-label{font-size:.7rem;color:#c8a878;letter-spacing:.3em;margin-bottom:.25rem;font-weight:700;text-transform:uppercase}
.power-number{
  font-family:'Bangers',cursive;font-size:2.5rem;
  color:var(--yellow);letter-spacing:.1em;
  animation:numberflicker 4s ease-in-out infinite;
}
@keyframes numberflicker{
  0%,90%,100%{opacity:1}
  92%,96%{opacity:.8}
  94%,98%{opacity:1}
}

/* ── STATS BAR ── */
.stats-bar{
  display:flex;justify-content:center;gap:0;
  max-width:700px;margin:0 auto 2rem;
  border:1px solid rgba(255,106,0,.3);
  background:rgba(0,0,0,.5);
  border-radius:4px;overflow:hidden;
}
.stat{
  flex:1;text-align:center;padding:1.25rem 1rem;
  border-right:1px solid rgba(255,106,0,.2);
  transition:background .3s;
}
.stat:last-child{border-right:none}
.stat:hover{background:rgba(255,106,0,.08)}
.stat-value{font-family:'Bangers',cursive;font-size:2rem;color:var(--yellow)}
.stat-label{font-size:.7rem;color:#c8a878;letter-spacing:.2em;margin-top:.2rem;font-weight:700;text-transform:uppercase}

/* ── TIMER ── */
.timer-box{
  display:inline-block;
  background:rgba(0,0,0,.8);
  border:2px solid var(--orange);
  padding:1rem 2.5rem;border-radius:4px;
  margin-bottom:2rem;
  position:relative;
}
.timer-box::before,.timer-box::after{
  content:'◆';position:absolute;top:50%;transform:translateY(-50%);
  color:var(--orange);font-size:.6rem;
}
.timer-box::before{left:.5rem}
.timer-box::after{right:.5rem}
.timer-label{font-size:.65rem;color:#c8a878;letter-spacing:.3em;margin-bottom:.25rem;font-weight:700;text-transform:uppercase}
.timer{font-family:'Bangers',cursive;font-size:2.5rem;color:var(--yellow);letter-spacing:.1em}

/* ── SECTION ── */
.section{padding:2rem;max-width:1200px;margin:0 auto;position:relative;z-index:1}

/* ── CHALLENGE CARDS ── */
.challenges-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1rem}
.challenge-card{
  background:linear-gradient(135deg,rgba(18,8,0,.95),rgba(10,5,0,.98));
  border:1px solid rgba(255,106,0,.25);
  border-radius:4px;padding:1.25rem;cursor:pointer;
  transition:all .25s;position:relative;overflow:hidden;
}
.challenge-card::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,transparent,rgba(255,106,0,.05));
  opacity:0;transition:opacity .25s;
}
.challenge-card:hover{
  border-color:var(--orange);
  transform:translateY(-4px);
  box-shadow:0 8px 30px rgba(255,106,0,.25),0 0 0 1px rgba(255,106,0,.1);
}
.challenge-card:hover::before{opacity:1}

/* ── AURA EFFECT ON CARD HOVER ── */
.challenge-card::after{
  content:'';position:absolute;top:-50%;left:-50%;
  width:200%;height:200%;
  background:radial-gradient(circle,rgba(255,180,0,.08) 0%,transparent 60%);
  opacity:0;transition:opacity .3s;pointer-events:none;
}
.challenge-card:hover::after{opacity:1}

.ch-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.75rem}
.ch-name{font-family:'Bangers',cursive;font-size:1.1rem;color:#f5e6c8;letter-spacing:.05em}
.ch-points{
  font-family:'Bangers',cursive;font-size:1.3rem;
  color:var(--yellow);
  text-shadow:0 0 10px #ffd70066;
}
.ch-meta{display:flex;gap:.5rem;margin-bottom:.5rem;flex-wrap:wrap}
.tag{font-size:.7rem;padding:2px 8px;border-radius:2px;letter-spacing:.1em;font-weight:700}
.tag-cat{background:rgba(0,170,255,.15);color:var(--blue);border:1px solid rgba(0,170,255,.3)}
.tag-easy{background:rgba(0,255,100,.1);color:#00ff88;border:1px solid rgba(0,255,100,.3)}
.tag-medium{background:rgba(255,215,0,.1);color:var(--yellow);border:1px solid rgba(255,215,0,.3)}
.tag-hard{background:rgba(255,106,0,.15);color:var(--orange);border:1px solid rgba(255,106,0,.3)}
.tag-insane{background:rgba(255,26,26,.15);color:#ff4444;border:1px solid rgba(255,26,26,.3)}
.ch-desc{font-size:.82rem;color:#a08060;margin-top:.5rem;line-height:1.6}
.ch-solves{font-size:.75rem;color:#806040;margin-top:.5rem}
.ch-hints{font-size:.7rem;color:#c8a878;margin-top:.25rem}
.solved-badge{
  position:absolute;top:.75rem;right:.75rem;
  background:rgba(255,215,0,.15);
  border:1px solid rgba(255,215,0,.5);
  color:var(--yellow);font-size:.65rem;padding:2px 6px;border-radius:2px;
  font-family:'Bangers',cursive;letter-spacing:.1em;
}

/* ── MODAL ── */
.modal-overlay{
  position:fixed;inset:0;
  background:rgba(5,2,0,.92);
  display:none;align-items:center;justify-content:center;
  z-index:1000;backdrop-filter:blur(4px);
}
.modal-overlay.active{display:flex;animation:modalin .3s ease}
@keyframes modalin{0%{opacity:0}100%{opacity:1}}
.modal{
  background:linear-gradient(135deg,rgba(20,10,0,.99),rgba(10,5,0,.99));
  border:2px solid var(--orange);
  border-radius:4px;padding:2rem;
  max-width:560px;width:90%;max-height:90vh;overflow-y:auto;
  position:relative;
  box-shadow:0 0 60px rgba(255,106,0,.3),0 0 120px rgba(255,106,0,.1);
  animation:modalslide .3s ease;
}
@keyframes modalslide{0%{transform:translateY(-20px) scale(.97)}100%{transform:translateY(0) scale(1)}}
.modal::before{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--red),var(--orange),var(--yellow),var(--orange),var(--red));
  animation:modalshine 2s linear infinite;
}
@keyframes modalshine{0%{background-position:0% 50%}100%{background-position:200% 50%}}
.modal h2{
  font-family:'Bangers',cursive;font-size:1.8rem;letter-spacing:.1em;
  color:var(--orange);margin-bottom:.5rem;
  text-shadow:0 0 15px #ff6a0066;
}
.modal-desc{color:#a08060;margin-bottom:1rem;line-height:1.7;font-size:.9rem}

.flag-input{
  width:100%;padding:.75rem 1rem;
  background:rgba(255,106,0,.05);
  border:2px solid rgba(255,106,0,.3);
  color:var(--yellow);font-family:'Share Tech Mono',monospace;font-size:.95rem;
  border-radius:2px;outline:none;transition:all .2s;
  letter-spacing:.05em;
}
.flag-input:focus{
  border-color:var(--orange);
  box-shadow:0 0 20px rgba(255,106,0,.3);
  background:rgba(255,106,0,.08);
}
.flag-input::placeholder{color:#5a3a20}

.btn-row{display:flex;gap:.75rem;margin-top:1rem;flex-wrap:wrap}
.result-msg{margin-top:1rem;padding:.75rem 1rem;border-radius:2px;font-size:.95rem;display:none;font-weight:700}
.result-msg.correct{
  background:rgba(255,215,0,.15);border:1px solid rgba(255,215,0,.5);
  color:var(--yellow);animation:correctflash .5s ease;
}
.result-msg.wrong{
  background:rgba(255,26,26,.1);border:1px solid rgba(255,26,26,.4);
  color:#ff6666;animation:wrongshake .4s ease;
}
@keyframes correctflash{0%{background:rgba(255,215,0,.4)}100%{background:rgba(255,215,0,.15)}}
@keyframes wrongshake{0%,100%{transform:translateX(0)}25%{transform:translateX(-6px)}75%{transform:translateX(6px)}}

/* ── HINTS ── */
.hints-section{margin-top:1.5rem;border-top:1px solid rgba(255,106,0,.2);padding-top:1rem}
.hints-title{font-size:.75rem;color:#c8a878;letter-spacing:.2em;margin-bottom:.75rem;font-weight:700;text-transform:uppercase}
.hint-item{
  background:rgba(255,106,0,.05);
  border:1px solid rgba(255,106,0,.2);
  border-radius:2px;padding:.75rem;margin-bottom:.5rem;font-size:.85rem;
}
.hint-locked{display:flex;justify-content:space-between;align-items:center}
.hint-cost{color:#ff6666;font-size:.75rem;font-weight:700}
.hint-text{color:#c8a878;line-height:1.6}
.hint-unlock-btn{
  padding:.35rem .75rem;font-family:'Bangers',cursive;font-size:.85rem;
  border:1px solid var(--red);background:transparent;color:var(--red);
  cursor:pointer;border-radius:2px;transition:all .2s;letter-spacing:.1em;
}
.hint-unlock-btn:hover{background:rgba(255,26,26,.1);box-shadow:0 0 10px rgba(255,26,26,.3)}

/* ── LIVE FEED ── */
.live-feed{max-height:400px;overflow-y:auto}
.feed-item{
  padding:.6rem 0;border-bottom:1px solid rgba(255,106,0,.1);
  font-size:.88rem;display:flex;gap:.75rem;align-items:center;flex-wrap:wrap;
  transition:background .2s;
}
.feed-item:hover{background:rgba(255,106,0,.05);padding-left:.5rem}
.feed-time{color:#806040;flex-shrink:0;font-family:'Share Tech Mono',monospace;font-size:.8rem}
.feed-team{color:var(--yellow);font-weight:700}
.feed-pts{color:var(--orange);margin-left:auto;font-family:'Bangers',cursive;font-size:1.1rem}

/* ── SCOREBOARD ── */
.graph-container{
  background:rgba(0,0,0,.5);
  border:1px solid rgba(255,106,0,.2);
  border-radius:4px;padding:1.5rem;margin-bottom:2rem;
}
.graph-title{
  font-family:'Bangers',cursive;font-size:1.1rem;
  color:var(--orange);letter-spacing:.2em;margin-bottom:1rem;
}

/* ── USER BAR ── */
.user-bar{display:flex;align-items:center;gap:.75rem}
.user-badge{
  font-family:'Bangers',cursive;font-size:.9rem;letter-spacing:.1em;
  color:var(--yellow);border:1px solid rgba(255,215,0,.4);
  padding:4px 12px;border-radius:2px;
  background:rgba(255,215,0,.1);
}
.logout-btn{
  font-family:'Bangers',cursive;font-size:.85rem;letter-spacing:.1em;
  color:#c8a878;cursor:pointer;border:1px solid rgba(255,106,0,.3);
  padding:4px 12px;border-radius:2px;background:none;
  transition:all .2s;
}
.logout-btn:hover{color:var(--red);border-color:var(--red);box-shadow:0 0 10px rgba(255,26,26,.3)}

/* ── LOGIN PROMPT ── */
.login-prompt{
  background:rgba(255,106,0,.05);border:1px solid rgba(255,106,0,.2);
  border-radius:4px;padding:1.5rem;text-align:center;margin-bottom:2rem;
}
.login-prompt p{color:#a08060;margin-bottom:1rem;font-size:.95rem}
.login-prompt a{
  color:var(--orange);text-decoration:none;
  border:1px solid var(--orange);padding:.5rem 1.5rem;
  border-radius:2px;margin:0 .5rem;
  font-family:'Bangers',cursive;font-size:.95rem;letter-spacing:.1em;
  transition:all .2s;
}
.login-prompt a:hover{background:rgba(255,106,0,.15);box-shadow:0 0 15px rgba(255,106,0,.3)}

/* ── CERT BUTTON ── */
.cert-btn{
  background:none;border:1px solid rgba(255,215,0,.4);
  color:var(--yellow);padding:.4rem .8rem;
  font-family:'Bangers',cursive;font-size:.85rem;letter-spacing:.1em;
  cursor:pointer;border-radius:2px;transition:all .2s;
}
.cert-btn:hover{background:rgba(255,215,0,.1);box-shadow:0 0 10px rgba(255,215,0,.3)}

/* ── KI CHARGE ANIMATION ── */
@keyframes kicharge{
  0%{box-shadow:0 0 5px var(--orange)}
  50%{box-shadow:0 0 30px var(--yellow),0 0 60px var(--orange)}
  100%{box-shadow:0 0 5px var(--orange)}
}
.ki-charging{animation:kicharge 1s ease-in-out infinite}

/* ── DRAGON BALLS DECORATION ── */
.dragonballs{
  display:flex;justify-content:center;gap:.75rem;
  margin:1rem auto;
}
.dball{
  width:18px;height:18px;border-radius:50%;
  background:radial-gradient(circle at 35% 35%,#fff8e0,var(--yellow) 40%,var(--orange) 80%,#8b4500);
  box-shadow:0 0 8px rgba(255,215,0,.5);
  position:relative;transition:transform .2s;cursor:default;
}
.dball:hover{transform:scale(1.3);box-shadow:0 0 15px rgba(255,215,0,.8)}
.dball::after{
  content:'';position:absolute;
  background:rgba(255,50,0,.7);border-radius:50%;
}
.dball-1::after{width:3px;height:3px;top:50%;left:50%;transform:translate(-50%,-50%)}
.dball-2::after{width:4px;height:4px;top:40%;left:40%;box-shadow:4px 2px 0 rgba(255,50,0,.7)}
.dball-3::after{width:3px;height:3px;top:35%;left:35%;box-shadow:5px 0 0 rgba(255,50,0,.7),2px 5px 0 rgba(255,50,0,.7)}
.dball-4::after{width:3px;height:3px;top:33%;left:33%;box-shadow:5px 0 0 rgba(255,50,0,.7),0 5px 0 rgba(255,50,0,.7),5px 5px 0 rgba(255,50,0,.7)}
.dball-5::after{width:3px;height:3px;top:30%;left:30%;box-shadow:5px 0 0 rgba(255,50,0,.7),0 5px 0 rgba(255,50,0,.7),5px 5px 0 rgba(255,50,0,.7),2px 2px 0 rgba(255,50,0,.7)}
.dball-6::after{width:3px;height:3px;top:28%;left:28%;box-shadow:5px 0 0 rgba(255,50,0,.7),0 5px 0 rgba(255,50,0,.7),5px 5px 0 rgba(255,50,0,.7),0 2px 0 rgba(255,50,0,.7),5px 2px 0 rgba(255,50,0,.7)}
.dball-7::after{width:2px;height:2px;top:25%;left:25%;box-shadow:4px 0 0 rgba(255,50,0,.7),0 4px 0 rgba(255,50,0,.7),4px 4px 0 rgba(255,50,0,.7),2px 0 0 rgba(255,50,0,.7),0 2px 0 rgba(255,50,0,.7),4px 2px 0 rgba(255,50,0,.7),2px 4px 0 rgba(255,50,0,.7)}

/* ── SCROLLBAR ── */
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:#0a0500}
::-webkit-scrollbar-thumb{background:var(--orange);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--yellow)}

/* ── CATEGORY HEADER ── */
.cat-header{
  grid-column:1/-1;
  font-family:'Bangers',cursive;font-size:1.1rem;letter-spacing:.2em;
  color:var(--orange);padding:.5rem 0;
  border-bottom:1px solid rgba(255,106,0,.3);margin-bottom:.5rem;
  display:flex;align-items:center;gap:.75rem;
}
.cat-header::before{content:'◈';color:var(--yellow)}

/* ── KI BLAST PARTICLE ── */
.ki-particle{
  position:fixed;pointer-events:none;z-index:9999;
  border-radius:50%;
  background:radial-gradient(circle,#fff,var(--yellow),var(--orange));
  animation:kiblast .6s ease-out forwards;
}
@keyframes kiblast{
  0%{transform:scale(0);opacity:1}
  50%{opacity:.8}
  100%{transform:scale(3);opacity:0}
}

/* ── SCOUTER SCAN EFFECT ── */
.scouter-scan{
  position:fixed;top:0;left:0;right:0;bottom:0;
  pointer-events:none;z-index:9998;
  background:linear-gradient(0deg,transparent 48%,rgba(0,255,0,.03) 50%,transparent 52%);
  animation:scouterscan 4s linear infinite;
}
@keyframes scouterscan{0%{transform:translateY(-100%)}100%{transform:translateY(100%)}}

/* ── ADMIN GRID ── */
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:2rem}
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
    timerLabel.textContent = 'BATTLE BEGINS IN';
    timerEl.textContent = formatTime(start - now);
  } else if (now < end) {
    const diff = end - now;
    timerLabel.textContent = 'POWER REMAINING';
    timerEl.textContent = formatTime(diff);
    timerEl.style.color = diff < 3600000 ? 'var(--red)' : 'var(--yellow)';
  } else {
    timerLabel.textContent = 'BATTLE OVER';
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
<html lang="en">
<head><meta charset="UTF-8"><title>Login - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + DBZ_ANIMATIONS + """
.login-wrapper{
  min-height:100vh;display:flex;align-items:center;justify-content:center;
  position:relative;z-index:1;
}
.login-bg-text{
  position:fixed;font-family:'Bangers',cursive;font-size:20vw;
  color:rgba(255,106,0,.03);top:50%;left:50%;
  transform:translate(-50%,-50%);letter-spacing:.1em;
  pointer-events:none;z-index:0;white-space:nowrap;
}
</style>
</head>
<body>
<div class="scouter-scan"></div>
<div class="energy-lines">
  <span style="top:20%;width:60%;left:20%;animation-delay:0s;animation-duration:4s"></span>
  <span style="top:50%;width:40%;left:30%;animation-delay:1.5s;animation-duration:3s"></span>
  <span style="top:75%;width:70%;left:10%;animation-delay:2.5s;animation-duration:5s"></span>
</div>
<div class="login-bg-text">DBZ</div>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span> CTF</span></a>
  <nav>
    <a href="/login" class="active">LOGIN</a>
    <a href="/register">REGISTER</a>
  </nav>
</header>
<div class="login-wrapper">
  <div class="container" style="margin:0;width:100%">
    <div style="text-align:center;margin-bottom:2rem">
      <div class="dragonballs">
        <div class="dball dball-1"></div>
        <div class="dball dball-2"></div>
        <div class="dball dball-3"></div>
        <div class="dball dball-4"></div>
        <div class="dball dball-5"></div>
        <div class="dball dball-6"></div>
        <div class="dball dball-7"></div>
      </div>
    </div>
    <div class="card">
      <h2>⚡ WARRIOR LOGIN</h2>
      <div class="form-group">
        <label>TEAM NAME</label>
        <input type="text" id="team" placeholder="Enter your warrior name"/>
      </div>
      <div class="form-group">
        <label>PASSWORD</label>
        <div class="pw-wrap">
          <input type="password" id="password" placeholder="••••••••"/>
          <button class="pw-toggle" onclick="togglePw('password','eye1')" type="button">
            <span id="eye1">👁</span>
          </button>
        </div>
      </div>
      <button class="btn btn-full btn-ki" id="login-btn" onclick="login()">
        ⚡ POWER UP & LOGIN
      </button>
      <div class="text-center">
        <a href="/register" class="link">No account? Join the battle →</a>
      </div>
    </div>
  </div>
</div>
<script>
function togglePw(inputId, eyeId) {
  const input = document.getElementById(inputId);
  const eye = document.getElementById(eyeId);
  input.type = input.type === 'password' ? 'text' : 'password';
  eye.textContent = input.type === 'password' ? '👁' : '🙈';
}
function spawnKiParticle(x, y) {
  const p = document.createElement('div');
  p.className = 'ki-particle';
  p.style.cssText = `left:${x-10}px;top:${y-10}px;width:20px;height:20px`;
  document.body.appendChild(p);
  setTimeout(() => p.remove(), 600);
}
document.addEventListener('click', e => spawnKiParticle(e.clientX, e.clientY));
async function login() {
  const team = document.getElementById('team').value.trim();
  const password = document.getElementById('password').value;
  document.querySelectorAll('.alert').forEach(m => m.remove());
  if (!team || !password) return showAlert('⚠ Fill in all fields, warrior!', 'error');
  const btn = document.getElementById('login-btn');
  btn.textContent = '⚡ CHARGING KI...';
  btn.disabled = true;
  btn.classList.add('ki-charging');
  try {
    const r = await fetch('/api/v1/auth/login', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({team_name: team, password})
    });
    const data = await r.json();
    if (data.success) {
      localStorage.setItem('ctf_token', data.token);
      localStorage.setItem('ctf_team', data.team);
      localStorage.setItem('ctf_is_admin', data.is_admin === true ? 'true' : 'false');
      showAlert('🐉 POWER LEVEL MAXIMUM! Entering battle...', 'success');
      for(let i=0;i<8;i++) setTimeout(()=>spawnKiParticle(Math.random()*window.innerWidth,Math.random()*window.innerHeight),i*80);
      setTimeout(() => window.location.href = data.is_admin ? '/admin' : '/', 1000);
    } else {
      showAlert('💀 ' + (data.message || 'Login failed'), 'error');
      btn.textContent = '⚡ POWER UP & LOGIN';
      btn.disabled = false;
      btn.classList.remove('ki-charging');
    }
  } catch(e) {
    showAlert('⚠ Network error - try again', 'error');
    btn.textContent = '⚡ POWER UP & LOGIN';
    btn.disabled = false;
    btn.classList.remove('ki-charging');
  }
}
function showAlert(msg, type) {
  document.querySelector('.card').insertAdjacentHTML('afterbegin',
    `<div class="alert alert-${type}">${msg}</div>`);
}
document.addEventListener('keydown', e => { if (e.key === 'Enter') login(); });
</script>
</body></html>"""

REGISTER_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Register - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + DBZ_ANIMATIONS + """</style>
</head>
<body>
<div class="scouter-scan"></div>
<div class="energy-lines">
  <span style="top:15%;width:50%;left:25%;animation-delay:0s"></span>
  <span style="top:60%;width:60%;left:15%;animation-delay:2s"></span>
</div>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span> CTF</span></a>
  <nav><a href="/login">LOGIN</a><a href="/register" class="active">REGISTER</a></nav>
</header>
<div class="login-wrapper" style="display:flex;align-items:center;justify-content:center;min-height:calc(100vh - 80px);position:relative;z-index:1">
  <div class="container" style="margin:2rem auto;width:100%">
    <div style="text-align:center;margin-bottom:1.5rem">
      <div class="dragonballs">
        <div class="dball dball-1"></div><div class="dball dball-2"></div>
        <div class="dball dball-3"></div><div class="dball dball-4"></div>
        <div class="dball dball-5"></div><div class="dball dball-6"></div>
        <div class="dball dball-7"></div>
      </div>
    </div>
    <div class="card">
      <h2>🐉 JOIN THE BATTLE</h2>
      <div class="form-group"><label>TEAM NAME</label>
        <input type="text" id="name" placeholder="Choose your warrior name" maxlength="32"/></div>
      <div class="form-group"><label>EMAIL</label>
        <input type="email" id="email" placeholder="warrior@earth.com"/></div>
      <div class="form-group"><label>PASSWORD</label>
        <div class="pw-wrap">
          <input type="password" id="password" placeholder="min 8 characters"/>
          <button class="pw-toggle" onclick="togglePw('password','eye1')" type="button"><span id="eye1">👁</span></button>
        </div>
      </div>
      <div class="form-group"><label>CONFIRM PASSWORD</label>
        <div class="pw-wrap">
          <input type="password" id="confirm" placeholder="repeat password"/>
          <button class="pw-toggle" onclick="togglePw('confirm','eye2')" type="button"><span id="eye2">👁</span></button>
        </div>
      </div>
      <div class="form-group"><label>COUNTRY (optional)</label>
        <input type="text" id="country" placeholder="Planet Vegeta"/></div>
      <button class="btn btn-full btn-ki" id="reg-btn" onclick="register()">🐉 SUMMON THE DRAGON</button>
      <div class="text-center"><a href="/login" class="link">Already a warrior? Login →</a></div>
    </div>
  </div>
</div>
<script>
function togglePw(inputId, eyeId) {
  const input = document.getElementById(inputId);
  const eye = document.getElementById(eyeId);
  input.type = input.type === 'password' ? 'text' : 'password';
  eye.textContent = input.type === 'password' ? '👁' : '🙈';
}
function spawnKiParticle(x, y) {
  const p = document.createElement('div');
  p.className = 'ki-particle';
  p.style.cssText = `left:${x-10}px;top:${y-10}px;width:20px;height:20px`;
  document.body.appendChild(p);
  setTimeout(() => p.remove(), 600);
}
document.addEventListener('click', e => spawnKiParticle(e.clientX, e.clientY));
async function register() {
  const name = document.getElementById('name').value.trim();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const confirm = document.getElementById('confirm').value;
  const country = document.getElementById('country').value.trim();
  document.querySelectorAll('.alert').forEach(m => m.remove());
  if (!name || !email || !password) return showAlert('⚠ Fill in all required fields!', 'error');
  if (password !== confirm) return showAlert('⚠ Passwords do not match!', 'error');
  if (password.length < 8) return showAlert('⚠ Password must be at least 8 characters!', 'error');
  const btn = document.getElementById('reg-btn');
  btn.textContent = '🐉 GATHERING DRAGON BALLS...';
  btn.disabled = true;
  btn.classList.add('ki-charging');
  try {
    const r = await fetch('/api/v1/auth/register', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({team_name:name, email, password, country})
    });
    const data = await r.json();
    showAlert((data.success?'🐉 ':'⚠ ') + data.message, data.success ? 'success' : 'error');
    if (data.success) {
      for(let i=0;i<12;i++) setTimeout(()=>spawnKiParticle(Math.random()*window.innerWidth,Math.random()*window.innerHeight),i*60);
      setTimeout(() => window.location.href = '/login', 2500);
    } else {
      btn.textContent = '🐉 SUMMON THE DRAGON';
      btn.disabled = false;
      btn.classList.remove('ki-charging');
    }
  } catch(e) {
    showAlert('⚠ Network error', 'error');
    btn.textContent = '🐉 SUMMON THE DRAGON';
    btn.disabled = false;
    btn.classList.remove('ki-charging');
  }
}
function showAlert(msg, type) {
  document.querySelector('.card').insertAdjacentHTML('afterbegin',
    `<div class="alert alert-${type}">${msg}</div>`);
}
document.addEventListener('keydown', e => { if (e.key === 'Enter') register(); });
</script>
</body></html>"""

VERIFY_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Verify - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + DBZ_ANIMATIONS + """</style></head><body>
<header class="header"><a class="logo" href="/">{{ ctf_name }}<span> CTF</span></a></header>
<div style="display:flex;align-items:center;justify-content:center;min-height:calc(100vh - 80px);position:relative;z-index:1">
  <div class="container"><div class="card" style="text-align:center">
    <h2>⚡ EMAIL VERIFICATION</h2><br>
    {% if success %}
      <div class="alert alert-success">🐉 {{ message }}</div><br>
      <a href="/login" class="btn btn-ki">ENTER THE BATTLE →</a>
    {% else %}
      <div class="alert alert-error">💀 {{ message }}</div>
    {% endif %}
  </div></div>
</div></body></html>"""

ADMIN_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Admin - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + DBZ_ANIMATIONS + """</style></head><body>
<div class="scouter-scan"></div>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span> CTF</span></a>
  <nav>
    <a href="/">ARENA</a>
    <a href="/admin" class="active">COMMAND</a>
    <span class="power-level">👑 {{ admin_name }}</span>
    <button onclick="logout()" class="logout-btn">RETREAT</button>
  </nav>
</header>
<div class="wide">
  <div style="text-align:center;padding:1.5rem 0 1rem">
    <div style="font-family:'Bangers',cursive;font-size:2rem;color:var(--orange);letter-spacing:.2em;text-shadow:0 0 20px #ff6a0066">
      ⚡ COMMAND CENTER ⚡
    </div>
  </div>
  <div class="grid-4">
    <div class="stat-card"><div class="stat-value" id="stat-teams">-</div><div class="stat-label">Warriors</div></div>
    <div class="stat-card"><div class="stat-value" id="stat-challenges">-</div><div class="stat-label">Challenges</div></div>
    <div class="stat-card"><div class="stat-value" id="stat-solves">-</div><div class="stat-label">Victories</div></div>
    <div class="stat-card"><div class="stat-value" id="stat-verified">-</div><div class="stat-label">Verified</div></div>
  </div>
  <div class="tabs">
    <div class="tab active" onclick="switchTab('teams')" id="tab-teams">⚔ WARRIORS</div>
    <div class="tab" onclick="switchTab('challenges')" id="tab-challenges">🐉 CHALLENGES</div>
    <div class="tab" onclick="switchTab('solves')" id="tab-solves">⚡ BATTLE LOG</div>
  </div>
  <div class="panel active" id="panel-teams">
    <div class="section-title">⚔ ALL WARRIORS</div>
    <input id="search" placeholder="Search warrior..."
      style="padding:.5rem 1rem;background:rgba(255,106,0,.05);border:1px solid rgba(255,106,0,.3);color:#f5e6c8;font-family:'Rajdhani',sans-serif;border-radius:2px;width:300px;margin-bottom:1rem;outline:none"
      oninput="filterTeams()"/>
    <table>
      <thead><tr><th>WARRIOR</th><th>EMAIL</th><th>ORIGIN</th><th>POWER</th><th>VICTORIES</th><th>STATUS</th><th>ACTIONS</th></tr></thead>
      <tbody id="teams-body"></tbody>
    </table>
  </div>
  <div class="panel" id="panel-challenges">
    <div class="section-title">🐉 CHALLENGES</div>
    <table>
      <thead><tr><th>NAME</th><th>CATEGORY</th><th>POWER</th><th>DIFFICULTY</th><th>SOLVED</th><th>HINTS</th></tr></thead>
      <tbody id="challenges-body"></tbody>
    </table>
  </div>
  <div class="panel" id="panel-solves">
    <div class="section-title">⚡ BATTLE LOG</div>
    <table>
      <thead><tr><th>TIME</th><th>WARRIOR</th><th>CHALLENGE</th><th>POWER</th><th>FIRST BLOOD</th></tr></thead>
      <tbody id="solves-body"></tbody>
    </table>
  </div>
</div>
<script>
const token = localStorage.getItem('ctf_token');
const isAdmin = localStorage.getItem('ctf_is_admin') === 'true';
if (!token || !isAdmin) window.location.href = '/login';
let allTeams = [];
function spawnKiParticle(x,y){const p=document.createElement('div');p.className='ki-particle';p.style.cssText=`left:${x-10}px;top:${y-10}px;width:20px;height:20px`;document.body.appendChild(p);setTimeout(()=>p.remove(),600)}
document.addEventListener('click',e=>spawnKiParticle(e.clientX,e.clientY));
async function api(path, opts={}) {
  const headers = {'Content-Type':'application/json','Authorization':`Bearer ${token}`};
  const r = await fetch('/api/v1'+path, {headers, ...opts});
  if (r.status===401||r.status===403){window.location.href='/login';return{}}
  return r.json();
}
async function loadStats() {
  const [teams, challenges, feed] = await Promise.all([api('/admin/teams'),api('/challenges'),api('/feed')]);
  allTeams = teams.teams||[];
  document.getElementById('stat-teams').textContent = allTeams.length;
  document.getElementById('stat-challenges').textContent = (challenges.challenges||[]).length;
  document.getElementById('stat-solves').textContent = (feed.events||[]).length;
  document.getElementById('stat-verified').textContent = allTeams.filter(t=>t.verified).length;
  renderTeams(allTeams);
  document.getElementById('challenges-body').innerHTML=(challenges.challenges||[]).map(c=>`<tr>
    <td style="font-family:'Bangers',cursive;font-size:1rem;color:#f5e6c8">${c.name}</td>
    <td><span class="badge badge-blue">${c.category}</span></td>
    <td style="color:var(--yellow);font-family:'Bangers',cursive;font-size:1.1rem">${c.points}</td>
    <td>${c.difficulty}</td><td>${c.solves}</td>
    <td style="color:#c8a878">${c.hints?.length||0} hints</td>
  </tr>`).join('');
  document.getElementById('solves-body').innerHTML=(feed.events||[]).map(e=>`<tr>
    <td style="color:#806040;font-size:.8rem">${e.timestamp}</td>
    <td style="color:var(--yellow);font-weight:700">${e.team}</td>
    <td>${e.challenge}</td>
    <td style="color:var(--orange);font-family:'Bangers',cursive">+${e.points}</td>
    <td>${e.first_blood?'🩸 FIRST BLOOD':''}</td>
  </tr>`).join('');
}
function renderTeams(teams){
  document.getElementById('teams-body').innerHTML=teams.map(t=>`<tr>
    <td style="color:var(--yellow);font-family:'Bangers',cursive;font-size:1rem">${t.name}</td>
    <td style="color:#806040;font-size:.8rem">${t.email}</td>
    <td>${t.country||'-'}</td>
    <td style="color:var(--orange);font-family:'Bangers',cursive;font-size:1.1rem">${t.score}</td>
    <td>${t.solves}</td>
    <td>
      ${t.verified?'<span class="badge badge-green">VERIFIED</span>':'<span class="badge badge-yellow">UNVERIFIED</span>'}
      ${t.banned?'<span class="badge badge-red" style="margin-left:4px">BANNED</span>':''}
    </td>
    <td style="display:flex;gap:4px">
      <button class="btn btn-sm ${t.banned?'btn-blue':'btn-red'}" onclick="${t.banned?`unbanTeam('${t.name}')`:`banTeam('${t.name}')`}">${t.banned?'UNBAN':'BAN'}</button>
      <button class="btn btn-sm" onclick="resetScore('${t.name}')">RESET</button>
      <button class="btn btn-sm btn-red" onclick="deleteTeam('${t.name}')">DELETE</button>
    </td>
  </tr>`).join('');
}
function filterTeams(){const q=document.getElementById('search').value.toLowerCase();renderTeams(allTeams.filter(t=>t.name.toLowerCase().includes(q)||t.email.toLowerCase().includes(q)))}
async function banTeam(name){if(!confirm(`Ban warrior "${name}"?`))return;await api('/admin/teams/ban',{method:'POST',body:JSON.stringify({team_name:name})});loadStats()}
async function unbanTeam(name){if(!confirm(`Unban warrior "${name}"?`))return;await api('/admin/teams/unban',{method:'POST',body:JSON.stringify({team_name:name})});loadStats()}
async function resetScore(name){if(!confirm(`Reset power level for "${name}"?`))return;await api('/admin/teams/reset',{method:'POST',body:JSON.stringify({team_name:name})});loadStats()}
async function deleteTeam(name){if(!confirm(`PERMANENTLY DELETE warrior "${name}"?`))return;await api('/admin/teams/delete',{method:'POST',body:JSON.stringify({team_name:name})});loadStats()}
function switchTab(name){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));document.getElementById('tab-'+name).classList.add('active');document.getElementById('panel-'+name).classList.add('active')}
function logout(){fetch('/api/v1/auth/logout',{method:'POST',headers:{'Authorization':`Bearer ${token}`}});localStorage.clear();window.location.href='/login'}
loadStats();
setInterval(loadStats,30000);
</script></body></html>"""

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{{ ctf_name }}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-adapter-moment/1.0.1/chartjs-adapter-moment.min.js"></script>
<style>""" + BASE_STYLE + DBZ_ANIMATIONS + """</style>
</head>
<body>
<div class="scouter-scan"></div>
<div class="energy-lines">
  <span style="top:10%;width:80%;left:10%;animation-delay:0s;animation-duration:5s"></span>
  <span style="top:35%;width:50%;left:25%;animation-delay:1s;animation-duration:4s"></span>
  <span style="top:60%;width:70%;left:15%;animation-delay:2s;animation-duration:6s"></span>
  <span style="top:85%;width:60%;left:20%;animation-delay:3s;animation-duration:4.5s"></span>
</div>

<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span> CTF</span></a>
  <nav>
    <a href="#" onclick="switchTab('challenges')">⚔ CHALLENGES</a>
    <a href="#" onclick="switchTab('scoreboard')">🏆 POWER RANKS</a>
    <a href="#" onclick="switchTab('feed')">⚡ BATTLE FEED</a>
    <div class="user-bar" id="user-bar" style="display:none">
      <span class="user-badge" id="user-name"></span>
      <a id="admin-link" href="/admin" style="display:none;color:var(--red);font-family:'Bangers',cursive;font-size:.9rem;letter-spacing:.1em;text-decoration:none;border:1px solid rgba(255,26,26,.4);padding:4px 10px;border-radius:2px;">👑 COMMAND</a>
      <button class="logout-btn" onclick="logout()">RETREAT</button>
    </div>
    <div id="auth-links">
      <a href="/login">LOGIN</a>
      <a href="/register">REGISTER</a>
    </div>
  </nav>
</header>

<div class="hero">
  <div class="dragon-radar">
    <div class="radar-circle"></div>
    <div class="radar-circle"></div>
    <div class="radar-circle"></div>
    <div class="radar-dot"></div>
  </div>
  <div class="dragonballs">
    <div class="dball dball-1"></div><div class="dball dball-2"></div>
    <div class="dball dball-3"></div><div class="dball dball-4"></div>
    <div class="dball dball-5"></div><div class="dball dball-6"></div>
    <div class="dball dball-7"></div>
  </div>
  <h1 class="hero-title">{{ ctf_name }}</h1>
  <div class="hero-subtitle">{{ ctf_description }}</div>
  <div class="power-display">
    <div class="power-label">🐉 YOUR POWER LEVEL</div>
    <div class="power-number" id="power-counter">LOADING...</div>
  </div>
  <div class="timer-box">
    <div class="timer-label" id="timer-label">POWER REMAINING</div>
    <div class="timer" id="timer">--:--:--</div>
  </div>
  <div class="stats-bar">
    <div class="stat"><div class="stat-value" id="stat-challenges">-</div><div class="stat-label">⚔ Challenges</div></div>
    <div class="stat"><div class="stat-value" id="stat-teams">-</div><div class="stat-label">🥊 Warriors</div></div>
    <div class="stat"><div class="stat-value" id="stat-solves">-</div><div class="stat-label">💥 Victories</div></div>
  </div>
</div>

<div class="section">
  <div class="tabs">
    <div class="tab active" onclick="switchTab('challenges')" id="tab-challenges">⚔ CHALLENGES</div>
    <div class="tab" onclick="switchTab('scoreboard')" id="tab-scoreboard">🏆 POWER RANKS</div>
    <div class="tab" onclick="switchTab('feed')" id="tab-feed">⚡ BATTLE FEED</div>
  </div>

  <div class="panel active" id="panel-challenges">
    <div class="section-title">⚔ BATTLE CHALLENGES</div>
    <div id="login-prompt-box"></div>
    <div class="challenges-grid" id="challenges-grid">
      <div style="color:#806040;padding:2rem;font-family:'Bangers',cursive;font-size:1.2rem;letter-spacing:.1em">⚡ LOADING CHALLENGES...</div>
    </div>
  </div>

  <div class="panel" id="panel-scoreboard">
    <div class="section-title">🏆 POWER RANKINGS</div>
    <div class="graph-container">
      <div class="graph-title">⚡ POWER LEVEL PROGRESSION</div>
      <canvas id="scoreGraph" height="120"></canvas>
    </div>
    <table>
      <thead><tr><th>RANK</th><th>WARRIOR</th><th>POWER LEVEL</th><th>VICTORIES</th><th>LAST BATTLE</th><th></th></tr></thead>
      <tbody id="scoreboard-body"></tbody>
    </table>
  </div>

  <div class="panel" id="panel-feed">
    <div class="section-title">⚡ LIVE BATTLE FEED</div>
    <div class="live-feed" id="live-feed"></div>
  </div>
</div>

<div class="modal-overlay" id="modal">
  <div class="modal">
    <h2 id="modal-title">⚡ SUBMIT FLAG</h2>
    <p class="modal-desc" id="modal-desc"></p>
    <input class="flag-input" id="flag-input" placeholder="CTF{...}" type="text"/>
    <div class="btn-row">
      <button class="btn btn-ki" onclick="submitFlag()">⚡ RELEASE KI BLAST</button>
      <button class="btn btn-red" onclick="closeModal()">💀 RETREAT</button>
    </div>
    <div class="result-msg" id="result-msg"></div>
    <div class="hints-section" id="hints-section"></div>
  </div>
</div>

<script>
let currentChallenge = null;
let scoreChart = null;
const token = localStorage.getItem('ctf_token');
const team = localStorage.getItem('ctf_team');
const isAdmin = localStorage.getItem('ctf_is_admin') === 'true';

if (token && team) {
  document.getElementById('user-bar').style.display = 'flex';
  document.getElementById('user-name').textContent = '⚡ ' + team;
  document.getElementById('auth-links').style.display = 'none';
  if (isAdmin) document.getElementById('admin-link').style.display = 'inline-block';
}

// ── KI BLAST CURSOR ──
function spawnKiParticle(x, y) {
  const p = document.createElement('div');
  p.className = 'ki-particle';
  const size = 10 + Math.random() * 15;
  p.style.cssText = `left:${x-size/2}px;top:${y-size/2}px;width:${size}px;height:${size}px`;
  document.body.appendChild(p);
  setTimeout(() => p.remove(), 600);
}
document.addEventListener('click', e => {
  spawnKiParticle(e.clientX, e.clientY);
  for(let i=0;i<3;i++) setTimeout(()=>spawnKiParticle(e.clientX+(Math.random()-0.5)*40,e.clientY+(Math.random()-0.5)*40),i*80);
});

// ── POWER COUNTER ANIMATION ──
function animatePowerCounter(target) {
  const el = document.getElementById('power-counter');
  if (!target || target === 0) { el.textContent = 'SCOUTING...'; return; }
  let current = 0;
  const step = Math.ceil(target / 60);
  const interval = setInterval(() => {
    current = Math.min(current + step, target);
    el.textContent = current.toLocaleString();
    if (current >= target) clearInterval(interval);
  }, 16);
}

async function api(path, opts={}) {
  const headers = {'Content-Type':'application/json'};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return (await fetch('/api/v1'+path, {headers, ...opts})).json();
}

async function loadChallenges() {
  const data = await api('/challenges');
  const myData = token ? await api('/me/solves') : {solves:[]};
  const mySolves = new Set((myData.solves||[]).map(s=>s.challenge_id));
  const grid = document.getElementById('challenges-grid');
  const prompt = document.getElementById('login-prompt-box');
  if (!token) {
    prompt.innerHTML = `<div class="login-prompt">
      <p>⚡ Login to submit flags and compete for the Dragon Balls!</p>
      <a href="/login">⚡ LOGIN</a><a href="/register">🐉 REGISTER</a>
    </div>`;
  }
  if (!data.challenges?.length) {
    grid.innerHTML = '<div style="color:#806040;padding:2rem;font-family:Bangers,cursive;letter-spacing:.1em">No challenges yet. The Dragon awaits...</div>';
    return;
  }
  document.getElementById('stat-challenges').textContent = data.challenges.length;
  const grouped = {};
  data.challenges.forEach(ch => {
    if (!grouped[ch.category]) grouped[ch.category] = [];
    grouped[ch.category].push(ch);
  });
  grid.innerHTML = '';
  Object.entries(grouped).sort().forEach(([cat, chs]) => {
    const hdr = document.createElement('div');
    hdr.className = 'cat-header';
    hdr.textContent = cat.toUpperCase();
    grid.appendChild(hdr);
    chs.sort((a,b)=>a.points-b.points).forEach(ch => {
      const solved = mySolves.has(ch.id);
      const card = document.createElement('div');
      card.className = 'challenge-card';
      if (solved) card.style.borderColor = 'rgba(255,215,0,.5)';
      card.innerHTML = `
        ${solved ? '<div class="solved-badge">✓ CONQUERED</div>' : ''}
        <div class="ch-header">
          <div class="ch-name">${ch.name}</div>
          <div class="ch-points">${ch.points} PL</div>
        </div>
        <div class="ch-meta">
          <span class="tag tag-cat">${ch.category}</span>
          <span class="tag tag-${ch.difficulty}">${ch.difficulty.toUpperCase()}</span>
        </div>
        <div class="ch-desc">${ch.description||''}</div>
        <div class="ch-solves">⚔ ${ch.solves} warrior${ch.solves!==1?'s':''} conquered</div>
        ${ch.hints?.length ? `<div class="ch-hints">💡 ${ch.hints.length} hints available</div>` : ''}`;
      card.onclick = () => token ? openModal(ch) : window.location.href='/login';
      grid.appendChild(card);
    });
  });
}

async function loadScoreboard() {
  const data = await api('/scoreboard');
  document.getElementById('stat-teams').textContent = data.scores?.length||0;
  const tbody = document.getElementById('scoreboard-body');
  if (!data.scores?.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="color:#806040;padding:1rem;font-family:Bangers,cursive">No warriors yet. Be the first!</td></tr>';
    return;
  }
  const ranks = ['🥇','🥈','🥉'];
  tbody.innerHTML = data.scores.map((e,i)=>`<tr>
    <td style="font-family:'Bangers',cursive;font-size:1.3rem;color:${i===0?'#ffd700':i===1?'#c0c0c0':i===2?'#cd7f32':'#f5e6c8'}">${ranks[i]||(i+1)}</td>
    <td style="font-family:'Bangers',cursive;font-size:1rem;color:var(--yellow)">${e.team}</td>
    <td style="font-family:'Bangers',cursive;font-size:1.2rem;color:var(--orange)">${e.score.toLocaleString()}</td>
    <td>${e.solves}</td>
    <td style="color:#806040;font-size:.8rem">${e.last_solve}</td>
    <td><button class="cert-btn" onclick="getCertificate('${e.team}','${i+1}')">🏆 CERT</button></td>
  </tr>`).join('');
  await drawScoreGraph(data.scores.slice(0,5));
  if (data.scores.length) animatePowerCounter(data.scores[0].score);
}

async function drawScoreGraph(topTeams) {
  const timelines = await Promise.all(topTeams.map(t=>api(`/scoreboard/timeline?team=${encodeURIComponent(t.team)}`)));
  const colors = ['#ffd700','#ff6a00','#ff1a1a','#00aaff','#aa00ff'];
  const datasets = topTeams.map((t,i)=>({
    label: t.team,
    data: (timelines[i].timeline||[]).map(p=>({x:p.time*1000,y:p.total})),
    borderColor: colors[i], backgroundColor: colors[i]+'22',
    borderWidth: 2, pointRadius: 3, tension: 0.3, fill: false,
  }));
  const ctx = document.getElementById('scoreGraph').getContext('2d');
  if (scoreChart) scoreChart.destroy();
  scoreChart = new Chart(ctx, {
    type:'line', data:{datasets},
    options:{
      responsive:true, interaction:{mode:'index',intersect:false},
      plugins:{
        legend:{labels:{color:'#c8a878',font:{family:'Rajdhani',weight:'700'},boxWidth:12}},
        tooltip:{backgroundColor:'#120800',borderColor:'#ff6a0066',borderWidth:1,titleColor:'#ffd700',bodyColor:'#f5e6c8'}
      },
      scales:{
        x:{type:'time',time:{unit:'hour'},ticks:{color:'#806040',font:{family:'Share Tech Mono',size:10}},grid:{color:'rgba(255,106,0,.1)'}},
        y:{ticks:{color:'#806040',font:{family:'Share Tech Mono',size:10}},grid:{color:'rgba(255,106,0,.1)'}}
      }
    }
  });
}

async function loadFeed() {
  const data = await api('/feed');
  const feed = document.getElementById('live-feed');
  if (!data.events?.length) {
    feed.innerHTML = '<div style="color:#806040;padding:1rem;font-family:Bangers,cursive;letter-spacing:.1em">No battles yet. Be the first warrior!</div>';
    return;
  }
  document.getElementById('stat-solves').textContent = data.events.length;
  feed.innerHTML = data.events.map(e=>`
    <div class="feed-item">
      <span class="feed-time">[${e.timestamp}]</span>
      <span class="feed-team">⚡ ${e.team}</span>
      <span style="color:#806040">conquered</span>
      <span style="color:#f5e6c8">${e.challenge}</span>
      ${e.first_blood?'<span style="color:var(--red)">🩸 FIRST BLOOD</span>':''}
      <span class="feed-pts">+${e.points} PL</span>
    </div>`).join('');
}

async function openModal(ch) {
  currentChallenge = ch;
  document.getElementById('modal-title').textContent = '⚡ ' + ch.name;
  document.getElementById('modal-desc').textContent = ch.description||'Defeat this challenge and claim your power!';
  document.getElementById('flag-input').value = '';
  document.getElementById('result-msg').style.display = 'none';
  await loadHints(ch);
  document.getElementById('modal').classList.add('active');
  setTimeout(()=>document.getElementById('flag-input').focus(),100);
}

async function loadHints(ch) {
  const section = document.getElementById('hints-section');
  if (!ch.hints?.length) { section.innerHTML=''; return; }
  const unlocked = token ? await api(`/hints/${ch.id}`) : {unlocked:[]};
  const unlockedSet = new Set((unlocked.unlocked||[]).map(h=>h.hint_index));
  section.innerHTML = `<div class="hints-title">💡 SENSEI HINTS (${ch.hints.length} available)</div>` +
    ch.hints.map((hint,i) => {
      const cost = Math.floor(ch.points * 0.1 * (i+1));
      if (unlockedSet.has(i)) {
        return `<div class="hint-item">
          <div style="font-size:.7rem;color:#c8a878;margin-bottom:.35rem">HINT ${i+1} — UNLOCKED 💡</div>
          <div class="hint-text">${unlocked.unlocked.find(h=>h.hint_index===i)?.text||''}</div>
        </div>`;
      }
      return `<div class="hint-item">
        <div class="hint-locked">
          <span style="font-size:.85rem;color:#c8a878">Hint ${i+1}</span>
          <div style="display:flex;align-items:center;gap:.75rem">
            <span class="hint-cost">-${cost} PL</span>
            <button class="hint-unlock-btn" onclick="unlockHint('${ch.id}',${i},${cost})">UNLOCK</button>
          </div>
        </div>
      </div>`;
    }).join('');
}

async function unlockHint(challengeId, hintIndex, cost) {
  if (!token) return window.location.href='/login';
  if (!confirm(`Sacrifice ${cost} power level for this hint?`)) return;
  const r = await api('/hints/unlock', {method:'POST', body:JSON.stringify({challenge_id:challengeId,hint_index:hintIndex})});
  if (r.success) await loadHints(currentChallenge);
  else alert(r.message||'Failed to unlock hint');
}

function closeModal() {
  document.getElementById('modal').classList.remove('active');
  currentChallenge = null;
}

async function submitFlag() {
  if (!currentChallenge) return;
  const flag = document.getElementById('flag-input').value.trim();
  if (!flag) return;
  const btn = document.querySelector('.btn-ki');
  btn.textContent = '⚡ CHARGING...';
  btn.disabled = true;
  const r = await fetch('/api/v1/submit', {
    method:'POST',
    headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`},
    body: JSON.stringify({challenge_id:currentChallenge.id, flag, team})
  });
  const data = await r.json();
  btn.textContent = '⚡ RELEASE KI BLAST';
  btn.disabled = false;
  const msg = document.getElementById('result-msg');
  msg.style.display = 'block';
  msg.className = 'result-msg '+(data.correct?'correct':'wrong');
  msg.textContent = data.correct ? '🐉 CHALLENGE CONQUERED! POWER LEVEL INCREASING!' : '💀 ' + data.message;
  if (data.correct) {
    for(let i=0;i<15;i++) setTimeout(()=>spawnKiParticle(Math.random()*window.innerWidth,Math.random()*window.innerHeight),i*60);
    setTimeout(()=>{closeModal();loadChallenges();loadScoreboard();loadFeed();},2000);
  }
}

function getCertificate(teamName, rank) {
  window.open(`/certificate/${teamName}?rank=${rank}`, '_blank');
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
  fetch('/api/v1/auth/logout',{method:'POST',headers:{'Authorization':`Bearer ${token}`}});
  localStorage.clear();
  window.location.href='/login';
}

document.getElementById('flag-input')?.addEventListener('keydown',e=>{if(e.key==='Enter')submitFlag()});
document.getElementById('modal')?.addEventListener('click',e=>{if(e.target===document.getElementById('modal'))closeModal()});

loadChallenges();
loadFeed();
setInterval(()=>{loadScoreboard();loadFeed();},30000);
</script>
<script>""" + TIMER_JS + """</script>
</body></html>"""

CERT_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Certificate - {{ team }}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Rajdhani:wght@400;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{
  background:radial-gradient(ellipse at center,#1a0800 0%,#0a0300 60%,#050100 100%);
  display:flex;align-items:center;justify-content:center;
  min-height:100vh;padding:2rem;font-family:'Rajdhani',sans-serif;
}
.cert{
  background:linear-gradient(135deg,rgba(25,12,0,.98),rgba(10,5,0,.99));
  border:3px solid #ff6a00;border-radius:8px;padding:4rem;
  max-width:800px;width:100%;text-align:center;position:relative;
  box-shadow:0 0 80px rgba(255,106,0,.3),0 0 160px rgba(255,106,0,.1);
}
.cert::before{content:'';position:absolute;inset:10px;border:1px solid rgba(255,215,0,.2);border-radius:4px;pointer-events:none}
.corner{position:absolute;width:24px;height:24px;border-color:#ffd700;border-style:solid}
.corner-tl{top:18px;left:18px;border-width:3px 0 0 3px}
.corner-tr{top:18px;right:18px;border-width:3px 3px 0 0}
.corner-bl{bottom:18px;left:18px;border-width:0 0 3px 3px}
.corner-br{bottom:18px;right:18px;border-width:0 3px 3px 0}
.cert-logo{font-family:'Bangers',cursive;font-size:1rem;color:rgba(255,106,0,.6);letter-spacing:.3em;margin-bottom:2rem}
.cert-title{font-family:'Bangers',cursive;font-size:3rem;font-weight:900;
  background:linear-gradient(135deg,#fff,#ffd700,#ff6a00);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  margin-bottom:.5rem;letter-spacing:.1em;}
.cert-subtitle{color:rgba(255,215,0,.7);font-size:.9rem;letter-spacing:.3em;margin-bottom:3rem;font-weight:700;text-transform:uppercase}
.cert-text{color:#a08060;font-size:.95rem;margin-bottom:.75rem;letter-spacing:.05em}
.cert-name{font-family:'Bangers',cursive;font-size:2.5rem;color:#fff;margin:1rem 0;
  padding:.75rem 2rem;border:2px solid rgba(255,215,0,.5);display:inline-block;
  background:rgba(255,215,0,.05);border-radius:4px;letter-spacing:.1em;
  text-shadow:0 0 20px rgba(255,215,0,.5);}
.cert-rank{font-family:'Bangers',cursive;font-size:3.5rem;color:#ffd700;margin:1rem 0;
  text-shadow:0 0 30px rgba(255,215,0,.6)}
.cert-details{display:flex;justify-content:center;gap:3rem;margin:2rem 0;padding:1.5rem;
  border-top:1px solid rgba(255,106,0,.3);border-bottom:1px solid rgba(255,106,0,.3)}
.cert-detail-value{font-family:'Bangers',cursive;font-size:1.8rem;color:#ffd700}
.cert-detail-label{font-size:.7rem;color:#806040;letter-spacing:.15em;margin-top:.25rem;font-weight:700;text-transform:uppercase}
.cert-footer{margin-top:2rem;color:#5a3a20;font-size:.75rem;letter-spacing:.1em}
.cert-id{color:#3a2010;font-size:.65rem;margin-top:.5rem}
.print-btn{margin-top:2rem;padding:.75rem 2rem;background:transparent;
  border:2px solid #ff6a00;color:#ffd700;font-family:'Bangers',cursive;
  font-size:1rem;cursor:pointer;border-radius:2px;letter-spacing:.15em;transition:all .2s}
.print-btn:hover{background:rgba(255,106,0,.15);box-shadow:0 0 20px rgba(255,106,0,.4)}
.dragonballs{display:flex;justify-content:center;gap:.75rem;margin:1rem 0}
.dball{width:20px;height:20px;border-radius:50%;
  background:radial-gradient(circle at 35% 35%,#fff8e0,#ffd700 40%,#ff6a00 80%,#8b4500);
  box-shadow:0 0 10px rgba(255,215,0,.5)}
@media print{.print-btn{display:none}}
</style>
</head>
<body>
<div class="cert">
  <div class="corner corner-tl"></div><div class="corner corner-tr"></div>
  <div class="corner corner-bl"></div><div class="corner corner-br"></div>
  <div class="cert-logo">🐉 {{ ctf_name | upper }} // CTF 🐉</div>
  <div class="dragonballs">
    <div class="dball"></div><div class="dball"></div><div class="dball"></div>
    <div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div>
  </div>
  <div class="cert-title">CERTIFICATE</div>
  <div class="cert-subtitle">⚡ Of Warrior Achievement ⚡</div>
  <div class="cert-text">This certifies that the mighty warrior</div>
  <div class="cert-name">{{ team }}</div>
  <div class="cert-text">has proven their power in</div>
  <div class="cert-text" style="color:#ff6a00;font-size:1.2rem;font-family:'Bangers',cursive;letter-spacing:.1em">{{ ctf_name }}</div>
  <div class="cert-rank">{{ rank_emoji }} RANK #{{ rank }}</div>
  <div class="cert-details">
    <div class="cert-detail"><div class="cert-detail-value">{{ score }}</div><div class="cert-detail-label">⚡ Power Level</div></div>
    <div class="cert-detail"><div class="cert-detail-value">{{ solves }}</div><div class="cert-detail-label">⚔ Victories</div></div>
    <div class="cert-detail"><div class="cert-detail-value">{{ rank }}</div><div class="cert-detail-label">🏆 Final Rank</div></div>
  </div>
  <div class="cert-footer">🐉 {{ ctf_name }} — {{ date }} 🐉</div>
  <div class="cert-id">Certificate ID: {{ cert_id }}</div>
  <button class="print-btn" onclick="window.print()">🖨️ CLAIM YOUR SCROLL</button>
</div>
</body></html>"""


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

    @app.route("/")
    def index():
        return render_template_string(INDEX_HTML,
            ctf_name=config.ctf_name, ctf_description=config.ctf_description,
            start_time=config.start_time, end_time=config.end_time)

    @app.route("/login")
    def login_page():
        return render_template_string(LOGIN_HTML, ctf_name=config.ctf_name)

    @app.route("/register")
    def register_page():
        return render_template_string(REGISTER_HTML, ctf_name=config.ctf_name)

    @app.route("/verify/<token>")
    def verify_email(token):
        result = auth.verify_email(token)
        return render_template_string(VERIFY_HTML,
            ctf_name=config.ctf_name, success=result.success, message=result.message)

    @app.route("/admin")
    def admin_page():
        return render_template_string(ADMIN_HTML,
            ctf_name=config.ctf_name, admin_name=config.admin_username)

    @app.route("/certificate/<team_name>")
    def certificate(team_name):
        import hashlib
        from datetime import datetime
        rank = int(request.args.get("rank", 1))
        info = auth.get_team_info(team_name)
        score = info.get("score", 0) if info else 0
        solves = info.get("solves", 0) if info else 0
        rank_emojis = {1:"🥇", 2:"🥈", 3:"🥉"}
        cert_id = hashlib.md5(f"{team_name}{rank}{config.ctf_name}".encode()).hexdigest()[:12].upper()
        return render_template_string(CERT_HTML,
            ctf_name=config.ctf_name, team=team_name,
            rank=rank, rank_emoji=rank_emojis.get(rank, "🏅"),
            score=score, solves=solves,
            date=datetime.now().strftime("%B %d, %Y"), cert_id=cert_id)

    @app.route("/api/v1/auth/register", methods=["POST"])
    @require_json
    def api_register():
        try:
            d = request.get_json()
            result = auth.register(d.get("team_name","").strip(), d.get("email","").strip().lower(), d.get("password",""), d.get("country","").strip())
            return jsonify({"success": result.success, "message": result.message})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

    @app.route("/api/v1/auth/login", methods=["POST"])
    @require_json
    def api_login():
        try:
            d = request.get_json()
            result = auth.login(d.get("team_name","").strip(), d.get("password",""), request.remote_addr)
            is_admin = auth.is_admin(result.team) if result.success else False
            return jsonify({"success": result.success, "message": result.message, "token": result.token, "team": result.team, "is_admin": is_admin})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

    @app.route("/api/v1/auth/logout", methods=["POST"])
    def api_logout():
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        auth.logout(token)
        return jsonify({"success": True})

    @app.route("/api/v1/auth/resend", methods=["POST"])
    @require_json
    def api_resend():
        try:
            d = request.get_json()
            result = auth.resend_verification(d.get("email","").strip().lower())
            return jsonify({"success": result.success, "message": result.message})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

    @app.route("/api/v1/challenges")
    def api_challenges():
        try:
            challenges = manager.list_challenges()
            result = []
            for c in challenges:
                hints = c.hints if isinstance(c.hints, list) else []
                result.append({"id": c.id, "name": c.name, "category": c.category, "points": c.points, "difficulty": c.difficulty, "description": c.description, "solves": c.solves, "hints": [None]*len(hints)})
            return jsonify({"challenges": result})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"challenges": [], "error": str(e)}), 500

    @app.route("/api/v1/submit", methods=["POST"])
    @require_json
    @require_auth
    def api_submit():
        try:
            team = get_current_team()
            d = request.get_json()
            challenge_id = d.get("challenge_id","").strip()
            flag = d.get("flag","").strip()
            if not challenge_id or not flag:
                return jsonify({"error": "Missing fields"}), 400
            result = validator.validate(challenge_id, flag, team, request.remote_addr)
            return jsonify({"correct": result.correct, "points": result.points, "message": result.message, "hint": result.hint})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"correct": False, "message": f"Server error: {str(e)}"}), 500

    @app.route("/api/v1/hints/<challenge_id>")
    @require_auth
    def api_get_hints(challenge_id):
        try:
            team = get_current_team()
            rows = manager.db.fetchall("SELECT hint_index, cost FROM hint_unlocks WHERE team=? AND challenge_id=?", (team, challenge_id))
            challenge = manager.get_challenge(challenge_id)
            if not challenge: return jsonify({"unlocked": []})
            unlocked = []
            for row in rows:
                idx = row[0]
                if idx < len(challenge.hints):
                    unlocked.append({"hint_index": idx, "cost": row[1], "text": challenge.hints[idx]})
            return jsonify({"unlocked": unlocked})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"unlocked": [], "error": str(e)}), 500

    @app.route("/api/v1/hints/unlock", methods=["POST"])
    @require_json
    @require_auth
    def api_unlock_hint():
        try:
            team = get_current_team()
            d = request.get_json()
            challenge_id = d.get("challenge_id","")
            hint_index = int(d.get("hint_index", 0))
            challenge = manager.get_challenge(challenge_id)
            if not challenge: return jsonify({"success": False, "message": "Challenge not found"})
            if hint_index >= len(challenge.hints): return jsonify({"success": False, "message": "Hint not found"})
            existing = manager.db.fetchone("SELECT id FROM hint_unlocks WHERE team=? AND challenge_id=? AND hint_index=?", (team, challenge_id, hint_index))
            if existing: return jsonify({"success": True, "message": "Already unlocked"})
            cost = int(challenge.points * 0.1 * (hint_index + 1))
            team_info = auth.get_team_info(team)
            if not team_info: return jsonify({"success": False, "message": "Team not found"})
            if team_info["score"] < cost: return jsonify({"success": False, "message": f"Not enough power level! Need {cost} PL"})
            manager.db.execute("UPDATE teams SET score = score - ? WHERE name=?", (cost, team))
            manager.db.execute("INSERT INTO hint_unlocks (team, challenge_id, hint_index, cost) VALUES (?,?,?,?)", (team, challenge_id, hint_index, cost))
            return jsonify({"success": True, "message": f"Hint unlocked! -{cost} PL", "text": challenge.hints[hint_index]})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

    @app.route("/api/v1/scoreboard")
    def api_scoreboard():
        try:
            n = min(int(request.args.get("top", 50)), 100)
            return jsonify({"scores": [{"rank": e.rank, "team": e.team, "score": e.score, "solves": e.solves, "last_solve": e.last_solve} for e in scoreboard.get_top(n)]})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"scores": [], "error": str(e)}), 500

    @app.route("/api/v1/scoreboard/timeline")
    def api_timeline():
        try:
            team = request.args.get("team", "")
            return jsonify({"timeline": scoreboard.get_score_timeline(team)})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"timeline": [], "error": str(e)}), 500

    @app.route("/api/v1/feed")
    def api_feed():
        try:
            return jsonify({"events": [{"team": e.team, "challenge": e.challenge, "category": e.category, "points": e.points, "timestamp": e.timestamp, "first_blood": e.first_blood} for e in scoreboard.get_solve_feed()]})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"events": [], "error": str(e)}), 500

    @app.route("/api/v1/me")
    @require_auth
    def api_me():
        team = get_current_team()
        return jsonify({"team": auth.get_team_info(team)})

    @app.route("/api/v1/me/solves")
    def api_me_solves():
        try:
            team = get_current_team()
            if not team: return jsonify({"solves": []})
            solves = validator.get_team_solves(team)
            return jsonify({"solves": [{"challenge_id": r[0], "points": r[1], "first_blood": bool(r[2])} for r in solves]})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"solves": [], "error": str(e)}), 500

    @app.route("/api/v1/admin/teams")
    @require_admin
    def api_admin_teams():
        return jsonify({"teams": auth.get_all_teams()})

    @app.route("/api/v1/admin/teams/ban", methods=["POST"])
    @require_admin
    @require_json
    def api_ban():
        auth.ban_team(request.get_json().get("team_name",""))
        return jsonify({"success": True})

    @app.route("/api/v1/admin/teams/unban", methods=["POST"])
    @require_admin
    @require_json
    def api_unban():
        auth.unban_team(request.get_json().get("team_name",""))
        return jsonify({"success": True})

    @app.route("/api/v1/admin/teams/delete", methods=["POST"])
    @require_admin
    @require_json
    def api_delete():
        auth.delete_team(request.get_json().get("team_name",""))
        return jsonify({"success": True})

    @app.route("/api/v1/admin/teams/reset", methods=["POST"])
    @require_admin
    @require_json
    def api_reset():
        auth.reset_team_score(request.get_json().get("team_name",""))
        return jsonify({"success": True})

    @app.errorhandler(404)
    def not_found(e): return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e): return jsonify({"error": "Internal server error"}), 500

    return app


# ── Entry point ────────────────────────────────────────────────────────
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))