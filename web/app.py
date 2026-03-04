"""
Web App - CTF Platform - Dragon Ball Z Theme with Real Character Images
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

CHARACTER_JS = """
(function() {
  const CHARS = [
    {
      id: 'goku', name: 'Goku',
      img: 'https://www.pngmart.com/files/22/Goku-PNG-Isolated-File.png',
      imgSSJ: 'https://www.pngmart.com/files/22/Goku-SSJ-PNG-Isolated-Photo.png',
      width: 160, auraColor: '#ffd700', glowColor: '#ff6a00',
      quotes: ['KAMEHAMEHA!!','I need to get stronger!','KAIO-KEN x10!','Time to power up!','This is not over yet!'],
      fightQuotes: ['KAMEHAMEHA!!','KAIO-KEN!!','This ends NOW!'],
      powerUpQuotes: ["I'M GOING SUPER SAIYAN!",'AAAAHHHHH!!!','FULL POWER!!'],
      speed: 1.4, jumpHeight: 200, isSSJ: false,
      x: 80, y: 0, vx: 1.4, state: 'walk', stateTimer: 100,
      jumpVy: 0, isJumping: false, flipped: false,
    },
    {
      id: 'vegeta', name: 'Vegeta',
      img: 'https://www.pngmart.com/files/22/Vegeta-PNG-Isolated-Cutout.png',
      imgSSJ: null,
      width: 150, auraColor: '#8800ff', glowColor: '#aa00ff',
      quotes: ['I am the PRINCE of Saiyans!','My power is MAXIMUM!','OVER 9000!!','FINAL FLASH!!','You pathetic weakling!'],
      fightQuotes: ['FINAL FLASH!!','GALICK GUN!!','I will destroy you!'],
      powerUpQuotes: ['MY PRIDE...!','VEGETA DOES NOT LOSE!','FINAL BURST!!'],
      speed: 1.6, jumpHeight: 180, isSSJ: false,
      x: 500, y: 0, vx: -1.6, state: 'walk', stateTimer: 120,
      jumpVy: 0, isJumping: false, flipped: true,
    },
    {
      id: 'piccolo', name: 'Piccolo',
      img: 'https://www.pngmart.com/files/22/Piccolo-PNG-Free-Download.png',
      imgSSJ: null,
      width: 155, auraColor: '#00aa44', glowColor: '#004422',
      quotes: ['Special Beam Cannon!','I sense a great power...','Training never ends.','MAKANKOSAPPO!!','Hmph.'],
      fightQuotes: ['SPECIAL BEAM CANNON!!','HELLZONE GRENADE!!','You are no match for me!'],
      powerUpQuotes: ['My power grows...','UNLIMITED POWER!!','Feel my ki!!'],
      speed: 1.2, jumpHeight: 220, isSSJ: false,
      x: 900, y: 0, vx: 1.2, state: 'idle', stateTimer: 200,
      jumpVy: 0, isJumping: false, flipped: false,
    },
    {
      id: 'frieza', name: 'Frieza',
      img: 'https://www.pngmart.com/files/22/Frieza-PNG-File.png',
      imgSSJ: null,
      width: 145, auraColor: '#cc44ff', glowColor: '#880088',
      quotes: ["I am the greatest in the universe!",'Pathetic creatures...','DEATH BEAM!!','No one can stop me!','Kneel before me!'],
      fightQuotes: ['DEATH BALL!!','SUPERNOVA!!','You will all perish!'],
      powerUpQuotes: ['100% POWER!!','UNLIMITED POWER!!','TREMBLE BEFORE ME!!'],
      speed: 1.3, jumpHeight: 230, isSSJ: false,
      x: 1100, y: 0, vx: -1.3, state: 'float', stateTimer: 180,
      jumpVy: 0, isJumping: false, flipped: true,
    },
    {
      id: 'gohan', name: 'Gohan',
      img: 'https://www.pngmart.com/files/22/Gohan-PNG-Free-Download.png',
      imgSSJ: null,
      width: 148, auraColor: '#ffd700', glowColor: '#ff6600',
      quotes: ["It's over!","I won't let you hurt them!",'MASENKO!!','SSJ2 UNLOCKED!!','THIS POWER...!'],
      fightQuotes: ['MASENKO HA!!','FATHER-SON KAMEHAMEHA!!','THIS ENDS NOW!!'],
      powerUpQuotes: ['RAAAHHHHH!!!','SSJ2!!!','UNLIMITED POWER!!!'],
      speed: 1.5, jumpHeight: 195, isSSJ: false,
      x: 300, y: 0, vx: -1.5, state: 'walk', stateTimer: 110,
      jumpVy: 0, isJumping: false, flipped: true,
    },
  ];

  const FALLBACK_IMGS = {
    goku:    'https://static.wikia.nocookie.net/dragonball/images/5/5b/Goku_SSJ_Namek_Saga.png',
    vegeta:  'https://static.wikia.nocookie.net/dragonball/images/8/8b/VegetavsGokuEp.png',
    piccolo: 'https://static.wikia.nocookie.net/dragonball/images/3/33/PiccoloNV.png',
    frieza:  'https://static.wikia.nocookie.net/dragonball/images/6/6c/FriezaFinalForm.png',
    gohan:   'https://static.wikia.nocookie.net/dragonball/images/5/5b/GohanSSJ2Cell.png',
  };

  const GRAVITY = 0.75;
  let frameCount = 0;
  let elements = {};

  function init() {
    const layer = document.getElementById('characters-layer');
    if (!layer) return;

    CHARS.forEach(char => {
      const wrap = document.createElement('div');
      wrap.id = 'char-' + char.id;
      wrap.style.cssText = `
        position:absolute;bottom:0;left:${char.x}px;
        width:${char.width}px;pointer-events:auto;
        cursor:pointer;z-index:4;transition:filter 0.3s;
      `;

      const aura = document.createElement('div');
      aura.id = 'aura-' + char.id;
      aura.style.cssText = `
        position:absolute;bottom:-10px;left:50%;
        transform:translateX(-50%);
        width:80%;height:30px;
        background:${char.auraColor};
        border-radius:50%;
        filter:blur(14px);
        opacity:0.55;
        animation:auraPulse 1.8s ease-in-out infinite alternate;
        pointer-events:none;z-index:1;
      `;
      wrap.appendChild(aura);

      const img = document.createElement('img');
      img.src = char.img;
      img.alt = char.name;
      img.crossOrigin = 'anonymous';
      img.style.cssText = `
        width:100%;height:auto;display:block;
        position:relative;z-index:2;
        filter:drop-shadow(0 0 12px ${char.auraColor}) drop-shadow(0 4px 8px rgba(0,0,0,0.85));
      `;
      img.onerror = function() {
        if (this.src !== FALLBACK_IMGS[char.id]) {
          this.src = FALLBACK_IMGS[char.id] || '';
        }
        this.onerror = null;
      };
      wrap.appendChild(img);

      const bubble = document.createElement('div');
      bubble.id = 'bubble-' + char.id;
      bubble.style.cssText = `
        position:absolute;bottom:calc(100% + 10px);
        left:50%;transform:translateX(-50%);
        background:rgba(8,4,0,0.95);
        border:2px solid #ff6a00;border-radius:10px;
        padding:7px 14px;white-space:nowrap;
        font-family:'Bangers',cursive;font-size:1rem;
        letter-spacing:0.08em;color:#ffd700;
        opacity:0;transition:opacity 0.3s;
        pointer-events:none;z-index:10;
        box-shadow:0 0 18px rgba(255,106,0,0.5);
        text-align:center;min-width:90px;
      `;
      const tail = document.createElement('div');
      tail.style.cssText = `
        position:absolute;top:100%;left:50%;
        transform:translateX(-50%);
        border:7px solid transparent;
        border-top-color:#ff6a00;
      `;
      bubble.appendChild(tail);
      wrap.appendChild(bubble);

      const nameTag = document.createElement('div');
      nameTag.style.cssText = `
        text-align:center;
        font-family:'Bangers',cursive;
        font-size:0.85rem;letter-spacing:0.15em;
        color:${char.auraColor};
        text-shadow:0 0 8px ${char.auraColor};
        margin-top:2px;position:relative;z-index:2;
      `;
      nameTag.textContent = char.name.toUpperCase();
      wrap.appendChild(nameTag);

      layer.appendChild(wrap);
      elements[char.id] = { wrap, img, bubble, aura, nameTag };

      wrap.addEventListener('click', function(e) {
        e.stopPropagation();
        doJump(char);
        showBubble(char, char.quotes[Math.floor(Math.random() * char.quotes.length)]);
        spawnExplosion(char.x + char.width / 2, window.innerHeight - 80, char.auraColor);
      });
    });

    requestAnimationFrame(tick);
    setInterval(randomSpeech, 4000);
    setInterval(randomInteraction, 7000);
    setInterval(randomPowerUp, 13000);
  }

  function tick() {
    frameCount++;
    const W = window.innerWidth;

    CHARS.forEach(char => {
      const el = elements[char.id];
      if (!el) return;

      char.stateTimer--;
      if (char.stateTimer <= 0) changeState(char);

      if (char.isJumping) {
        char.jumpVy += GRAVITY;
        char.y -= char.jumpVy;
        if (char.y <= 0) { char.y = 0; char.isJumping = false; char.jumpVy = 0; }
      }

      if (char.state === 'walk')  char.x += char.vx;
      if (char.state === 'run')   char.x += char.vx * 2.8;
      if (char.state === 'fight') char.x += char.vx * 1.4;
      if (char.state === 'float') {
        char.x += char.vx * 0.7;
        char.y = 28 + Math.sin(frameCount * 0.018 + char.x * 0.008) * 22;
      }

      if (char.x > W - char.width - 10) {
        char.x = W - char.width - 10;
        char.vx = -Math.abs(char.vx);
        char.flipped = true;
      }
      if (char.x < 10) {
        char.x = 10;
        char.vx = Math.abs(char.vx);
        char.flipped = false;
      }

      el.wrap.style.left = char.x + 'px';
      el.wrap.style.bottom = (char.isJumping || char.state === 'float' ? Math.max(0, char.y) : 0) + 'px';
      el.wrap.style.transform = char.flipped ? 'scaleX(-1)' : 'scaleX(1)';

      if (char.state === 'powerup') {
        el.aura.style.opacity = '0.95';
        el.aura.style.width = '110%';
        el.aura.style.height = '50px';
        el.wrap.style.filter = `drop-shadow(0 0 25px ${char.auraColor}) drop-shadow(0 0 50px ${char.glowColor}) brightness(1.3)`;
      } else if (char.state === 'fight') {
        el.aura.style.opacity = '0.75';
        el.aura.style.width = '90%';
        el.aura.style.height = '35px';
        el.wrap.style.filter = `drop-shadow(0 0 18px ${char.auraColor}) drop-shadow(0 4px 8px rgba(0,0,0,0.8))`;
      } else {
        el.aura.style.opacity = '0.5';
        el.aura.style.width = '80%';
        el.aura.style.height = '28px';
        el.wrap.style.filter = `drop-shadow(0 0 12px ${char.auraColor}) drop-shadow(0 4px 8px rgba(0,0,0,0.85))`;
      }
    });

    requestAnimationFrame(tick);
  }

  function changeState(char) {
    const r = Math.random();
    if      (r < 0.30) { char.state='walk';  char.stateTimer=100+Math.random()*160; }
    else if (r < 0.44) { char.state='run';   char.stateTimer=35+Math.random()*55; char.vx=(Math.random()>.5?1:-1)*char.speed; char.flipped=char.vx<0; }
    else if (r < 0.56) { char.state='idle';  char.stateTimer=90+Math.random()*130; }
    else if (r < 0.67) { char.state='jump';  char.stateTimer=55; doJump(char); }
    else if (r < 0.78) { char.state='fight'; char.stateTimer=50+Math.random()*70; }
    else if (char.id === 'frieza') { char.state='float'; char.stateTimer=140+Math.random()*140; }
    else { char.state='walk'; char.stateTimer=120; }
  }

  function doJump(char) {
    if (!char.isJumping) {
      char.isJumping = true;
      char.jumpVy = -(char.jumpHeight * 0.20);
    }
  }

  function showBubble(char, text) {
    const el = elements[char.id];
    if (!el) return;
    const existing = el.bubble.querySelector('.bubble-text');
    if (existing) existing.remove();
    const span = document.createElement('span');
    span.className = 'bubble-text';
    span.textContent = text;
    el.bubble.insertBefore(span, el.bubble.firstChild);
    el.bubble.style.opacity = '1';
    setTimeout(() => { el.bubble.style.opacity = '0'; }, 2400);
  }

  function randomSpeech() {
    const char = CHARS[Math.floor(Math.random() * CHARS.length)];
    const pool = char.state==='fight' ? char.fightQuotes : char.state==='powerup' ? char.powerUpQuotes : char.quotes;
    showBubble(char, pool[Math.floor(Math.random() * pool.length)]);
  }

  function randomInteraction() {
    if (CHARS.length < 2) return;
    let i = Math.floor(Math.random() * CHARS.length);
    let j = Math.floor(Math.random() * CHARS.length);
    while (j === i) j = Math.floor(Math.random() * CHARS.length);
    const from = CHARS[i], to = CHARS[j];
    showBubble(from, from.fightQuotes[Math.floor(Math.random() * from.fightQuotes.length)]);
    from.state = 'fight'; from.stateTimer = 70;
    spawnKiBlast(from, to);
  }

  function spawnKiBlast(from, to) {
    const blast = document.createElement('div');
    const size = 18 + Math.random() * 14;
    const startX = from.x + from.width / 2;
    const startY = window.innerHeight - 120;
    const endX   = to.x + to.width / 2;
    const endY   = window.innerHeight - 120;
    blast.style.cssText = `
      position:fixed;
      left:${startX}px;top:${startY}px;
      width:${size}px;height:${size}px;
      border-radius:50%;
      background:radial-gradient(circle,#fff 0%,${from.auraColor} 50%,transparent 100%);
      box-shadow:0 0 20px ${from.auraColor},0 0 40px ${from.glowColor};
      pointer-events:none;z-index:6;
      transform:translate(-50%,-50%);
    `;
    document.body.appendChild(blast);
    const dx = endX - startX, dy = endY - startY;
    const dist = Math.sqrt(dx*dx + dy*dy);
    const dur = Math.max(250, dist * 0.7);
    let start = null;
    function anim(ts) {
      if (!start) start = ts;
      const p = Math.min(1, (ts - start) / dur);
      const arcY = -130 * Math.sin(Math.PI * p);
      blast.style.left  = (startX + dx * p) + 'px';
      blast.style.top   = (startY + dy * p + arcY) + 'px';
      blast.style.opacity = String(1 - p * 0.3);
      blast.style.transform = `translate(-50%,-50%) scale(${1 + p * 0.5})`;
      if (p < 1) { requestAnimationFrame(anim); }
      else {
        spawnExplosion(endX, endY, from.auraColor);
        blast.remove();
        const toChar = CHARS.find(c => c.id === to.id);
        if (toChar) showBubble(toChar, toChar.quotes[Math.floor(Math.random() * toChar.quotes.length)]);
      }
    }
    requestAnimationFrame(anim);
  }

  function spawnExplosion(x, y, color) {
    for (let i = 0; i < 7; i++) {
      const exp = document.createElement('div');
      const sz = 24 + Math.random() * 36;
      const ox = (Math.random() - 0.5) * 60;
      const oy = (Math.random() - 0.5) * 40;
      exp.style.cssText = `
        position:fixed;
        left:${x + ox - sz/2}px;top:${y + oy - sz/2}px;
        width:${sz}px;height:${sz}px;
        border-radius:50%;
        background:radial-gradient(circle,#fff 0%,${color} 40%,transparent 100%);
        box-shadow:0 0 30px ${color};
        pointer-events:none;z-index:7;
        animation:explodeAnim 0.6s ease-out forwards;
        animation-delay:${i * 0.04}s;
      `;
      document.body.appendChild(exp);
      setTimeout(() => exp.remove(), 700 + i * 45);
    }
  }

  function randomPowerUp() {
    const char = CHARS[Math.floor(Math.random() * CHARS.length)];
    const el = elements[char.id];
    if (!el) return;
    char.state = 'powerup'; char.stateTimer = 130;
    showBubble(char, char.powerUpQuotes[Math.floor(Math.random() * char.powerUpQuotes.length)]);
    spawnExplosion(char.x + char.width/2, window.innerHeight - 80, char.auraColor);
    if (char.id === 'goku' && char.imgSSJ && !char.isSSJ && Math.random() > 0.35) {
      char.isSSJ = true;
      el.img.src = char.imgSSJ;
      el.aura.style.background = '#ffd700';
      el.aura.style.height = '60px';
      el.aura.style.opacity = '0.9';
      el.wrap.style.filter = 'drop-shadow(0 0 30px #ffd700) drop-shadow(0 0 60px #ff6a00) brightness(1.4)';
      setTimeout(() => {
        char.isSSJ = false;
        el.img.src = char.img;
        el.aura.style.background = char.auraColor;
        el.aura.style.height = '28px';
        el.aura.style.opacity = '0.5';
      }, 18000);
    }
  }

  document.addEventListener('click', function(e) {
    if (e.target.closest && e.target.closest('#characters-layer')) return;
    spawnKiParticle(e.clientX, e.clientY);
  });

  function spawnKiParticle(x, y) {
    const p = document.createElement('div');
    p.className = 'ki-particle';
    const s = 10 + Math.random() * 15;
    p.style.cssText = `left:${x-s/2}px;top:${y-s/2}px;width:${s}px;height:${s}px`;
    document.body.appendChild(p);
    setTimeout(() => p.remove(), 600);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    setTimeout(init, 100);
  }

  window.dbzSpawnExplosion = spawnExplosion;
})();
"""

BASE_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');
:root {
  --orange:#ff6a00;--yellow:#ffd700;--gold:#ffb300;--red:#ff1a1a;
  --blue:#00aaff;--white:#fff;--dark:#0a0500;--card:#120800;
  --border:#ff6a0044;--glow:#ff6a00;--ki:#ffe066;--aura:#ff4400;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--dark);color:#f5e6c8;font-family:'Rajdhani',sans-serif;min-height:100vh;overflow-x:hidden;cursor:crosshair}
body::before{content:'';position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 80% 60% at 50% 0%,#ff6a0022 0%,transparent 70%),radial-gradient(ellipse 40% 40% at 80% 80%,#ffd70011 0%,transparent 60%),linear-gradient(180deg,#0a0500 0%,#0d0300 50%,#080200 100%);pointer-events:none}
body::after{content:'';position:fixed;inset:0;z-index:0;background-image:radial-gradient(circle 1px at 20% 30%,#ff6a0033 0%,transparent 1px),radial-gradient(circle 1px at 80% 70%,#ffd70022 0%,transparent 1px),radial-gradient(circle 2px at 10% 80%,#ff6a0044 0%,transparent 2px),radial-gradient(circle 1px at 90% 20%,#ffd70033 0%,transparent 1px);animation:stardrift 20s linear infinite;pointer-events:none}
@keyframes stardrift{0%{transform:translateY(0)}100%{transform:translateY(-100px)}}

/* ── CHARACTERS LAYER ── */
#characters-layer{position:fixed;inset:0;z-index:4;pointer-events:none;overflow:hidden}
#characters-layer > div{pointer-events:auto}
@keyframes auraPulse{0%{opacity:.35;transform:translateX(-50%) scale(.85)}100%{opacity:.75;transform:translateX(-50%) scale(1.15)}}
@keyframes explodeAnim{0%{transform:scale(0);opacity:1}60%{opacity:.8}100%{transform:scale(4);opacity:0}}

/* ── ENERGY LINES ── */
.energy-lines{position:fixed;inset:0;z-index:1;pointer-events:none;overflow:hidden}
.energy-lines span{position:absolute;height:1px;background:linear-gradient(90deg,transparent,#ff6a0055,transparent);animation:energyflow 3s linear infinite;opacity:0}
@keyframes energyflow{0%{opacity:0;transform:scaleX(0) translateX(-100%)}20%{opacity:1}80%{opacity:1}100%{opacity:0;transform:scaleX(1) translateX(100%)}}

/* ── HEADER ── */
.header{position:sticky;top:0;z-index:100;padding:1rem 2rem;display:flex;align-items:center;justify-content:space-between;background:linear-gradient(180deg,rgba(10,5,0,.98) 0%,rgba(10,5,0,.9) 100%);border-bottom:2px solid var(--orange);box-shadow:0 2px 30px #ff6a0044,0 0 60px #ff6a0011}
.header::after{content:'';position:absolute;bottom:-4px;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--yellow),var(--orange),var(--yellow),transparent);animation:headershine 3s linear infinite}
@keyframes headershine{0%{opacity:.3}50%{opacity:1}100%{opacity:.3}}
.logo{font-family:'Bangers',cursive;font-size:2rem;letter-spacing:.15em;text-decoration:none;background:linear-gradient(135deg,var(--yellow) 0%,var(--orange) 50%,var(--red) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 10px #ff6a0088);transition:filter .3s}
.logo:hover{filter:drop-shadow(0 0 20px #ffd700)}
.logo span{background:linear-gradient(135deg,#fff 0%,var(--yellow) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.power-level{font-family:'Bangers',cursive;font-size:.9rem;letter-spacing:.1em;color:var(--yellow);border:1px solid var(--orange);padding:4px 12px;border-radius:2px;background:rgba(255,106,0,.1);box-shadow:0 0 10px #ff6a0033;animation:powerpulse 2s ease-in-out infinite}
@keyframes powerpulse{0%,100%{box-shadow:0 0 10px #ff6a0033}50%{box-shadow:0 0 20px #ff6a0077}}
nav{display:flex;align-items:center;gap:1.5rem}
nav a{color:#c8a878;text-decoration:none;font-family:'Rajdhani',sans-serif;font-weight:700;font-size:.85rem;letter-spacing:.15em;text-transform:uppercase;transition:all .2s;position:relative}
nav a::after{content:'';position:absolute;bottom:-4px;left:0;right:0;height:2px;background:var(--orange);transform:scaleX(0);transition:transform .2s}
nav a:hover{color:var(--yellow);text-shadow:0 0 10px #ffd70088}
nav a:hover::after,nav a.active::after{transform:scaleX(1)}
nav a.active{color:var(--orange)}

/* ── BUTTONS ── */
.btn{padding:.75rem 1.75rem;font-family:'Bangers',cursive;font-size:1rem;letter-spacing:.15em;border:2px solid var(--orange);background:linear-gradient(135deg,rgba(255,106,0,.15),rgba(255,50,0,.05));color:var(--yellow);cursor:pointer;border-radius:2px;transition:all .2s;position:relative;overflow:hidden;text-transform:uppercase}
.btn::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,var(--orange),var(--red));opacity:0;transition:opacity .2s}
.btn:hover{color:#fff;box-shadow:0 0 20px #ff6a0066;transform:translateY(-2px)}
.btn:hover::before{opacity:.2}
.btn:active{transform:translateY(0) scale(.98)}
.btn:disabled{opacity:.4;cursor:not-allowed;transform:none}
.btn-full{width:100%;margin-top:.5rem}
.btn-red{border-color:var(--red)!important;color:var(--red)!important}
.btn-blue{border-color:var(--blue)!important;color:var(--blue)!important}
.btn-sm{padding:.35rem .8rem;font-size:.8rem}
.btn-ki{border-color:var(--yellow);background:linear-gradient(135deg,rgba(255,215,0,.2),rgba(255,106,0,.1))}
.btn-ki:hover{box-shadow:0 0 30px #ffd70088,0 0 60px #ff6a0044;color:#fff}

/* ── LAYOUT ── */
.container{max-width:480px;margin:4rem auto;padding:0 1rem;position:relative;z-index:10}
.wide{max-width:1100px;margin:2rem auto;padding:0 1rem;position:relative;z-index:10}
.card{background:linear-gradient(135deg,rgba(18,8,0,.97),rgba(10,5,0,.99));border:1px solid var(--orange);border-radius:4px;padding:2rem;box-shadow:0 0 40px #ff6a0022,inset 0 0 40px rgba(255,106,0,.03);position:relative;overflow:hidden}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,transparent,var(--orange),var(--yellow),var(--orange),transparent);animation:cardshine 4s linear infinite}
@keyframes cardshine{0%{opacity:.5}50%{opacity:1}100%{opacity:.5}}
.card h2{font-family:'Bangers',cursive;font-size:1.8rem;letter-spacing:.2em;color:var(--orange);margin-bottom:1.5rem;text-shadow:0 0 20px #ff6a0066}

/* ── FORMS ── */
.form-group{margin-bottom:1.2rem}
.form-group label{display:block;font-size:.75rem;color:#c8a878;letter-spacing:.15em;margin-bottom:.4rem;font-family:'Rajdhani',sans-serif;font-weight:700;text-transform:uppercase}
.form-group input{width:100%;padding:.75rem 1rem;background:rgba(255,106,0,.05);border:1px solid rgba(255,106,0,.3);color:#f5e6c8;font-family:'Share Tech Mono',monospace;font-size:.9rem;border-radius:2px;outline:none;transition:all .2s}
.form-group input:focus{border-color:var(--orange);box-shadow:0 0 15px rgba(255,106,0,.3);background:rgba(255,106,0,.08)}
.form-group input::placeholder{color:#5a3a20}
.pw-wrap{position:relative}
.pw-wrap input{padding-right:3rem}
.pw-toggle{position:absolute;right:.75rem;top:50%;transform:translateY(-50%);background:none;border:none;color:#c8a878;cursor:pointer;font-size:1rem;padding:0;line-height:1;transition:color .2s}
.pw-toggle:hover{color:var(--yellow)}

/* ── ALERTS ── */
.alert{padding:.75rem 1rem;border-radius:2px;margin-bottom:1rem;font-size:.9rem;font-weight:600}
.alert-error{background:rgba(255,26,26,.1);border:1px solid rgba(255,26,26,.4);color:#ff6666}
.alert-success{background:rgba(255,215,0,.1);border:1px solid rgba(255,215,0,.4);color:var(--yellow)}
.link{color:var(--orange);text-decoration:none;font-size:.85rem;font-weight:600}
.link:hover{color:var(--yellow);text-shadow:0 0 8px #ffd70088}
.text-center{text-align:center;margin-top:1rem}

/* ── TABLES ── */
table{width:100%;border-collapse:collapse}
th{text-align:left;padding:.75rem 1rem;font-size:.95rem;letter-spacing:.15em;color:var(--orange);border-bottom:2px solid rgba(255,106,0,.3);font-family:'Bangers',cursive}
td{padding:.75rem 1rem;border-bottom:1px solid rgba(255,106,0,.1);font-size:.9rem}
tr:hover td{background:rgba(255,106,0,.05)}
.badge{font-size:.7rem;padding:2px 8px;border-radius:2px;letter-spacing:.1em;font-weight:700}
.badge-green{background:rgba(0,255,100,.1);color:#00ff88;border:1px solid rgba(0,255,100,.3)}
.badge-red{background:rgba(255,26,26,.1);color:#ff4444;border:1px solid rgba(255,26,26,.3)}
.badge-blue{background:rgba(0,170,255,.1);color:var(--blue);border:1px solid rgba(0,170,255,.3)}
.badge-yellow{background:rgba(255,215,0,.1);color:var(--yellow);border:1px solid rgba(255,215,0,.3)}

/* ── STAT CARDS ── */
.stat-card{background:linear-gradient(135deg,rgba(18,8,0,.9),rgba(10,5,0,.95));border:1px solid rgba(255,106,0,.3);border-radius:4px;padding:1.5rem;text-align:center;position:relative;overflow:hidden;transition:all .3s;cursor:default}
.stat-card:hover{border-color:var(--orange);box-shadow:0 0 20px #ff6a0044;transform:translateY(-3px)}
.stat-value{font-family:'Bangers',cursive;font-size:2.5rem;background:linear-gradient(135deg,var(--yellow),var(--orange));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.stat-label{font-size:.75rem;color:#c8a878;letter-spacing:.15em;margin-top:.25rem;font-weight:700;text-transform:uppercase}
.section-title{font-family:'Bangers',cursive;font-size:1.5rem;color:var(--orange);letter-spacing:.2em;margin-bottom:1.5rem;padding-bottom:.5rem;border-bottom:2px solid rgba(255,106,0,.3);text-shadow:0 0 15px #ff6a0055}

/* ── TABS ── */
.tabs{display:flex;margin-bottom:2rem}
.tab{padding:.75rem 1.5rem;cursor:pointer;border:1px solid rgba(255,106,0,.3);border-right:none;font-family:'Bangers',cursive;font-size:1rem;letter-spacing:.15em;color:#c8a878;transition:all .2s;text-transform:uppercase}
.tab:last-child{border-right:1px solid rgba(255,106,0,.3)}
.tab:hover{color:var(--yellow);background:rgba(255,106,0,.1)}
.tab.active{color:var(--orange);background:rgba(255,106,0,.15);border-color:var(--orange);box-shadow:inset 0 -2px 0 var(--orange)}
.panel{display:none}.panel.active{display:block}

/* ── HERO ── */
.hero{text-align:center;padding:4rem 2rem 2rem;position:relative;z-index:10}
.dragon-radar{position:relative;width:140px;height:140px;margin:0 auto 2rem}
.radar-circle{position:absolute;inset:0;border-radius:50%;border:2px solid var(--orange);animation:radarping 2s ease-out infinite}
.radar-circle:nth-child(2){animation-delay:.5s;border-color:var(--yellow)}
.radar-circle:nth-child(3){animation-delay:1s;border-color:var(--red);opacity:.5}
@keyframes radarping{0%{transform:scale(.3);opacity:1}100%{transform:scale(1.5);opacity:0}}
.radar-dot{position:absolute;top:50%;left:50%;width:16px;height:16px;border-radius:50%;background:radial-gradient(circle,#fff,var(--yellow),var(--orange));transform:translate(-50%,-50%);box-shadow:0 0 20px var(--yellow),0 0 40px var(--orange);animation:dotpulse 1s ease-in-out infinite alternate}
@keyframes dotpulse{0%{transform:translate(-50%,-50%) scale(1)}100%{transform:translate(-50%,-50%) scale(1.3)}}
.hero-title{font-family:'Bangers',cursive;font-size:clamp(2.5rem,8vw,5.5rem);letter-spacing:.1em;line-height:1;margin-bottom:.5rem;background:linear-gradient(135deg,#fff 0%,var(--yellow) 30%,var(--orange) 60%,var(--red) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 20px #ff6a0088);animation:titlepulse 3s ease-in-out infinite}
@keyframes titlepulse{0%,100%{filter:drop-shadow(0 0 20px #ff6a0088)}50%{filter:drop-shadow(0 0 40px #ffd70088) drop-shadow(0 0 60px #ff6a0066)}}
.hero-subtitle{font-family:'Bangers',cursive;font-size:1.1rem;letter-spacing:.3em;color:var(--orange);margin-bottom:2rem;opacity:.8}
.power-display{display:inline-block;background:rgba(0,0,0,.7);border:2px solid var(--orange);padding:.75rem 2.5rem;border-radius:4px;margin-bottom:2rem;box-shadow:0 0 30px #ff6a0044;position:relative;overflow:hidden}
.power-display::before{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,215,0,.05),transparent);animation:scanline 2s linear infinite}
@keyframes scanline{0%{transform:translateX(-100%)}100%{transform:translateX(100%)}}
.power-label{font-size:.7rem;color:#c8a878;letter-spacing:.3em;margin-bottom:.25rem;font-weight:700;text-transform:uppercase}
.power-number{font-family:'Bangers',cursive;font-size:2.5rem;color:var(--yellow);letter-spacing:.1em}
.stats-bar{display:flex;justify-content:center;gap:0;max-width:700px;margin:0 auto 2rem;border:1px solid rgba(255,106,0,.3);background:rgba(0,0,0,.5);border-radius:4px;overflow:hidden}
.stat{flex:1;text-align:center;padding:1.25rem 1rem;border-right:1px solid rgba(255,106,0,.2);transition:background .3s}
.stat:last-child{border-right:none}
.stat:hover{background:rgba(255,106,0,.08)}
.stat-value2{font-family:'Bangers',cursive;font-size:2rem;color:var(--yellow)}
.stat-label2{font-size:.7rem;color:#c8a878;letter-spacing:.2em;margin-top:.2rem;font-weight:700;text-transform:uppercase}
.timer-box{display:inline-block;background:rgba(0,0,0,.8);border:2px solid var(--orange);padding:1rem 2.5rem;border-radius:4px;margin-bottom:2rem;position:relative}
.timer-box::before,.timer-box::after{content:'◆';position:absolute;top:50%;transform:translateY(-50%);color:var(--orange);font-size:.6rem}
.timer-box::before{left:.5rem}.timer-box::after{right:.5rem}
.timer-label{font-size:.65rem;color:#c8a878;letter-spacing:.3em;margin-bottom:.25rem;font-weight:700;text-transform:uppercase}
.timer{font-family:'Bangers',cursive;font-size:2.5rem;color:var(--yellow);letter-spacing:.1em}

/* ── SECTION / CHALLENGES ── */
.section{padding:2rem;max-width:1200px;margin:0 auto;position:relative;z-index:10}
.challenges-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1rem}
.challenge-card{background:linear-gradient(135deg,rgba(18,8,0,.95),rgba(10,5,0,.98));border:1px solid rgba(255,106,0,.25);border-radius:4px;padding:1.25rem;cursor:pointer;transition:all .25s;position:relative;overflow:hidden}
.challenge-card:hover{border-color:var(--orange);transform:translateY(-4px);box-shadow:0 8px 30px rgba(255,106,0,.25)}
.ch-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.75rem}
.ch-name{font-family:'Bangers',cursive;font-size:1.1rem;color:#f5e6c8;letter-spacing:.05em}
.ch-points{font-family:'Bangers',cursive;font-size:1.3rem;color:var(--yellow);text-shadow:0 0 10px #ffd70066}
.ch-meta{display:flex;gap:.5rem;margin-bottom:.5rem;flex-wrap:wrap}
.tag{font-size:.7rem;padding:2px 8px;border-radius:2px;letter-spacing:.1em;font-weight:700}
.tag-cat{background:rgba(0,170,255,.15);color:var(--blue);border:1px solid rgba(0,170,255,.3)}
.tag-easy{background:rgba(0,255,100,.1);color:#00ff88;border:1px solid rgba(0,255,100,.3)}
.tag-medium{background:rgba(255,215,0,.1);color:var(--yellow);border:1px solid rgba(255,215,0,.3)}
.tag-hard{background:rgba(255,106,0,.15);color:var(--orange);border:1px solid rgba(255,106,0,.3)}
.tag-insane{background:rgba(255,26,26,.15);color:#ff4444;border:1px solid rgba(255,26,26,.3)}
.ch-desc{font-size:.82rem;color:#a08060;margin-top:.5rem;line-height:1.6}
.ch-solves{font-size:.75rem;color:#806040;margin-top:.5rem}
.solved-badge{position:absolute;top:.75rem;right:.75rem;background:rgba(255,215,0,.15);border:1px solid rgba(255,215,0,.5);color:var(--yellow);font-size:.65rem;padding:2px 6px;border-radius:2px;font-family:'Bangers',cursive;letter-spacing:.1em}
.cat-header{grid-column:1/-1;font-family:'Bangers',cursive;font-size:1.1rem;letter-spacing:.2em;color:var(--orange);padding:.5rem 0;border-bottom:1px solid rgba(255,106,0,.3);margin-bottom:.5rem;display:flex;align-items:center;gap:.75rem}
.cat-header::before{content:'◈';color:var(--yellow)}

/* ── MODAL ── */
.modal-overlay{position:fixed;inset:0;background:rgba(5,2,0,.92);display:none;align-items:center;justify-content:center;z-index:1000;backdrop-filter:blur(4px)}
.modal-overlay.active{display:flex;animation:modalin .3s ease}
@keyframes modalin{0%{opacity:0}100%{opacity:1}}
.modal{background:linear-gradient(135deg,rgba(20,10,0,.99),rgba(10,5,0,.99));border:2px solid var(--orange);border-radius:4px;padding:2rem;max-width:560px;width:90%;max-height:90vh;overflow-y:auto;position:relative;box-shadow:0 0 60px rgba(255,106,0,.3);animation:modalslide .3s ease}
@keyframes modalslide{0%{transform:translateY(-20px) scale(.97)}100%{transform:translateY(0) scale(1)}}
.modal::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--red),var(--orange),var(--yellow),var(--orange),var(--red))}
.modal h2{font-family:'Bangers',cursive;font-size:1.8rem;letter-spacing:.1em;color:var(--orange);margin-bottom:.5rem;text-shadow:0 0 15px #ff6a0066}
.modal-desc{color:#a08060;margin-bottom:1rem;line-height:1.7;font-size:.9rem}
.flag-input{width:100%;padding:.75rem 1rem;background:rgba(255,106,0,.05);border:2px solid rgba(255,106,0,.3);color:var(--yellow);font-family:'Share Tech Mono',monospace;font-size:.95rem;border-radius:2px;outline:none;transition:all .2s}
.flag-input:focus{border-color:var(--orange);box-shadow:0 0 20px rgba(255,106,0,.3)}
.flag-input::placeholder{color:#5a3a20}
.btn-row{display:flex;gap:.75rem;margin-top:1rem;flex-wrap:wrap}
.result-msg{margin-top:1rem;padding:.75rem 1rem;border-radius:2px;font-size:.95rem;display:none;font-weight:700}
.result-msg.correct{background:rgba(255,215,0,.15);border:1px solid rgba(255,215,0,.5);color:var(--yellow);animation:correctflash .5s ease}
.result-msg.wrong{background:rgba(255,26,26,.1);border:1px solid rgba(255,26,26,.4);color:#ff6666;animation:wrongshake .4s ease}
@keyframes correctflash{0%{background:rgba(255,215,0,.4)}100%{background:rgba(255,215,0,.15)}}
@keyframes wrongshake{0%,100%{transform:translateX(0)}25%{transform:translateX(-6px)}75%{transform:translateX(6px)}}

/* ── HINTS ── */
.hints-section{margin-top:1.5rem;border-top:1px solid rgba(255,106,0,.2);padding-top:1rem}
.hints-title{font-size:.75rem;color:#c8a878;letter-spacing:.2em;margin-bottom:.75rem;font-weight:700;text-transform:uppercase}
.hint-item{background:rgba(255,106,0,.05);border:1px solid rgba(255,106,0,.2);border-radius:2px;padding:.75rem;margin-bottom:.5rem;font-size:.85rem}
.hint-locked{display:flex;justify-content:space-between;align-items:center}
.hint-cost{color:#ff6666;font-size:.75rem;font-weight:700}
.hint-text{color:#c8a878;line-height:1.6}
.hint-unlock-btn{padding:.35rem .75rem;font-family:'Bangers',cursive;font-size:.85rem;border:1px solid var(--red);background:transparent;color:var(--red);cursor:pointer;border-radius:2px;transition:all .2s;letter-spacing:.1em}
.hint-unlock-btn:hover{background:rgba(255,26,26,.1);box-shadow:0 0 10px rgba(255,26,26,.3)}

/* ── LIVE FEED ── */
.live-feed{max-height:400px;overflow-y:auto}
.feed-item{padding:.6rem 0;border-bottom:1px solid rgba(255,106,0,.1);font-size:.88rem;display:flex;gap:.75rem;align-items:center;flex-wrap:wrap;transition:background .2s}
.feed-item:hover{background:rgba(255,106,0,.05);padding-left:.5rem}
.feed-time{color:#806040;flex-shrink:0;font-family:'Share Tech Mono',monospace;font-size:.8rem}
.feed-team{color:var(--yellow);font-weight:700}
.feed-pts{color:var(--orange);margin-left:auto;font-family:'Bangers',cursive;font-size:1.1rem}

/* ── SCOREBOARD ── */
.graph-container{background:rgba(0,0,0,.5);border:1px solid rgba(255,106,0,.2);border-radius:4px;padding:1.5rem;margin-bottom:2rem}
.graph-title{font-family:'Bangers',cursive;font-size:1.1rem;color:var(--orange);letter-spacing:.2em;margin-bottom:1rem}

/* ── USER BAR ── */
.user-bar{display:flex;align-items:center;gap:.75rem}
.user-badge{font-family:'Bangers',cursive;font-size:.9rem;letter-spacing:.1em;color:var(--yellow);border:1px solid rgba(255,215,0,.4);padding:4px 12px;border-radius:2px;background:rgba(255,215,0,.1)}
.logout-btn{font-family:'Bangers',cursive;font-size:.85rem;letter-spacing:.1em;color:#c8a878;cursor:pointer;border:1px solid rgba(255,106,0,.3);padding:4px 12px;border-radius:2px;background:none;transition:all .2s}
.logout-btn:hover{color:var(--red);border-color:var(--red)}
.login-prompt{background:rgba(255,106,0,.05);border:1px solid rgba(255,106,0,.2);border-radius:4px;padding:1.5rem;text-align:center;margin-bottom:2rem}
.login-prompt p{color:#a08060;margin-bottom:1rem;font-size:.95rem}
.login-prompt a{color:var(--orange);text-decoration:none;border:1px solid var(--orange);padding:.5rem 1.5rem;border-radius:2px;margin:0 .5rem;font-family:'Bangers',cursive;font-size:.95rem;letter-spacing:.1em;transition:all .2s}
.login-prompt a:hover{background:rgba(255,106,0,.15)}
.cert-btn{background:none;border:1px solid rgba(255,215,0,.4);color:var(--yellow);padding:.4rem .8rem;font-family:'Bangers',cursive;font-size:.85rem;letter-spacing:.1em;cursor:pointer;border-radius:2px;transition:all .2s}
.cert-btn:hover{background:rgba(255,215,0,.1)}

/* ── DRAGON BALLS ── */
.dragonballs{display:flex;justify-content:center;gap:.75rem;margin:1rem auto}
.dball{width:18px;height:18px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#fff8e0,var(--yellow) 40%,var(--orange) 80%,#8b4500);box-shadow:0 0 8px rgba(255,215,0,.5);position:relative;transition:transform .2s;cursor:default}
.dball:hover{transform:scale(1.3);box-shadow:0 0 15px rgba(255,215,0,.8)}

/* ── MISC ── */
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:2rem}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:#0a0500}
::-webkit-scrollbar-thumb{background:var(--orange);border-radius:3px}
.scouter-scan{position:fixed;top:0;left:0;right:0;bottom:0;pointer-events:none;z-index:3;background:linear-gradient(0deg,transparent 48%,rgba(0,255,0,.02) 50%,transparent 52%);animation:scouterscan 5s linear infinite}
@keyframes scouterscan{0%{transform:translateY(-100%)}100%{transform:translateY(100%)}}
.ki-particle{position:fixed;pointer-events:none;z-index:9999;border-radius:50%;background:radial-gradient(circle,#fff,var(--yellow),var(--orange));animation:kiblast .6s ease-out forwards}
@keyframes kiblast{0%{transform:scale(0);opacity:1}50%{opacity:.8}100%{transform:scale(3);opacity:0}}
@keyframes kicharge{0%{box-shadow:0 0 5px var(--orange)}50%{box-shadow:0 0 30px var(--yellow),0 0 60px var(--orange)}100%{box-shadow:0 0 5px var(--orange)}}
.ki-charging{animation:kicharge 1s ease-in-out infinite}
"""

TIMER_JS = """
function updateTimer() {
  const start = new Date("{{ start_time }}").getTime();
  const end   = new Date("{{ end_time }}").getTime();
  const now   = new Date().getTime();
  const timerEl    = document.getElementById('timer');
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
<style>""" + BASE_STYLE + """
.login-wrapper{min-height:100vh;display:flex;align-items:center;justify-content:center;position:relative;z-index:10}
</style></head>
<body>
<div id="characters-layer"></div>
<div class="scouter-scan"></div>
<div class="energy-lines">
  <span style="top:20%;width:60%;left:20%;animation-delay:0s;animation-duration:4s"></span>
  <span style="top:60%;width:70%;left:10%;animation-delay:2s;animation-duration:5s"></span>
</div>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span> CTF</span></a>
  <nav><a href="/login" class="active">LOGIN</a><a href="/register">REGISTER</a></nav>
</header>
<div class="login-wrapper">
  <div class="container" style="margin:0;width:100%">
    <div style="text-align:center;margin-bottom:1.5rem">
      <div class="dragonballs">
        <div class="dball"></div><div class="dball"></div><div class="dball"></div>
        <div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div>
      </div>
    </div>
    <div class="card">
      <h2>⚡ WARRIOR LOGIN</h2>
      <div class="form-group"><label>TEAM NAME</label>
        <input type="text" id="team" placeholder="Enter your warrior name"/></div>
      <div class="form-group"><label>PASSWORD</label>
        <div class="pw-wrap">
          <input type="password" id="password" placeholder="••••••••"/>
          <button class="pw-toggle" onclick="togglePw('password','eye1')" type="button"><span id="eye1">👁</span></button>
        </div>
      </div>
      <button class="btn btn-full btn-ki" id="login-btn" onclick="login()">⚡ POWER UP & LOGIN</button>
      <div class="text-center"><a href="/register" class="link">No account? Join the battle →</a></div>
    </div>
  </div>
</div>
<script>
function togglePw(i,e){const inp=document.getElementById(i),eye=document.getElementById(e);inp.type=inp.type==='password'?'text':'password';eye.textContent=inp.type==='password'?'👁':'🙈'}
function spawnKi(x,y){const p=document.createElement('div');p.className='ki-particle';const s=10+Math.random()*15;p.style.cssText=`left:${x-s/2}px;top:${y-s/2}px;width:${s}px;height:${s}px`;document.body.appendChild(p);setTimeout(()=>p.remove(),600)}
document.addEventListener('click',e=>{if(e.target.closest&&e.target.closest('#characters-layer'))return;spawnKi(e.clientX,e.clientY);for(let i=0;i<2;i++)setTimeout(()=>spawnKi(e.clientX+(Math.random()-.5)*30,e.clientY+(Math.random()-.5)*30),i*80)});
async function login(){
  const team=document.getElementById('team').value.trim(),password=document.getElementById('password').value;
  document.querySelectorAll('.alert').forEach(m=>m.remove());
  if(!team||!password)return showAlert('⚠ Fill in all fields, warrior!','error');
  const btn=document.getElementById('login-btn');
  btn.textContent='⚡ CHARGING KI...';btn.disabled=true;btn.classList.add('ki-charging');
  try{
    const r=await fetch('/api/v1/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({team_name:team,password})});
    const data=await r.json();
    if(data.success){
      localStorage.setItem('ctf_token',data.token);localStorage.setItem('ctf_team',data.team);localStorage.setItem('ctf_is_admin',data.is_admin===true?'true':'false');
      showAlert('🐉 POWER LEVEL MAXIMUM! Entering battle...','success');
      for(let i=0;i<10;i++)setTimeout(()=>spawnKi(Math.random()*window.innerWidth,Math.random()*window.innerHeight),i*80);
      setTimeout(()=>window.location.href=data.is_admin?'/admin':'/',1000);
    }else{showAlert('💀 '+(data.message||'Login failed'),'error');btn.textContent='⚡ POWER UP & LOGIN';btn.disabled=false;btn.classList.remove('ki-charging')}
  }catch(e){showAlert('⚠ Network error','error');btn.textContent='⚡ POWER UP & LOGIN';btn.disabled=false;btn.classList.remove('ki-charging')}
}
function showAlert(msg,type){document.querySelector('.card').insertAdjacentHTML('afterbegin',`<div class="alert alert-${type}">${msg}</div>`)}
document.addEventListener('keydown',e=>{if(e.key==='Enter')login()});
</script>
<script>""" + CHARACTER_JS + """</script>
</body></html>"""

REGISTER_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Register - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + """</style></head>
<body>
<div id="characters-layer"></div>
<div class="scouter-scan"></div>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span> CTF</span></a>
  <nav><a href="/login">LOGIN</a><a href="/register" class="active">REGISTER</a></nav>
</header>
<div style="display:flex;align-items:center;justify-content:center;min-height:calc(100vh - 80px);position:relative;z-index:10">
  <div class="container" style="margin:2rem auto;width:100%">
    <div style="text-align:center;margin-bottom:1rem">
      <div class="dragonballs">
        <div class="dball"></div><div class="dball"></div><div class="dball"></div>
        <div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div>
      </div>
    </div>
    <div class="card">
      <h2>🐉 JOIN THE BATTLE</h2>
      <div class="form-group"><label>TEAM NAME</label><input type="text" id="name" placeholder="Choose your warrior name" maxlength="32"/></div>
      <div class="form-group"><label>EMAIL</label><input type="email" id="email" placeholder="warrior@earth.com"/></div>
      <div class="form-group"><label>PASSWORD</label>
        <div class="pw-wrap"><input type="password" id="password" placeholder="min 8 characters"/>
          <button class="pw-toggle" onclick="togglePw('password','eye1')" type="button"><span id="eye1">👁</span></button></div></div>
      <div class="form-group"><label>CONFIRM PASSWORD</label>
        <div class="pw-wrap"><input type="password" id="confirm" placeholder="repeat password"/>
          <button class="pw-toggle" onclick="togglePw('confirm','eye2')" type="button"><span id="eye2">👁</span></button></div></div>
      <div class="form-group"><label>COUNTRY (optional)</label><input type="text" id="country" placeholder="Planet Vegeta"/></div>
      <button class="btn btn-full btn-ki" id="reg-btn" onclick="register()">🐉 SUMMON THE DRAGON</button>
      <div class="text-center"><a href="/login" class="link">Already a warrior? Login →</a></div>
    </div>
  </div>
</div>
<script>
function togglePw(i,e){const inp=document.getElementById(i),eye=document.getElementById(e);inp.type=inp.type==='password'?'text':'password';eye.textContent=inp.type==='password'?'👁':'🙈'}
function spawnKi(x,y){const p=document.createElement('div');p.className='ki-particle';const s=10+Math.random()*15;p.style.cssText=`left:${x-s/2}px;top:${y-s/2}px;width:${s}px;height:${s}px`;document.body.appendChild(p);setTimeout(()=>p.remove(),600)}
document.addEventListener('click',e=>{if(e.target.closest&&e.target.closest('#characters-layer'))return;spawnKi(e.clientX,e.clientY)});
async function register(){
  const name=document.getElementById('name').value.trim(),email=document.getElementById('email').value.trim(),password=document.getElementById('password').value,confirm=document.getElementById('confirm').value,country=document.getElementById('country').value.trim();
  document.querySelectorAll('.alert').forEach(m=>m.remove());
  if(!name||!email||!password)return showAlert('⚠ Fill in all required fields!','error');
  if(password!==confirm)return showAlert('⚠ Passwords do not match!','error');
  if(password.length<8)return showAlert('⚠ Password must be at least 8 characters!','error');
  const btn=document.getElementById('reg-btn');btn.textContent='🐉 GATHERING DRAGON BALLS...';btn.disabled=true;btn.classList.add('ki-charging');
  try{
    const r=await fetch('/api/v1/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({team_name:name,email,password,country})});
    const data=await r.json();
    showAlert((data.success?'🐉 ':'⚠ ')+data.message,data.success?'success':'error');
    if(data.success){for(let i=0;i<12;i++)setTimeout(()=>spawnKi(Math.random()*window.innerWidth,Math.random()*window.innerHeight),i*60);setTimeout(()=>window.location.href='/login',2500)}
    else{btn.textContent='🐉 SUMMON THE DRAGON';btn.disabled=false;btn.classList.remove('ki-charging')}
  }catch(e){showAlert('⚠ Network error','error');btn.textContent='🐉 SUMMON THE DRAGON';btn.disabled=false;btn.classList.remove('ki-charging')}
}
function showAlert(msg,type){document.querySelector('.card').insertAdjacentHTML('afterbegin',`<div class="alert alert-${type}">${msg}</div>`)}
document.addEventListener('keydown',e=>{if(e.key==='Enter')register()});
</script>
<script>""" + CHARACTER_JS + """</script>
</body></html>"""

VERIFY_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Verify - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + """</style></head><body>
<div id="characters-layer"></div>
<header class="header"><a class="logo" href="/">{{ ctf_name }}<span> CTF</span></a></header>
<div style="display:flex;align-items:center;justify-content:center;min-height:calc(100vh - 80px);position:relative;z-index:10">
  <div class="container"><div class="card" style="text-align:center">
    <h2>⚡ EMAIL VERIFICATION</h2><br>
    {% if success %}<div class="alert alert-success">🐉 {{ message }}</div><br><a href="/login" class="btn btn-ki">ENTER THE BATTLE →</a>
    {% else %}<div class="alert alert-error">💀 {{ message }}</div>{% endif %}
  </div></div>
</div>
<script>""" + CHARACTER_JS + """</script>
</body></html>"""

ADMIN_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Admin - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + """</style></head><body>
<div id="characters-layer"></div>
<div class="scouter-scan"></div>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span> CTF</span></a>
  <nav>
    <a href="/">ARENA</a><a href="/admin" class="active">COMMAND</a>
    <span class="power-level">👑 {{ admin_name }}</span>
    <button onclick="logout()" class="logout-btn">RETREAT</button>
  </nav>
</header>
<div class="wide">
  <div style="text-align:center;padding:1.5rem 0 1rem">
    <div style="font-family:'Bangers',cursive;font-size:2rem;color:var(--orange);letter-spacing:.2em;text-shadow:0 0 20px #ff6a0066">⚡ COMMAND CENTER ⚡</div>
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
    <input id="search" placeholder="Search warrior..." style="padding:.5rem 1rem;background:rgba(255,106,0,.05);border:1px solid rgba(255,106,0,.3);color:#f5e6c8;font-family:'Rajdhani',sans-serif;border-radius:2px;width:300px;margin-bottom:1rem;outline:none" oninput="filterTeams()"/>
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
const token=localStorage.getItem('ctf_token'),isAdmin=localStorage.getItem('ctf_is_admin')==='true';
if(!token||!isAdmin)window.location.href='/login';
let allTeams=[];
async function api(path,opts={}){const headers={'Content-Type':'application/json','Authorization':`Bearer ${token}`};const r=await fetch('/api/v1'+path,{headers,...opts});if(r.status===401||r.status===403){window.location.href='/login';return{}}return r.json()}
async function loadStats(){
  const[teams,challenges,feed]=await Promise.all([api('/admin/teams'),api('/challenges'),api('/feed')]);
  allTeams=teams.teams||[];
  document.getElementById('stat-teams').textContent=allTeams.length;
  document.getElementById('stat-challenges').textContent=(challenges.challenges||[]).length;
  document.getElementById('stat-solves').textContent=(feed.events||[]).length;
  document.getElementById('stat-verified').textContent=allTeams.filter(t=>t.verified).length;
  renderTeams(allTeams);
  document.getElementById('challenges-body').innerHTML=(challenges.challenges||[]).map(c=>`<tr><td style="font-family:'Bangers',cursive">${c.name}</td><td><span class="badge badge-blue">${c.category}</span></td><td style="color:var(--yellow);font-family:'Bangers',cursive;font-size:1.1rem">${c.points}</td><td>${c.difficulty}</td><td>${c.solves}</td><td style="color:#c8a878">${c.hints?.length||0}</td></tr>`).join('');
  document.getElementById('solves-body').innerHTML=(feed.events||[]).map(e=>`<tr><td style="color:#806040;font-size:.8rem">${e.timestamp}</td><td style="color:var(--yellow);font-weight:700">${e.team}</td><td>${e.challenge}</td><td style="color:var(--orange);font-family:'Bangers',cursive">+${e.points}</td><td>${e.first_blood?'🩸 FIRST BLOOD':''}</td></tr>`).join('');
}
function renderTeams(teams){document.getElementById('teams-body').innerHTML=teams.map(t=>`<tr><td style="color:var(--yellow);font-family:'Bangers',cursive">${t.name}</td><td style="color:#806040;font-size:.8rem">${t.email}</td><td>${t.country||'-'}</td><td style="color:var(--orange);font-family:'Bangers',cursive;font-size:1.1rem">${t.score}</td><td>${t.solves}</td><td>${t.verified?'<span class="badge badge-green">VERIFIED</span>':'<span class="badge badge-yellow">UNVERIFIED</span>'}${t.banned?'<span class="badge badge-red" style="margin-left:4px">BANNED</span>':''}</td><td style="display:flex;gap:4px"><button class="btn btn-sm ${t.banned?'btn-blue':'btn-red'}" onclick="${t.banned?`unbanTeam('${t.name}')`:`banTeam('${t.name}')`}">${t.banned?'UNBAN':'BAN'}</button><button class="btn btn-sm" onclick="resetScore('${t.name}')">RESET</button><button class="btn btn-sm btn-red" onclick="deleteTeam('${t.name}')">DELETE</button></td></tr>`).join('')}
function filterTeams(){const q=document.getElementById('search').value.toLowerCase();renderTeams(allTeams.filter(t=>t.name.toLowerCase().includes(q)||t.email.toLowerCase().includes(q)))}
async function banTeam(name){if(!confirm(`Ban warrior "${name}"?`))return;await api('/admin/teams/ban',{method:'POST',body:JSON.stringify({team_name:name})});loadStats()}
async function unbanTeam(name){if(!confirm(`Unban warrior "${name}"?`))return;await api('/admin/teams/unban',{method:'POST',body:JSON.stringify({team_name:name})});loadStats()}
async function resetScore(name){if(!confirm(`Reset power level for "${name}"?`))return;await api('/admin/teams/reset',{method:'POST',body:JSON.stringify({team_name:name})});loadStats()}
async function deleteTeam(name){if(!confirm(`DELETE warrior "${name}"?`))return;await api('/admin/teams/delete',{method:'POST',body:JSON.stringify({team_name:name})});loadStats()}
function switchTab(name){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));document.getElementById('tab-'+name).classList.add('active');document.getElementById('panel-'+name).classList.add('active')}
function logout(){fetch('/api/v1/auth/logout',{method:'POST',headers:{'Authorization':`Bearer ${token}`}});localStorage.clear();window.location.href='/login'}
loadStats();setInterval(loadStats,30000);
</script>
<script>""" + CHARACTER_JS + """</script>
</body></html>"""

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{{ ctf_name }}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-adapter-moment/1.0.1/chartjs-adapter-moment.min.js"></script>
<style>""" + BASE_STYLE + """</style>
</head>
<body>
<div id="characters-layer"></div>
<div class="scouter-scan"></div>
<div class="energy-lines">
  <span style="top:10%;width:80%;left:10%;animation-delay:0s;animation-duration:5s"></span>
  <span style="top:40%;width:50%;left:25%;animation-delay:1.5s;animation-duration:4s"></span>
  <span style="top:70%;width:70%;left:15%;animation-delay:3s;animation-duration:6s"></span>
</div>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span> CTF</span></a>
  <nav>
    <a href="#" onclick="switchTab('challenges')">⚔ CHALLENGES</a>
    <a href="#" onclick="switchTab('scoreboard')">🏆 POWER RANKS</a>
    <a href="#" onclick="switchTab('feed')">⚡ BATTLE FEED</a>
    <div class="user-bar" id="user-bar" style="display:none">
      <span class="user-badge" id="user-name"></span>
      <a id="admin-link" href="/admin" style="display:none;color:var(--red);font-family:'Bangers',cursive;font-size:.9rem;letter-spacing:.1em;text-decoration:none;border:1px solid rgba(255,26,26,.4);padding:4px 10px;border-radius:2px">👑 COMMAND</a>
      <button class="logout-btn" onclick="logout()">RETREAT</button>
    </div>
    <div id="auth-links"><a href="/login">LOGIN</a><a href="/register">REGISTER</a></div>
  </nav>
</header>

<div class="hero">
  <div class="dragon-radar">
    <div class="radar-circle"></div><div class="radar-circle"></div><div class="radar-circle"></div>
    <div class="radar-dot"></div>
  </div>
  <div class="dragonballs">
    <div class="dball"></div><div class="dball"></div><div class="dball"></div>
    <div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div>
  </div>
  <h1 class="hero-title">{{ ctf_name }}</h1>
  <div class="hero-subtitle">{{ ctf_description }}</div>
  <div class="power-display">
    <div class="power-label">🐉 TOP WARRIOR POWER LEVEL</div>
    <div class="power-number" id="power-counter">SCOUTING...</div>
  </div>
  <div class="timer-box">
    <div class="timer-label" id="timer-label">POWER REMAINING</div>
    <div class="timer" id="timer">--:--:--</div>
  </div>
  <div class="stats-bar">
    <div class="stat"><div class="stat-value2" id="stat-challenges">-</div><div class="stat-label2">⚔ Challenges</div></div>
    <div class="stat"><div class="stat-value2" id="stat-teams">-</div><div class="stat-label2">🥊 Warriors</div></div>
    <div class="stat"><div class="stat-value2" id="stat-solves">-</div><div class="stat-label2">💥 Victories</div></div>
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
      <div style="color:#806040;padding:2rem;font-family:'Bangers',cursive;font-size:1.2rem">⚡ LOADING...</div>
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
let currentChallenge=null,scoreChart=null;
const token=localStorage.getItem('ctf_token'),team=localStorage.getItem('ctf_team'),isAdmin=localStorage.getItem('ctf_is_admin')==='true';
if(token&&team){document.getElementById('user-bar').style.display='flex';document.getElementById('user-name').textContent='⚡ '+team;document.getElementById('auth-links').style.display='none';if(isAdmin)document.getElementById('admin-link').style.display='inline-block'}

function spawnKi(x,y){const p=document.createElement('div');p.className='ki-particle';const s=10+Math.random()*15;p.style.cssText=`left:${x-s/2}px;top:${y-s/2}px;width:${s}px;height:${s}px`;document.body.appendChild(p);setTimeout(()=>p.remove(),600)}
document.addEventListener('click',e=>{if(e.target.closest&&e.target.closest('#characters-layer'))return;spawnKi(e.clientX,e.clientY);for(let i=0;i<2;i++)setTimeout(()=>spawnKi(e.clientX+(Math.random()-.5)*30,e.clientY+(Math.random()-.5)*30),i*80)});

function animatePowerCounter(target){const el=document.getElementById('power-counter');if(!target){el.textContent='SCOUTING...';return}let c=0;const step=Math.ceil(target/60);const iv=setInterval(()=>{c=Math.min(c+step,target);el.textContent=c.toLocaleString();if(c>=target)clearInterval(iv)},16)}

async function api(path,opts={}){const headers={'Content-Type':'application/json'};if(token)headers['Authorization']=`Bearer ${token}`;return(await fetch('/api/v1'+path,{headers,...opts})).json()}

async function loadChallenges(){
  const data=await api('/challenges');
  const myData=token?await api('/me/solves'):{solves:[]};
  const mySolves=new Set((myData.solves||[]).map(s=>s.challenge_id));
  const grid=document.getElementById('challenges-grid');
  const prompt=document.getElementById('login-prompt-box');
  if(!token){prompt.innerHTML=`<div class="login-prompt"><p>⚡ Login to submit flags and compete for the Dragon Balls!</p><a href="/login">⚡ LOGIN</a><a href="/register">🐉 REGISTER</a></div>`}
  if(!data.challenges?.length){grid.innerHTML='<div style="color:#806040;padding:2rem;font-family:Bangers,cursive">No challenges yet...</div>';return}
  document.getElementById('stat-challenges').textContent=data.challenges.length;
  const grouped={};
  data.challenges.forEach(ch=>{if(!grouped[ch.category])grouped[ch.category]=[];grouped[ch.category].push(ch)});
  grid.innerHTML='';
  Object.entries(grouped).sort().forEach(([cat,chs])=>{
    const hdr=document.createElement('div');hdr.className='cat-header';hdr.textContent=cat.toUpperCase();grid.appendChild(hdr);
    chs.sort((a,b)=>a.points-b.points).forEach(ch=>{
      const solved=mySolves.has(ch.id);
      const card=document.createElement('div');card.className='challenge-card';
      if(solved)card.style.borderColor='rgba(255,215,0,.5)';
      card.innerHTML=`${solved?'<div class="solved-badge">✓ CONQUERED</div>':''}<div class="ch-header"><div class="ch-name">${ch.name}</div><div class="ch-points">${ch.points} PL</div></div><div class="ch-meta"><span class="tag tag-cat">${ch.category}</span><span class="tag tag-${ch.difficulty}">${ch.difficulty.toUpperCase()}</span></div><div class="ch-desc">${ch.description||''}</div><div class="ch-solves">⚔ ${ch.solves} warrior${ch.solves!==1?'s':''} conquered</div>${ch.hints?.length?`<div style="font-size:.7rem;color:#c8a878;margin-top:.25rem">💡 ${ch.hints.length} hints</div>`:''}`;
      card.onclick=()=>token?openModal(ch):window.location.href='/login';
      grid.appendChild(card);
    });
  });
}

async function loadScoreboard(){
  const data=await api('/scoreboard');
  document.getElementById('stat-teams').textContent=data.scores?.length||0;
  const tbody=document.getElementById('scoreboard-body');
  if(!data.scores?.length){tbody.innerHTML='<tr><td colspan="6" style="color:#806040;padding:1rem;font-family:Bangers,cursive">No warriors yet!</td></tr>';return}
  const ranks=['🥇','🥈','🥉'];
  tbody.innerHTML=data.scores.map((e,i)=>`<tr><td style="font-family:'Bangers',cursive;font-size:1.3rem;color:${i===0?'#ffd700':i===1?'#c0c0c0':i===2?'#cd7f32':'#f5e6c8'}">${ranks[i]||(i+1)}</td><td style="font-family:'Bangers',cursive;color:var(--yellow)">${e.team}</td><td style="font-family:'Bangers',cursive;font-size:1.2rem;color:var(--orange)">${e.score.toLocaleString()}</td><td>${e.solves}</td><td style="color:#806040;font-size:.8rem">${e.last_solve}</td><td><button class="cert-btn" onclick="getCertificate('${e.team}','${i+1}')">🏆 CERT</button></td></tr>`).join('');
  await drawScoreGraph(data.scores.slice(0,5));
  if(data.scores.length)animatePowerCounter(data.scores[0].score);
}

async function drawScoreGraph(topTeams){
  const timelines=await Promise.all(topTeams.map(t=>api(`/scoreboard/timeline?team=${encodeURIComponent(t.team)}`)));
  const colors=['#ffd700','#ff6a00','#ff1a1a','#00aaff','#aa00ff'];
  const datasets=topTeams.map((t,i)=>({label:t.team,data:(timelines[i].timeline||[]).map(p=>({x:p.time*1000,y:p.total})),borderColor:colors[i],backgroundColor:colors[i]+'22',borderWidth:2,pointRadius:3,tension:.3,fill:false}));
  const ctx=document.getElementById('scoreGraph').getContext('2d');
  if(scoreChart)scoreChart.destroy();
  scoreChart=new Chart(ctx,{type:'line',data:{datasets},options:{responsive:true,interaction:{mode:'index',intersect:false},plugins:{legend:{labels:{color:'#c8a878',font:{family:'Rajdhani',weight:'700'},boxWidth:12}},tooltip:{backgroundColor:'#120800',borderColor:'#ff6a0066',borderWidth:1,titleColor:'#ffd700',bodyColor:'#f5e6c8'}},scales:{x:{type:'time',time:{unit:'hour'},ticks:{color:'#806040',font:{family:'Share Tech Mono',size:10}},grid:{color:'rgba(255,106,0,.1)'}},y:{ticks:{color:'#806040',font:{family:'Share Tech Mono',size:10}},grid:{color:'rgba(255,106,0,.1)'}}}}});
}

async function loadFeed(){
  const data=await api('/feed');
  const feed=document.getElementById('live-feed');
  if(!data.events?.length){feed.innerHTML='<div style="color:#806040;padding:1rem;font-family:Bangers,cursive">No battles yet!</div>';return}
  document.getElementById('stat-solves').textContent=data.events.length;
  feed.innerHTML=data.events.map(e=>`<div class="feed-item"><span class="feed-time">[${e.timestamp}]</span><span class="feed-team">⚡ ${e.team}</span><span style="color:#806040">conquered</span><span style="color:#f5e6c8">${e.challenge}</span>${e.first_blood?'<span style="color:var(--red)">🩸 FIRST BLOOD</span>':''}<span class="feed-pts">+${e.points} PL</span></div>`).join('');
}

async function openModal(ch){
  currentChallenge=ch;
  document.getElementById('modal-title').textContent='⚡ '+ch.name;
  document.getElementById('modal-desc').textContent=ch.description||'Defeat this challenge!';
  document.getElementById('flag-input').value='';
  document.getElementById('result-msg').style.display='none';
  await loadHints(ch);
  document.getElementById('modal').classList.add('active');
  setTimeout(()=>document.getElementById('flag-input').focus(),100);
}

async function loadHints(ch){
  const section=document.getElementById('hints-section');
  if(!ch.hints?.length){section.innerHTML='';return}
  const unlocked=token?await api(`/hints/${ch.id}`):{unlocked:[]};
  const unlockedSet=new Set((unlocked.unlocked||[]).map(h=>h.hint_index));
  section.innerHTML=`<div class="hints-title">💡 SENSEI HINTS (${ch.hints.length})</div>`+ch.hints.map((hint,i)=>{
    const cost=Math.floor(ch.points*.1*(i+1));
    if(unlockedSet.has(i))return`<div class="hint-item"><div style="font-size:.7rem;color:#c8a878;margin-bottom:.35rem">HINT ${i+1} 💡</div><div class="hint-text">${unlocked.unlocked.find(h=>h.hint_index===i)?.text||''}</div></div>`;
    return`<div class="hint-item"><div class="hint-locked"><span style="color:#c8a878">Hint ${i+1}</span><div style="display:flex;align-items:center;gap:.75rem"><span class="hint-cost">-${cost} PL</span><button class="hint-unlock-btn" onclick="unlockHint('${ch.id}',${i},${cost})">UNLOCK</button></div></div></div>`;
  }).join('');
}

async function unlockHint(cid,hi,cost){
  if(!token)return window.location.href='/login';
  if(!confirm(`Sacrifice ${cost} power level for this hint?`))return;
  const r=await api('/hints/unlock',{method:'POST',body:JSON.stringify({challenge_id:cid,hint_index:hi})});
  if(r.success)await loadHints(currentChallenge);
  else alert(r.message||'Failed');
}

function closeModal(){document.getElementById('modal').classList.remove('active');currentChallenge=null}

async function submitFlag(){
  if(!currentChallenge)return;
  const flag=document.getElementById('flag-input').value.trim();
  if(!flag)return;
  const btn=document.querySelector('#modal .btn-ki');
  btn.textContent='⚡ CHARGING...';btn.disabled=true;
  const r=await fetch('/api/v1/submit',{method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`},body:JSON.stringify({challenge_id:currentChallenge.id,flag,team})});
  const data=await r.json();
  btn.textContent='⚡ RELEASE KI BLAST';btn.disabled=false;
  const msg=document.getElementById('result-msg');
  msg.style.display='block';
  msg.className='result-msg '+(data.correct?'correct':'wrong');
  msg.textContent=data.correct?'🐉 CHALLENGE CONQUERED! POWER LEVEL RISING!':'💀 '+data.message;
  if(data.correct){
    for(let i=0;i<20;i++)setTimeout(()=>spawnKi(Math.random()*window.innerWidth,Math.random()*window.innerHeight),i*60);
    setTimeout(()=>{closeModal();loadChallenges();loadScoreboard();loadFeed()},2000);
  }
}

function getCertificate(teamName,rank){window.open(`/certificate/${teamName}?rank=${rank}`,'_blank')}
function switchTab(name){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));document.getElementById('tab-'+name).classList.add('active');document.getElementById('panel-'+name).classList.add('active');if(name==='scoreboard')loadScoreboard();if(name==='feed')loadFeed()}
function logout(){fetch('/api/v1/auth/logout',{method:'POST',headers:{'Authorization':`Bearer ${token}`}});localStorage.clear();window.location.href='/login'}
document.getElementById('flag-input')?.addEventListener('keydown',e=>{if(e.key==='Enter')submitFlag()});
document.getElementById('modal')?.addEventListener('click',e=>{if(e.target===document.getElementById('modal'))closeModal()});
loadChallenges();loadFeed();
setInterval(()=>{loadScoreboard();loadFeed()},30000);
</script>
<script>""" + TIMER_JS + """</script>
<script>""" + CHARACTER_JS + """</script>
</body></html>"""

CERT_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Certificate - {{ team }}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Rajdhani:wght@400;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{background:radial-gradient(ellipse at center,#1a0800 0%,#0a0300 60%,#050100 100%);display:flex;align-items:center;justify-content:center;min-height:100vh;padding:2rem;font-family:'Rajdhani',sans-serif}
.cert{background:linear-gradient(135deg,rgba(25,12,0,.98),rgba(10,5,0,.99));border:3px solid #ff6a00;border-radius:8px;padding:4rem;max-width:800px;width:100%;text-align:center;position:relative;box-shadow:0 0 80px rgba(255,106,0,.3),0 0 160px rgba(255,106,0,.1)}
.cert::before{content:'';position:absolute;inset:10px;border:1px solid rgba(255,215,0,.2);border-radius:4px;pointer-events:none}
.corner{position:absolute;width:24px;height:24px;border-color:#ffd700;border-style:solid}
.corner-tl{top:18px;left:18px;border-width:3px 0 0 3px}
.corner-tr{top:18px;right:18px;border-width:3px 3px 0 0}
.corner-bl{bottom:18px;left:18px;border-width:0 0 3px 3px}
.corner-br{bottom:18px;right:18px;border-width:0 3px 3px 0}
.cert-logo{font-family:'Bangers',cursive;font-size:1rem;color:rgba(255,106,0,.6);letter-spacing:.3em;margin-bottom:2rem}
.cert-title{font-family:'Bangers',cursive;font-size:3rem;background:linear-gradient(135deg,#fff,#ffd700,#ff6a00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.5rem;letter-spacing:.1em}
.cert-subtitle{color:rgba(255,215,0,.7);font-size:.9rem;letter-spacing:.3em;margin-bottom:3rem;font-weight:700;text-transform:uppercase}
.cert-text{color:#a08060;font-size:.95rem;margin-bottom:.75rem;letter-spacing:.05em}
.cert-name{font-family:'Bangers',cursive;font-size:2.5rem;color:#fff;margin:1rem 0;padding:.75rem 2rem;border:2px solid rgba(255,215,0,.5);display:inline-block;background:rgba(255,215,0,.05);border-radius:4px;letter-spacing:.1em;text-shadow:0 0 20px rgba(255,215,0,.5)}
.cert-rank{font-family:'Bangers',cursive;font-size:3.5rem;color:#ffd700;margin:1rem 0;text-shadow:0 0 30px rgba(255,215,0,.6)}
.cert-details{display:flex;justify-content:center;gap:3rem;margin:2rem 0;padding:1.5rem;border-top:1px solid rgba(255,106,0,.3);border-bottom:1px solid rgba(255,106,0,.3)}
.cert-detail-value{font-family:'Bangers',cursive;font-size:1.8rem;color:#ffd700}
.cert-detail-label{font-size:.7rem;color:#806040;letter-spacing:.15em;margin-top:.25rem;font-weight:700;text-transform:uppercase}
.cert-footer{margin-top:2rem;color:#5a3a20;font-size:.75rem;letter-spacing:.1em}
.cert-id{color:#3a2010;font-size:.65rem;margin-top:.5rem}
.print-btn{margin-top:2rem;padding:.75rem 2rem;background:transparent;border:2px solid #ff6a00;color:#ffd700;font-family:'Bangers',cursive;font-size:1rem;cursor:pointer;border-radius:2px;letter-spacing:.15em;transition:all .2s}
.print-btn:hover{background:rgba(255,106,0,.15);box-shadow:0 0 20px rgba(255,106,0,.4)}
.dragonballs{display:flex;justify-content:center;gap:.75rem;margin:1rem 0}
.dball{width:20px;height:20px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#fff8e0,#ffd700 40%,#ff6a00 80%,#8b4500);box-shadow:0 0 10px rgba(255,215,0,.5)}
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
        rank_emojis = {1: "🥇", 2: "🥈", 3: "🥉"}
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


# ── Entry point ──────────────────────────────────────────────────────
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))