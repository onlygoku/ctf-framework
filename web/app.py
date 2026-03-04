"""
Web App - CTF Platform - Dragon Ball Z Theme with Pixel Art Characters
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

# ─────────────────────────────────────────────────────────────────────
# PIXEL ART CHARACTER SYSTEM
# Each character is drawn with CSS box-shadow pixel art technique
# ─────────────────────────────────────────────────────────────────────

PIXEL_ART_CSS = """
/* ── PIXEL ART BASE ── */
.px { display:inline-block; width:4px; height:4px; position:relative; }
.char-wrap {
  position:absolute; bottom:0; cursor:pointer; pointer-events:auto;
  image-rendering:pixelated; transform-origin:bottom center;
}
.char-canvas {
  position:relative; width:48px; height:80px;
  image-rendering:pixelated;
}

/* ── WALK ANIMATION ── */
@keyframes walkBob  { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-3px)} }
@keyframes runBob   { 0%,100%{transform:translateY(0)} 25%{transform:translateY(-5px)} 75%{transform:translateY(-2px)} }
@keyframes idleBreath{ 0%,100%{transform:scaleY(1)} 50%{transform:scaleY(0.97)} }
@keyframes jumpArc  { 0%{transform:translateY(0) rotate(0deg)} 40%{transform:translateY(-90px) rotate(-10deg)} 60%{transform:translateY(-90px) rotate(10deg)} 100%{transform:translateY(0) rotate(0deg)} }
@keyframes powerUp  { 0%{filter:brightness(1)} 30%{filter:brightness(2) saturate(2)} 60%{filter:brightness(3) saturate(3)} 100%{filter:brightness(1)} }
@keyframes ssjFlare { 0%,100%{box-shadow:0 0 20px #ffd700, 0 0 40px #ff6a00} 50%{box-shadow:0 0 40px #fff, 0 0 80px #ffd700, 0 0 120px #ff6a00} }
@keyframes fightKick{ 0%{transform:rotate(0deg)} 30%{transform:rotate(-15deg) translateX(8px)} 70%{transform:rotate(15deg) translateX(-8px)} 100%{transform:rotate(0deg)} }
@keyframes chargeKi { 0%{opacity:0.4;transform:scale(0.8)} 50%{opacity:1;transform:scale(1.1)} 100%{opacity:0.4;transform:scale(0.8)} }
@keyframes floatUp  { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-12px)} }
@keyframes legLeft  { 0%,100%{transform:rotate(20deg)} 50%{transform:rotate(-20deg)} }
@keyframes legRight { 0%,100%{transform:rotate(-20deg)} 50%{transform:rotate(20deg)} }
@keyframes armSwing { 0%,100%{transform:rotate(-25deg)} 50%{transform:rotate(25deg)} }
@keyframes hairFlap { 0%,100%{transform:skewX(0deg)} 50%{transform:skewX(5deg)} }
@keyframes auraRing { 0%{transform:translateX(-50%) scaleX(0.7);opacity:0.3} 100%{transform:translateX(-50%) scaleX(1.1);opacity:0.8} }
@keyframes kiOrb    { 0%,100%{transform:scale(1) rotate(0deg);opacity:0.8} 50%{transform:scale(1.3) rotate(180deg);opacity:1} }
@keyframes explosion{ 0%{transform:scale(0);opacity:1} 100%{transform:scale(4);opacity:0} }
@keyframes kiBlast  { 0%{transform:scale(0);opacity:1} 100%{transform:scale(2.5);opacity:0} }
@keyframes screenShake{ 0%,100%{transform:translate(0,0)} 20%{transform:translate(-4px,2px)} 40%{transform:translate(4px,-2px)} 60%{transform:translate(-3px,3px)} 80%{transform:translate(3px,-1px)} }

/* ── AURA ── */
.char-aura {
  position:absolute; bottom:-6px; left:50%;
  border-radius:50%; filter:blur(10px);
  animation:auraRing 1.2s ease-in-out infinite alternate;
  pointer-events:none; z-index:0;
}
/* ── KI ORB ── */
.ki-orb {
  position:absolute; border-radius:50%;
  background:radial-gradient(circle at 35% 35%,#fff,currentColor);
  animation:kiOrb 1.8s ease-in-out infinite;
  pointer-events:none;
}
/* ── SPEECH BUBBLE ── */
.speech-bubble {
  position:absolute; bottom:calc(100% + 8px); left:50%;
  transform:translateX(-50%);
  background:rgba(5,2,0,.96); border:2px solid #ff6a00;
  border-radius:8px; padding:5px 10px;
  font-family:'Bangers',cursive; font-size:.85rem;
  letter-spacing:.06em; color:#ffd700;
  white-space:nowrap; opacity:0; transition:opacity .25s;
  pointer-events:none; z-index:20;
  box-shadow:0 0 14px rgba(255,106,0,.4);
}
.speech-bubble::after {
  content:''; position:absolute; top:100%; left:50%;
  transform:translateX(-50%);
  border:6px solid transparent; border-top-color:#ff6a00;
}
.char-name {
  text-align:center; font-family:'Bangers',cursive;
  font-size:.75rem; letter-spacing:.12em;
  margin-top:2px; position:relative; z-index:2;
}
"""

PIXEL_CHARS_JS = r"""
(function(){
'use strict';

// ── PIXEL ART RENDERER ──────────────────────────────────────────────
// Each character defined as a 12x20 grid of colored pixels
// Colors: 0=transparent, other=hex string key in palette

const PAL = {
  // Shared
  W:'#fff', SK:'#f5c97a', SK2:'#e8a85a', DK:'#1a0800',
  BK:'#111', OR:'#ff6a00', YL:'#ffd700', RD:'#ff2200',
  BL:'#1a44cc', PU:'#7700cc', GR:'#116611', GY:'#888',
  LG:'#22aa33', PK:'#ff44cc', WH:'#eeeeff', NV:'#001166',
  OG:'#ff8800', TL:'#00bbaa', SL:'#ccccdd', CY:'#00ddff',
};

// 12-wide x 20-tall pixel maps  (row by row, top to bottom)
// Values are palette keys or 0 (transparent)
const SPRITES = {

goku:[
  // Hair (spiky, black)
  [0,0,'BK','BK','BK','BK','BK','BK','BK',0,0,0],
  [0,'BK','BK','BK','BK','BK','BK','BK','BK','BK',0,0],
  ['BK','BK','BK','SK','SK','SK','SK','SK','BK','BK','BK',0],
  // Face
  [0,'BK','SK','SK','SK','SK','SK','SK','SK','BK',0,0],
  [0,'SK','SK','W','BK','SK','W','BK','SK','SK',0,0], // eyes
  [0,'SK','SK','SK','SK','SK','SK','SK','SK','SK',0,0],
  [0,'SK','SK','SK','OR','SK','SK','OR','SK','SK',0,0], // cheeks/nose
  [0,0,'SK','SK','SK','SK','SK','SK','SK',0,0,0],
  // Neck + shoulders
  [0,0,0,'SK','SK','SK','SK','SK',0,0,0,0],
  // Gi top (orange)
  [0,'OR','OR','OR','OR','OR','OR','OR','OR','OR',0,0],
  [0,'OR','BL','OR','OR','OR','OR','OR','BL','OR',0,0], // belt detail
  ['OR','OR','OR','OR','OR','OR','OR','OR','OR','OR','OR',0],
  // Belt (blue)
  [0,'BL','BL','BL','BL','BL','BL','BL','BL','BL',0,0],
  // Gi pants (blue)
  [0,'BL','BL','OR','BL','BL','BL','OR','BL','BL',0,0],
  [0,'BL','BL','OR','BL','BL','BL','OR','BL','BL',0,0],
  [0,'BL','BL','OR','BL','BL','BL','OR','BL','BL',0,0],
  // Legs
  [0,0,'OR','OR','BL',0,0,'BL','OR','OR',0,0],
  [0,0,'OR','OR','BL',0,0,'BL','OR','OR',0,0],
  // Boots (red)
  [0,0,'RD','RD','RD',0,0,'RD','RD','RD',0,0],
  [0,0,'RD','RD','RD',0,0,'RD','RD','RD',0,0],
],

goku_ssj:[
  // Hair (golden/yellow)
  [0,0,'YL','YL','YL','YL','YL','YL','YL',0,0,0],
  [0,'YL','YL','YL','YL','YL','YL','YL','YL','YL',0,0],
  ['YL','YL','YL','SK','SK','SK','SK','SK','YL','YL','YL',0],
  [0,'YL','SK','SK','SK','SK','SK','SK','SK','YL',0,0],
  [0,'SK','SK','W','BK','SK','W','BK','SK','SK',0,0],
  [0,'SK','SK','SK','SK','SK','SK','SK','SK','SK',0,0],
  [0,'SK','SK','SK','OR','SK','SK','OR','SK','SK',0,0],
  [0,0,'SK','SK','SK','SK','SK','SK','SK',0,0,0],
  [0,0,0,'SK','SK','SK','SK','SK',0,0,0,0],
  [0,'OR','OR','OR','OR','OR','OR','OR','OR','OR',0,0],
  [0,'OR','BL','OR','OR','OR','OR','OR','BL','OR',0,0],
  ['OR','OR','OR','OR','OR','OR','OR','OR','OR','OR','OR',0],
  [0,'BL','BL','BL','BL','BL','BL','BL','BL','BL',0,0],
  [0,'BL','BL','OR','BL','BL','BL','OR','BL','BL',0,0],
  [0,'BL','BL','OR','BL','BL','BL','OR','BL','BL',0,0],
  [0,'BL','BL','OR','BL','BL','BL','OR','BL','BL',0,0],
  [0,0,'OR','OR','BL',0,0,'BL','OR','OR',0,0],
  [0,0,'OR','OR','BL',0,0,'BL','OR','OR',0,0],
  [0,0,'RD','RD','RD',0,0,'RD','RD','RD',0,0],
  [0,0,'RD','RD','RD',0,0,'RD','RD','RD',0,0],
],

vegeta:[
  // Widow peak hair
  [0,'BK','BK','BK','BK','BK','BK','BK','BK','BK',0,0],
  ['BK','BK','BK','BK','BK','BK','BK','BK','BK','BK','BK',0],
  ['BK','BK','BK','SK','SK','SK','SK','SK','BK','BK','BK',0],
  [0,'BK','SK','SK','SK','SK','SK','SK','SK','BK',0,0],
  [0,'SK','SK','W','BK','SK','W','BK','SK','SK',0,0],
  [0,'SK','SK','SK','SK','SK','SK','SK','SK','SK',0,0],
  [0,'SK','SK','SK',0,'SK','SK',0,'SK','SK',0,0], // stern face
  [0,0,'SK','SK','SK','SK','SK','SK','SK',0,0,0],
  [0,0,0,'SK','SK','SK','SK','SK',0,0,0,0],
  // Saiyan armor (white/gold)
  [0,'WH','WH','WH','WH','WH','WH','WH','WH','WH',0,0],
  [0,'WH','YL','WH','WH','WH','WH','WH','YL','WH',0,0],
  ['WH','WH','WH','WH','WH','WH','WH','WH','WH','WH','WH',0],
  // Belt
  [0,'BK','BK','BK','BK','BK','BK','BK','BK','BK',0,0],
  // Pants (blue/navy)
  [0,'NV','NV','WH','NV','NV','NV','WH','NV','NV',0,0],
  [0,'NV','NV','WH','NV','NV','NV','WH','NV','NV',0,0],
  [0,'NV','NV','WH','NV','NV','NV','WH','NV','NV',0,0],
  [0,0,'NV','NV','NV',0,0,'NV','NV','NV',0,0],
  [0,0,'NV','NV','NV',0,0,'NV','NV','NV',0,0],
  [0,0,'WH','WH','WH',0,0,'WH','WH','WH',0,0],
  [0,0,'WH','WH','WH',0,0,'WH','WH','WH',0,0],
],

piccolo:[
  // Antennae + head
  [0,0,0,'LG','LG',0,0,'LG','LG',0,0,0],
  [0,0,0,'LG','LG',0,0,'LG','LG',0,0,0],
  [0,0,'LG','LG','LG','LG','LG','LG','LG','LG',0,0],
  [0,'LG','LG','LG','LG','LG','LG','LG','LG','LG','LG',0],
  [0,'LG','LG','W','BK','LG','W','BK','LG','LG',0,0],// eyes (white pupils)
  [0,'LG','LG','LG','LG','LG','LG','LG','LG','LG',0,0],
  [0,'LG','LG','LG','LG','LG','LG','LG','LG','LG',0,0],
  [0,0,'LG','LG','LG','LG','LG','LG','LG',0,0,0],
  [0,0,0,'LG','LG','LG','LG','LG',0,0,0,0],
  // Purple gi / cape
  [0,'PU','PU','PU','PU','PU','PU','PU','PU','PU',0,0],
  [0,'PU','WH','PU','PU','PU','PU','PU','WH','PU',0,0],
  ['PU','PU','PU','PU','PU','PU','PU','PU','PU','PU','PU',0],
  [0,'WH','WH','WH','WH','WH','WH','WH','WH','WH',0,0],
  // Pants (purple)
  [0,'PU','PU','WH','PU','PU','PU','WH','PU','PU',0,0],
  [0,'PU','PU','WH','PU','PU','PU','WH','PU','PU',0,0],
  [0,'PU','PU','WH','PU','PU','PU','WH','PU','PU',0,0],
  [0,0,'PU','PU','PU',0,0,'PU','PU','PU',0,0],
  [0,0,'PU','PU','PU',0,0,'PU','PU','PU',0,0],
  [0,0,'WH','WH','WH',0,0,'WH','WH','WH',0,0],
  [0,0,'WH','WH','WH',0,0,'WH','WH','WH',0,0],
],

frieza:[
  // Head (white/purple markings)
  [0,0,'WH','WH','WH','WH','WH','WH','WH',0,0,0],
  [0,'WH','WH','WH','WH','WH','WH','WH','WH','WH',0,0],
  [0,'WH','PU','WH','WH','WH','WH','WH','PU','WH',0,0], // head markings
  [0,'WH','WH','WH','WH','WH','WH','WH','WH','WH',0,0],
  [0,'WH','WH','RD','BK','WH','RD','BK','WH','WH',0,0], // creepy eyes
  [0,'WH','WH','WH','WH','WH','WH','WH','WH','WH',0,0],
  [0,'WH','PU','WH','WH','WH','WH','WH','PU','WH',0,0],
  [0,0,'WH','WH','WH','WH','WH','WH','WH',0,0,0],
  [0,0,0,'WH','WH','WH','WH','WH',0,0,0,0],
  // Armor (white/purple)
  [0,'WH','WH','WH','WH','WH','WH','WH','WH','WH',0,0],
  [0,'WH','PU','WH','WH','WH','WH','WH','PU','WH',0,0],
  ['WH','WH','WH','WH','WH','WH','WH','WH','WH','WH','WH',0],
  [0,'PU','PU','PU','PU','PU','PU','PU','PU','PU',0,0],
  // Tail + legs (long)
  [0,'WH','WH','PU','WH','WH','WH','PU','WH','WH',0,0],
  [0,'WH','WH','PU','WH','WH','WH','PU','WH','WH',0,0],
  [0,'WH','WH','PU','WH','WH','WH','PU','WH','WH',0,0],
  [0,0,'WH','WH','WH',0,0,'WH','WH','WH',0,0],
  [0,0,'WH','WH','WH',0,0,'WH','WH','WH',0,0],
  [0,0,'PU','PU','PU',0,0,'PU','PU','PU',0,0],
  [0,0,'PU','PU','PU',0,0,'PU','PU','PU',0,0],
],

gohan:[
  // Hair (black, similar to goku but shorter)
  [0,0,'BK','BK','BK','BK','BK','BK',0,0,0,0],
  [0,'BK','BK','BK','BK','BK','BK','BK','BK','BK',0,0],
  ['BK','BK','BK','SK','SK','SK','SK','SK','BK','BK',0,0],
  [0,'BK','SK','SK','SK','SK','SK','SK','SK','BK',0,0],
  [0,'SK','SK','W','BK','SK','W','BK','SK','SK',0,0],
  [0,'SK','SK','SK','SK','SK','SK','SK','SK','SK',0,0],
  [0,'SK','SK','SK',0,'SK','SK',0,'SK','SK',0,0],
  [0,0,'SK','SK','SK','SK','SK','SK','SK',0,0,0],
  [0,0,0,'SK','SK','SK','SK','SK',0,0,0,0],
  // Purple gi
  [0,'PU','PU','PU','PU','PU','PU','PU','PU','PU',0,0],
  [0,'PU','YL','PU','PU','PU','PU','PU','YL','PU',0,0],
  ['PU','PU','PU','PU','PU','PU','PU','PU','PU','PU','PU',0],
  [0,'YL','YL','YL','YL','YL','YL','YL','YL','YL',0,0],
  [0,'BL','BL','YL','BL','BL','BL','YL','BL','BL',0,0],
  [0,'BL','BL','YL','BL','BL','BL','YL','BL','BL',0,0],
  [0,'BL','BL','YL','BL','BL','BL','YL','BL','BL',0,0],
  [0,0,'BL','BL','BL',0,0,'BL','BL','BL',0,0],
  [0,0,'BL','BL','BL',0,0,'BL','BL','BL',0,0],
  [0,0,'BK','BK','BK',0,0,'BK','BK','BK',0,0],
  [0,0,'BK','BK','BK',0,0,'BK','BK','BK',0,0],
],
};

// ── BUILD CHARACTER SVG ────────────────────────────────────────────
function buildPixelChar(spriteKey, scale=4) {
  const grid = SPRITES[spriteKey];
  const cols = 12, rows = 20;
  const W = cols * scale, H = rows * scale;
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" shape-rendering="crispEdges">`;
  for (let r=0; r<rows; r++) {
    for (let c=0; c<cols; c++) {
      const v = grid[r][c];
      if (!v || v === 0) continue;
      const col = PAL[v] || v;
      svg += `<rect x="${c*scale}" y="${r*scale}" width="${scale}" height="${scale}" fill="${col}"/>`;
    }
  }
  svg += '</svg>';
  return 'data:image/svg+xml;base64,' + btoa(svg);
}

// ── CHARACTER DEFINITIONS ──────────────────────────────────────────
const CHARS = [
  {
    id:'goku', name:'Goku', sprite:'goku', ssjSprite:'goku_ssj',
    aura:'#ffd700', glow:'#ff6a00', speed:1.4, jumpH:200,
    x:80,  vx:1.4,  flipped:false, state:'walk', timer:100,
    isSSJ:false, y:0, vy:0, jumping:false,
    quotes:['KAMEHAMEHA!!','I need to get stronger!','KAIO-KEN x10!'],
    fightQ:['KAMEHAMEHA!!','KAIO-KEN!!','This ends NOW!'],
    powerQ:["I'M GOING SUPER SAIYAN!",'AAAAHHHH!!!','FULL POWER!!'],
  },
  {
    id:'vegeta', name:'Vegeta', sprite:'vegeta', ssjSprite:null,
    aura:'#8800ff', glow:'#aa00ff', speed:1.6, jumpH:180,
    x:500, vx:-1.6, flipped:true,  state:'walk', timer:120,
    isSSJ:false, y:0, vy:0, jumping:false,
    quotes:['PRINCE OF SAIYANS!','OVER 9000!!','FINAL FLASH!!'],
    fightQ:['FINAL FLASH!!','GALICK GUN!!','Prepare to die!'],
    powerQ:['MY PRIDE...!','VEGETA WINS!!','FINAL BURST!!'],
  },
  {
    id:'piccolo', name:'Piccolo', sprite:'piccolo', ssjSprite:null,
    aura:'#00aa44', glow:'#004422', speed:1.2, jumpH:220,
    x:900, vx:1.2,  flipped:false, state:'idle', timer:200,
    isSSJ:false, y:0, vy:0, jumping:false,
    quotes:['Special Beam Cannon!','Train harder.','MAKANKOSAPPO!!'],
    fightQ:['HELLZONE GRENADE!!','Special Beam Cannon!!','FEEL MY POWER!'],
    powerQ:['Unlimited power...','RISING KI!!','BREAK YOUR LIMITS!'],
  },
  {
    id:'frieza', name:'Frieza', sprite:'frieza', ssjSprite:null,
    aura:'#cc44ff', glow:'#880088', speed:1.3, jumpH:240,
    x:1100,vx:-1.3, flipped:true,  state:'float', timer:180,
    isSSJ:false, y:0, vy:0, jumping:false,
    quotes:['Greatest in the universe!','DEATH BEAM!!','Pathetic fools...'],
    fightQ:['DEATH BALL!!','SUPERNOVA!!','YOU ALL DIE!!'],
    powerQ:['100% POWER!!','UNLIMITED MIGHT!!','TREMBLE!!'],
  },
  {
    id:'gohan', name:'Gohan', sprite:'gohan', ssjSprite:null,
    aura:'#ffd700', glow:'#ff6600', speed:1.5, jumpH:195,
    x:300, vx:-1.5, flipped:true,  state:'walk', timer:110,
    isSSJ:false, y:0, vy:0, jumping:false,
    quotes:["It's over!","MASENKO!!",'THIS POWER...!'],
    fightQ:['MASENKO HA!!','KAMEHAMEHA!!','I WONT LOSE!!'],
    powerQ:['RAAAHHHHH!!!','SSJ2!!!','HIDDEN POWER!!!'],
  },
];

const GRAV = 0.7;
let els = {}, frame = 0;
let imgCache = {};

// Pre-render all sprites
function prerender() {
  Object.keys(SPRITES).forEach(k => { imgCache[k] = buildPixelChar(k, 5); });
}

// ── RENDER SINGLE CHARACTER ────────────────────────────────────────
function buildCharEl(char) {
  const wrap = document.createElement('div');
  wrap.id = 'char-' + char.id;
  wrap.className = 'char-wrap';
  wrap.style.cssText = `left:${char.x}px; bottom:0; z-index:5;`;

  // Aura
  const aura = document.createElement('div');
  aura.className = 'char-aura';
  aura.style.cssText = `width:70px;height:20px;transform:translateX(-50%);background:${char.aura};`;
  wrap.appendChild(aura);

  // Left leg
  const legL = document.createElement('div');
  legL.className = 'leg-l';
  legL.style.cssText = `position:absolute;bottom:10px;left:10px;width:10px;height:22px;background:transparent;transform-origin:top center;`;

  // Right leg
  const legR = document.createElement('div');
  legR.className = 'leg-r';
  legR.style.cssText = `position:absolute;bottom:10px;left:26px;width:10px;height:22px;background:transparent;transform-origin:top center;`;

  // Body img
  const img = document.createElement('img');
  img.src = imgCache[char.sprite] || imgCache['goku'];
  img.style.cssText = `display:block;width:60px;height:auto;image-rendering:pixelated;position:relative;z-index:2;filter:drop-shadow(0 0 6px ${char.aura});`;
  img.draggable = false;
  wrap.appendChild(img);

  // Ki orb (for powerup state)
  const kiOrb = document.createElement('div');
  kiOrb.className = 'ki-orb';
  kiOrb.style.cssText = `width:14px;height:14px;top:-18px;left:50%;transform:translateX(-50%);color:${char.aura};display:none;`;
  wrap.appendChild(kiOrb);

  // Speech bubble
  const bubble = document.createElement('div');
  bubble.className = 'speech-bubble';
  bubble.id = 'bubble-' + char.id;
  const tail = document.createElement('span');
  bubble.appendChild(tail);
  wrap.appendChild(bubble);

  // Name tag
  const name = document.createElement('div');
  name.className = 'char-name';
  name.textContent = char.name.toUpperCase();
  name.style.color = char.aura;
  name.style.textShadow = `0 0 8px ${char.aura}`;
  wrap.appendChild(name);

  wrap.addEventListener('click', e => {
    e.stopPropagation();
    doJump(char);
    speak(char, char.quotes[Math.floor(Math.random()*char.quotes.length)]);
    boom(char.x + 30, window.innerHeight - 80, char.aura);
  });

  return { wrap, img, aura, kiOrb, bubble };
}

function init() {
  prerender();
  const layer = document.getElementById('characters-layer');
  if (!layer) return;
  CHARS.forEach(char => {
    const el = buildCharEl(char);
    layer.appendChild(el.wrap);
    els[char.id] = el;
  });
  requestAnimationFrame(loop);
  setInterval(() => speak(CHARS[Math.floor(Math.random()*CHARS.length)]), 4000);
  setInterval(doInteraction, 7500);
  setInterval(doPowerUp, 12000);
}

function loop() {
  frame++;
  const W = window.innerWidth;

  CHARS.forEach(char => {
    const el = els[char.id];
    if (!el) return;

    // State tick
    char.timer--;
    if (char.timer <= 0) nextState(char);

    // Physics
    if (char.jumping) {
      char.vy += GRAV;
      char.y -= char.vy;
      if (char.y <= 0) { char.y=0; char.jumping=false; char.vy=0; }
    }

    // Movement
    if (char.state==='walk')  char.x += char.vx;
    if (char.state==='run')   char.x += char.vx * 3;
    if (char.state==='fight') char.x += char.vx * 1.2;
    if (char.state==='float') {
      char.x += char.vx * 0.6;
      char.y = 25 + Math.sin(frame * 0.02) * 18;
    }

    // Boundary
    if (char.x > W - 70) { char.x = W-70; char.vx = -Math.abs(char.vx); char.flipped = true; }
    if (char.x < 5)       { char.x = 5;    char.vx =  Math.abs(char.vx); char.flipped = false; }

    // Apply position
    el.wrap.style.left = char.x + 'px';
    el.wrap.style.bottom = Math.max(0, char.y) + 'px';
    el.wrap.style.transform = char.flipped ? 'scaleX(-1)' : 'scaleX(1)';

    // Leg animations based on state
    const speed = char.state==='run' ? '0.2s' : char.state==='walk' ? '0.4s' : '0.8s';
    const legAnim = (char.state==='walk'||char.state==='run') ? `legLeft ${speed} ease-in-out infinite alternate` : 'none';

    // Image glow/filter per state
    if (char.state==='powerup') {
      el.img.style.filter = `drop-shadow(0 0 20px ${char.aura}) drop-shadow(0 0 40px ${char.glow}) brightness(1.5)`;
      el.aura.style.width = '90px'; el.aura.style.height = '30px'; el.aura.style.opacity='0.9';
      el.kiOrb.style.display = 'block';
    } else if (char.state==='fight') {
      el.img.style.filter = `drop-shadow(0 0 12px ${char.aura}) drop-shadow(0 2px 4px #000) brightness(1.2)`;
      el.aura.style.width = '75px'; el.aura.style.height = '22px'; el.aura.style.opacity='0.7';
      el.kiOrb.style.display = 'none';
    } else {
      el.img.style.filter = `drop-shadow(0 0 6px ${char.aura}) drop-shadow(0 2px 6px #000)`;
      el.aura.style.width = '65px'; el.aura.style.height = '16px'; el.aura.style.opacity='0.5';
      el.kiOrb.style.display = 'none';
    }

    // Walk bob animation on the whole wrap
    if (char.state==='walk') {
      el.wrap.style.animation = 'walkBob 0.4s ease-in-out infinite';
    } else if (char.state==='run') {
      el.wrap.style.animation = 'runBob 0.2s ease-in-out infinite';
    } else if (char.state==='idle') {
      el.wrap.style.animation = 'idleBreath 2s ease-in-out infinite';
    } else if (char.state==='powerup') {
      el.wrap.style.animation = 'powerUp 1.5s ease-in-out infinite';
    } else if (char.state==='float') {
      el.wrap.style.animation = 'floatUp 2s ease-in-out infinite';
    } else {
      el.wrap.style.animation = 'none';
    }
  });

  requestAnimationFrame(loop);
}

function nextState(char) {
  const r = Math.random();
  if      (r < 0.28) { char.state='walk';  char.timer=100+Math.random()*150; }
  else if (r < 0.40) { char.state='run';   char.timer=30+Math.random()*50; char.vx=(Math.random()>.5?1:-1)*char.speed; char.flipped=char.vx<0; }
  else if (r < 0.55) { char.state='idle';  char.timer=80+Math.random()*120; }
  else if (r < 0.65) { char.state='jump';  char.timer=60; doJump(char); char.state='walk'; }
  else if (r < 0.78) { char.state='fight'; char.timer=50+Math.random()*60; }
  else if (char.id==='frieza') { char.state='float'; char.timer=120+Math.random()*120; }
  else { char.state='walk'; char.timer=100; }
}

function doJump(char) {
  if (!char.jumping) { char.jumping=true; char.vy = -(char.jumpH * 0.18); }
}

function speak(char, text) {
  text = text || char.quotes[Math.floor(Math.random()*char.quotes.length)];
  const el = els[char.id];
  if (!el) return;
  // Clear old text node
  while (el.bubble.firstChild && el.bubble.firstChild.nodeType===3) el.bubble.removeChild(el.bubble.firstChild);
  const old = el.bubble.querySelector('.btxt');
  if (old) old.remove();
  const sp = document.createElement('span');
  sp.className = 'btxt';
  sp.textContent = text;
  el.bubble.insertBefore(sp, el.bubble.firstChild);
  el.bubble.style.opacity = '1';
  setTimeout(() => { el.bubble.style.opacity='0'; }, 2200);
}

function doInteraction() {
  if (CHARS.length < 2) return;
  let a = Math.floor(Math.random()*CHARS.length);
  let b = Math.floor(Math.random()*CHARS.length);
  while (b===a) b = Math.floor(Math.random()*CHARS.length);
  const from=CHARS[a], to=CHARS[b];
  speak(from, from.fightQ[Math.floor(Math.random()*from.fightQ.length)]);
  from.state='fight'; from.timer=70;
  fireKiBlast(from, to);
}

function fireKiBlast(from, to) {
  const el = document.createElement('div');
  const sx = from.x+30, sy = window.innerHeight-100;
  const ex = to.x+30,   ey = window.innerHeight-100;
  el.style.cssText = `position:fixed;left:${sx}px;top:${sy}px;width:16px;height:16px;border-radius:50%;background:radial-gradient(circle,#fff,${from.aura},transparent);box-shadow:0 0 16px ${from.aura};pointer-events:none;z-index:8;transform:translate(-50%,-50%);`;
  document.body.appendChild(el);
  const dx=ex-sx, dy=ey-sy, dist=Math.sqrt(dx*dx+dy*dy), dur=Math.max(220,dist*.65);
  let t0=null;
  (function step(ts){
    if(!t0)t0=ts;
    const p=Math.min(1,(ts-t0)/dur);
    el.style.left=(sx+dx*p)+'px';
    el.style.top=(sy+dy*p-100*Math.sin(Math.PI*p))+'px';
    el.style.opacity=String(1-p*.3);
    if(p<1){ requestAnimationFrame(step); }
    else { boom(ex,ey,from.aura); el.remove(); speak(to, to.quotes[Math.floor(Math.random()*to.quotes.length)]); }
  })(0);
  requestAnimationFrame(step => { t0=null; (function f(ts){ if(!t0)t0=ts; const p=Math.min(1,(ts-t0)/dur); el.style.left=(sx+dx*p)+'px'; el.style.top=(sy+dy*p-100*Math.sin(Math.PI*p))+'px'; el.style.opacity=String(1-p*.3); if(p<1) requestAnimationFrame(f); else { boom(ex,ey,from.aura); el.remove(); speak(to, to.quotes[Math.floor(Math.random()*to.quotes.length)]); } })(ts); });
}

function boom(x, y, color) {
  for (let i=0; i<6; i++) {
    const e=document.createElement('div');
    const s=20+Math.random()*30;
    e.style.cssText = `position:fixed;left:${x+(Math.random()-.5)*50}px;top:${y+(Math.random()-.5)*40}px;width:${s}px;height:${s}px;border-radius:50%;background:radial-gradient(circle,#fff,${color},transparent);pointer-events:none;z-index:9;animation:explosion .55s ease-out forwards;animation-delay:${i*.04}s;`;
    document.body.appendChild(e);
    setTimeout(()=>e.remove(), 650);
  }
}

function doPowerUp() {
  const char = CHARS[Math.floor(Math.random()*CHARS.length)];
  const el = els[char.id];
  if (!el) return;
  char.state='powerup'; char.timer=100;
  speak(char, char.powerQ[Math.floor(Math.random()*char.powerQ.length)]);
  boom(char.x+30, window.innerHeight-80, char.aura);
  // Goku SSJ
  if (char.id==='goku' && !char.isSSJ && Math.random()>.4) {
    char.isSSJ=true;
    el.img.src = imgCache['goku_ssj'];
    el.aura.style.background='#ffd700';
    setTimeout(() => { char.isSSJ=false; el.img.src=imgCache['goku']; el.aura.style.background=char.aura; }, 15000);
  }
}

document.addEventListener('click', e => {
  if (e.target.closest && e.target.closest('#characters-layer')) return;
  const p=document.createElement('div');
  p.className='ki-particle';
  const s=10+Math.random()*12;
  p.style.cssText=`left:${e.clientX-s/2}px;top:${e.clientY-s/2}px;width:${s}px;height:${s}px;`;
  document.body.appendChild(p);
  setTimeout(()=>p.remove(),600);
});

if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init);
else setTimeout(init,80);
window.dbzBoom=boom;
})();
"""

# ─────────────────────────────────────────────────────────────────────
# DBZ INTRO — fully self-contained, no external assets
# ─────────────────────────────────────────────────────────────────────
DBZ_INTRO = r"""
<div id="dbz-intro" style="position:fixed;inset:0;z-index:99999;background:#000;font-family:'Bangers',cursive;overflow:hidden;">

  <button id="intro-skip"
    style="position:absolute;top:18px;right:18px;z-index:10;background:transparent;
           border:1px solid rgba(255,106,0,.5);color:rgba(255,106,0,.8);
           font-family:'Bangers',cursive;font-size:.9rem;letter-spacing:.15em;
           padding:6px 16px;cursor:pointer;border-radius:2px;"
    onclick="window.__dbzSkip && window.__dbzSkip()">
    SKIP ▶
  </button>

  <!-- FLASH OVERLAY -->
  <div id="iFlash" style="position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none;z-index:5;"></div>

  <!-- PHASE 1: POWER CHARGE -->
  <div id="iCharge" style="position:absolute;inset:0;opacity:0;display:flex;align-items:center;justify-content:center;background:radial-gradient(ellipse at center,#1a0800,#000 70%);">
    <canvas id="iLCanvas" style="position:absolute;inset:0;width:100%;height:100%;opacity:0;"></canvas>

    <div style="position:absolute;top:24px;right:24px;background:rgba(0,0,0,.85);border:2px solid #ff6a00;padding:8px 16px;border-radius:3px;box-shadow:0 0 20px rgba(255,106,0,.4);">
      <div style="font-size:.55rem;color:#c8a878;letter-spacing:.3em;margin-bottom:2px;">POWER LEVEL</div>
      <div id="iPL" style="font-size:2rem;color:#ffd700;letter-spacing:.05em;">000000</div>
    </div>

    <div style="position:absolute;top:24px;left:24px;font-family:'Share Tech Mono',monospace;font-size:.7rem;color:#00ff44;opacity:0;" id="iScout">SCOUTING...</div>

    <div id="iAura" style="position:absolute;bottom:0;left:50%;transform:translateX(-50%);width:60px;height:0;background:linear-gradient(0deg,#ffd700,#ff6a00,transparent);filter:blur(10px);opacity:0;border-radius:50% 50% 0 0;"></div>

    <div id="iShockWrap" style="position:absolute;bottom:30px;left:50%;transform:translateX(-50%);width:0;height:0;pointer-events:none;">
    </div>

    <!-- Pixel Goku silhouette (CSS only) -->
    <div id="iSil" style="position:absolute;bottom:50px;left:50%;transform:translateX(-50%);opacity:0;">
      <canvas id="iSilCanvas" width="96" height="160" style="image-rendering:pixelated;filter:brightness(0) saturate(0) invert(1) sepia(1) saturate(5) hue-rotate(5deg);"></canvas>
    </div>

    <div id="iScream" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%) scale(0.5);font-size:clamp(2.5rem,8vw,6rem);letter-spacing:.08em;opacity:0;background:linear-gradient(135deg,#fff,#ffd700,#ff6a00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;white-space:nowrap;text-align:center;transition:transform .2s,opacity .15s;">
      AAAAHHHHH!!!
    </div>
  </div>

  <!-- PHASE 2: TITLE -->
  <div id="iTitle" style="position:absolute;inset:0;opacity:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:radial-gradient(ellipse at center,#0d0400,#000 80%);">
    <canvas id="iSpeedCanvas" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none;opacity:0.35;"></canvas>

    <div id="iDBalls" style="display:flex;gap:14px;margin-bottom:20px;opacity:0;">
    </div>

    <div id="iTitleText" style="font-size:clamp(2.5rem,10vw,7rem);letter-spacing:.08em;line-height:.95;text-align:center;opacity:0;transform:scale(3);background:linear-gradient(135deg,#fff 0%,#ffd700 35%,#ff6a00 65%,#ff1a1a 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 25px #ff6a0088);">
      CTF
    </div>

    <div id="iSub" style="font-size:clamp(.75rem,2vw,1.1rem);letter-spacing:.4em;color:#ff6a00;margin-top:14px;opacity:0;">⚡ CAPTURE THE FLAG ⚡</div>

    <div id="iBarWrap" style="margin-top:28px;width:min(380px,80vw);opacity:0;">
      <div style="font-size:.6rem;color:#c8a878;letter-spacing:.3em;margin-bottom:5px;text-align:center;">LOADING BATTLE DATA...</div>
      <div style="background:rgba(255,106,0,.15);border:1px solid rgba(255,106,0,.4);border-radius:2px;height:7px;overflow:hidden;">
        <div id="iBar" style="height:100%;width:0%;background:linear-gradient(90deg,#ff6a00,#ffd700);box-shadow:0 0 8px #ffd700;transition:width .04s linear;"></div>
      </div>
    </div>

    <button id="iEnterBtn" onclick="window.__dbzSkip && window.__dbzSkip()"
      style="display:none;margin-top:28px;padding:12px 44px;font-family:'Bangers',cursive;font-size:1.3rem;letter-spacing:.18em;border:2px solid #ffd700;background:linear-gradient(135deg,rgba(255,215,0,.18),rgba(255,106,0,.08));color:#ffd700;cursor:pointer;border-radius:2px;animation:enterpulse 1.4s ease-in-out infinite;">
      ⚡ ENTER THE BATTLE ⚡
    </button>
  </div>

  <!-- PHASE 3: CHARACTER PARADE -->
  <div id="iParade" style="position:absolute;inset:0;opacity:0;background:#000;overflow:hidden;">
    <canvas id="iParadeCanvas" style="position:absolute;inset:0;width:100%;height:100%;opacity:0.4;"></canvas>

    <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;">
      <canvas id="iCharCanvas" width="120" height="200" style="image-rendering:pixelated;display:block;margin:0 auto;transform:scale(0);transition:transform .35s cubic-bezier(.34,1.56,.64,1);filter:drop-shadow(0 0 20px #ffd700);"></canvas>
      <div id="iCharName" style="font-size:clamp(2rem,6vw,3.5rem);letter-spacing:.15em;color:#ffd700;margin-top:8px;opacity:0;transform:translateY(16px);transition:all .35s ease;"></div>
      <div id="iCharQuote" style="font-size:clamp(.85rem,2vw,1.2rem);letter-spacing:.08em;color:#ff6a00;margin-top:4px;opacity:0;transform:translateY(8px);transition:all .3s ease .1s;"></div>
    </div>

    <div id="iVsFlash" style="position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none;"></div>
  </div>

</div>

<style>
@keyframes enterpulse{0%,100%{box-shadow:0 0 16px rgba(255,215,0,.3),0 0 32px rgba(255,106,0,.15)}50%{box-shadow:0 0 32px rgba(255,215,0,.6),0 0 64px rgba(255,106,0,.35)}}
@keyframes dballspin{0%{box-shadow:0 0 8px rgba(255,215,0,.4)}50%{box-shadow:0 0 20px rgba(255,215,0,.9),0 0 40px rgba(255,106,0,.4)}100%{box-shadow:0 0 8px rgba(255,215,0,.4)}}
</style>

<script>
(function(){

// ── ONLY PLAY ONCE PER SESSION ──
if(sessionStorage.getItem('dbz_done')){
  document.getElementById('dbz-intro').style.display='none';
  return;
}

// ── Pixel palette + sprite (same as PIXEL_CHARS_JS) ──
const PAL2={W:'#fff',SK:'#f5c97a',SK2:'#e8a85a',DK:'#1a0800',BK:'#111',OR:'#ff6a00',YL:'#ffd700',RD:'#ff2200',BL:'#1a44cc',PU:'#7700cc',GR:'#116611',GY:'#888',LG:'#22aa33',PK:'#ff44cc',WH:'#eeeeff',NV:'#001166',OG:'#ff8800',TL:'#00bbaa',SL:'#ccccdd',CY:'#00ddff'};

const GOKU_GRID=[
  [0,0,'BK','BK','BK','BK','BK','BK','BK',0,0,0],
  [0,'BK','BK','BK','BK','BK','BK','BK','BK','BK',0,0],
  ['BK','BK','BK','SK','SK','SK','SK','SK','BK','BK','BK',0],
  [0,'BK','SK','SK','SK','SK','SK','SK','SK','BK',0,0],
  [0,'SK','SK','W','BK','SK','W','BK','SK','SK',0,0],
  [0,'SK','SK','SK','SK','SK','SK','SK','SK','SK',0,0],
  [0,'SK','SK','SK','OR','SK','SK','OR','SK','SK',0,0],
  [0,0,'SK','SK','SK','SK','SK','SK','SK',0,0,0],
  [0,0,0,'SK','SK','SK','SK','SK',0,0,0,0],
  [0,'OR','OR','OR','OR','OR','OR','OR','OR','OR',0,0],
  [0,'OR','BL','OR','OR','OR','OR','OR','BL','OR',0,0],
  ['OR','OR','OR','OR','OR','OR','OR','OR','OR','OR','OR',0],
  [0,'BL','BL','BL','BL','BL','BL','BL','BL','BL',0,0],
  [0,'BL','BL','OR','BL','BL','BL','OR','BL','BL',0,0],
  [0,'BL','BL','OR','BL','BL','BL','OR','BL','BL',0,0],
  [0,'BL','BL','OR','BL','BL','BL','OR','BL','BL',0,0],
  [0,0,'OR','OR','BL',0,0,'BL','OR','OR',0,0],
  [0,0,'OR','OR','BL',0,0,'BL','OR','OR',0,0],
  [0,0,'RD','RD','RD',0,0,'RD','RD','RD',0,0],
  [0,0,'RD','RD','RD',0,0,'RD','RD','RD',0,0],
];

const CHARS_PARADE=[
  {name:'GOKU',    grid:GOKU_GRID,             aura:'#ffd700',quote:'"KAMEHAMEHA!!"'},
  {name:'VEGETA',  grid:null, aura:'#8800ff', quote:'"OVER 9000!!"'},
  {name:'PICCOLO', grid:null, aura:'#00aa44', quote:'"SPECIAL BEAM CANNON!!"'},
  {name:'GOHAN',   grid:null, aura:'#ffd700', quote:'"THIS POWER...!"'},
  {name:'FRIEZA',  grid:null, aura:'#cc44ff', quote:'"KNEEL BEFORE ME!!"'},
];

// Vegeta grid
const VG=[
  [0,'BK','BK','BK','BK','BK','BK','BK','BK','BK',0,0],
  ['BK','BK','BK','BK','BK','BK','BK','BK','BK','BK','BK',0],
  ['BK','BK','BK','SK','SK','SK','SK','SK','BK','BK','BK',0],
  [0,'BK','SK','SK','SK','SK','SK','SK','SK','BK',0,0],
  [0,'SK','SK','W','BK','SK','W','BK','SK','SK',0,0],
  [0,'SK','SK','SK','SK','SK','SK','SK','SK','SK',0,0],
  [0,'SK','SK','SK',0,'SK','SK',0,'SK','SK',0,0],
  [0,0,'SK','SK','SK','SK','SK','SK','SK',0,0,0],
  [0,0,0,'SK','SK','SK','SK','SK',0,0,0,0],
  [0,'WH','WH','WH','WH','WH','WH','WH','WH','WH',0,0],
  [0,'WH','YL','WH','WH','WH','WH','WH','YL','WH',0,0],
  ['WH','WH','WH','WH','WH','WH','WH','WH','WH','WH','WH',0],
  [0,'BK','BK','BK','BK','BK','BK','BK','BK','BK',0,0],
  [0,'NV','NV','WH','NV','NV','NV','WH','NV','NV',0,0],
  [0,'NV','NV','WH','NV','NV','NV','WH','NV','NV',0,0],
  [0,'NV','NV','WH','NV','NV','NV','WH','NV','NV',0,0],
  [0,0,'NV','NV','NV',0,0,'NV','NV','NV',0,0],
  [0,0,'NV','NV','NV',0,0,'NV','NV','NV',0,0],
  [0,0,'WH','WH','WH',0,0,'WH','WH','WH',0,0],
  [0,0,'WH','WH','WH',0,0,'WH','WH','WH',0,0],
];
const PIC=[
  [0,0,0,'LG','LG',0,0,'LG','LG',0,0,0],
  [0,0,0,'LG','LG',0,0,'LG','LG',0,0,0],
  [0,0,'LG','LG','LG','LG','LG','LG','LG','LG',0,0],
  [0,'LG','LG','LG','LG','LG','LG','LG','LG','LG','LG',0],
  [0,'LG','LG','W','BK','LG','W','BK','LG','LG',0,0],
  [0,'LG','LG','LG','LG','LG','LG','LG','LG','LG',0,0],
  [0,'LG','LG','LG','LG','LG','LG','LG','LG','LG',0,0],
  [0,0,'LG','LG','LG','LG','LG','LG','LG',0,0,0],
  [0,0,0,'LG','LG','LG','LG','LG',0,0,0,0],
  [0,'PU','PU','PU','PU','PU','PU','PU','PU','PU',0,0],
  [0,'PU','WH','PU','PU','PU','PU','PU','WH','PU',0,0],
  ['PU','PU','PU','PU','PU','PU','PU','PU','PU','PU','PU',0],
  [0,'WH','WH','WH','WH','WH','WH','WH','WH','WH',0,0],
  [0,'PU','PU','WH','PU','PU','PU','WH','PU','PU',0,0],
  [0,'PU','PU','WH','PU','PU','PU','WH','PU','PU',0,0],
  [0,'PU','PU','WH','PU','PU','PU','WH','PU','PU',0,0],
  [0,0,'PU','PU','PU',0,0,'PU','PU','PU',0,0],
  [0,0,'PU','PU','PU',0,0,'PU','PU','PU',0,0],
  [0,0,'WH','WH','WH',0,0,'WH','WH','WH',0,0],
  [0,0,'WH','WH','WH',0,0,'WH','WH','WH',0,0],
];
const GH=[
  [0,0,'BK','BK','BK','BK','BK','BK',0,0,0,0],
  [0,'BK','BK','BK','BK','BK','BK','BK','BK','BK',0,0],
  ['BK','BK','BK','SK','SK','SK','SK','SK','BK','BK',0,0],
  [0,'BK','SK','SK','SK','SK','SK','SK','SK','BK',0,0],
  [0,'SK','SK','W','BK','SK','W','BK','SK','SK',0,0],
  [0,'SK','SK','SK','SK','SK','SK','SK','SK','SK',0,0],
  [0,'SK','SK','SK',0,'SK','SK',0,'SK','SK',0,0],
  [0,0,'SK','SK','SK','SK','SK','SK','SK',0,0,0],
  [0,0,0,'SK','SK','SK','SK','SK',0,0,0,0],
  [0,'PU','PU','PU','PU','PU','PU','PU','PU','PU',0,0],
  [0,'PU','YL','PU','PU','PU','PU','PU','YL','PU',0,0],
  ['PU','PU','PU','PU','PU','PU','PU','PU','PU','PU','PU',0],
  [0,'YL','YL','YL','YL','YL','YL','YL','YL','YL',0,0],
  [0,'BL','BL','YL','BL','BL','BL','YL','BL','BL',0,0],
  [0,'BL','BL','YL','BL','BL','BL','YL','BL','BL',0,0],
  [0,'BL','BL','YL','BL','BL','BL','YL','BL','BL',0,0],
  [0,0,'BL','BL','BL',0,0,'BL','BL','BL',0,0],
  [0,0,'BL','BL','BL',0,0,'BL','BL','BL',0,0],
  [0,0,'BK','BK','BK',0,0,'BK','BK','BK',0,0],
  [0,0,'BK','BK','BK',0,0,'BK','BK','BK',0,0],
];
const FZ=[
  [0,0,'WH','WH','WH','WH','WH','WH','WH',0,0,0],
  [0,'WH','WH','WH','WH','WH','WH','WH','WH','WH',0,0],
  [0,'WH','PU','WH','WH','WH','WH','WH','PU','WH',0,0],
  [0,'WH','WH','WH','WH','WH','WH','WH','WH','WH',0,0],
  [0,'WH','WH','RD','BK','WH','RD','BK','WH','WH',0,0],
  [0,'WH','WH','WH','WH','WH','WH','WH','WH','WH',0,0],
  [0,'WH','PU','WH','WH','WH','WH','WH','PU','WH',0,0],
  [0,0,'WH','WH','WH','WH','WH','WH','WH',0,0,0],
  [0,0,0,'WH','WH','WH','WH','WH',0,0,0,0],
  [0,'WH','WH','WH','WH','WH','WH','WH','WH','WH',0,0],
  [0,'WH','PU','WH','WH','WH','WH','WH','PU','WH',0,0],
  ['WH','WH','WH','WH','WH','WH','WH','WH','WH','WH','WH',0],
  [0,'PU','PU','PU','PU','PU','PU','PU','PU','PU',0,0],
  [0,'WH','WH','PU','WH','WH','WH','PU','WH','WH',0,0],
  [0,'WH','WH','PU','WH','WH','WH','PU','WH','WH',0,0],
  [0,'WH','WH','PU','WH','WH','WH','PU','WH','WH',0,0],
  [0,0,'WH','WH','WH',0,0,'WH','WH','WH',0,0],
  [0,0,'WH','WH','WH',0,0,'WH','WH','WH',0,0],
  [0,0,'PU','PU','PU',0,0,'PU','PU','PU',0,0],
  [0,0,'PU','PU','PU',0,0,'PU','PU','PU',0,0],
];
CHARS_PARADE[1].grid=VG;
CHARS_PARADE[2].grid=PIC;
CHARS_PARADE[3].grid=GH;
CHARS_PARADE[4].grid=FZ;

function drawGrid(canvas, grid, scale) {
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0,0,canvas.width,canvas.height);
  grid.forEach((row,r)=>{
    row.forEach((v,c)=>{
      if(!v||v===0) return;
      ctx.fillStyle = PAL2[v]||v;
      ctx.fillRect(c*scale, r*scale, scale, scale);
    });
  });
}

// ── LIGHTNING ──
function drawLightning(canvas, color, n) {
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.offsetWidth||window.innerWidth;
  canvas.height = canvas.offsetHeight||window.innerHeight;
  ctx.clearRect(0,0,canvas.width,canvas.height);
  const cx=canvas.width/2, cy=canvas.height*.6;
  for(let i=0;i<n;i++){
    ctx.beginPath(); ctx.strokeStyle=color;
    ctx.lineWidth=Math.random()*2+.5; ctx.globalAlpha=Math.random()*.7+.2;
    let x=cx+(Math.random()-.5)*180, y=cy+(Math.random()-.5)*180;
    ctx.moveTo(x,y);
    for(let j=0;j<5;j++){x+=(Math.random()-.5)*110;y+=(Math.random()-.5)*110;ctx.lineTo(x,y);}
    ctx.stroke();
  }
  ctx.globalAlpha=1;
}

// ── SPEED LINES ──
function drawSpeed(canvas) {
  const ctx = canvas.getContext('2d');
  canvas.width=canvas.offsetWidth||window.innerWidth;
  canvas.height=canvas.offsetHeight||window.innerHeight;
  ctx.clearRect(0,0,canvas.width,canvas.height);
  const cx=canvas.width/2, cy=canvas.height/2;
  for(let i=0;i<70;i++){
    const a=(i/70)*Math.PI*2;
    const inner=50+Math.random()*30;
    const outer=Math.max(canvas.width,canvas.height)*1.2;
    ctx.beginPath();
    ctx.strokeStyle=i%3===0?'#ffd700':i%3===1?'#ff6a00':'#ffffff33';
    ctx.lineWidth=Math.random()*2.5+.3;
    ctx.globalAlpha=.25+Math.random()*.25;
    ctx.moveTo(cx+Math.cos(a)*inner,cy+Math.sin(a)*inner);
    ctx.lineTo(cx+Math.cos(a)*outer,cy+Math.sin(a)*outer);
    ctx.stroke();
  }
  ctx.globalAlpha=1;
}

function drawParadeLines(canvas,color,t){
  const ctx=canvas.getContext('2d');
  canvas.width=canvas.offsetWidth||window.innerWidth;
  canvas.height=canvas.offsetHeight||window.innerHeight;
  ctx.clearRect(0,0,canvas.width,canvas.height);
  const cx=canvas.width/2;
  for(let i=0;i<55;i++){
    const a=(i/55)*Math.PI*2+t;
    const inner=60;
    const outer=550+Math.sin(t*3+i)*80;
    ctx.beginPath(); ctx.strokeStyle=i%2===0?color:'#ffffff18';
    ctx.lineWidth=Math.random()*1.8+.3;
    ctx.globalAlpha=.25+Math.sin(t*2+i)*.12;
    ctx.moveTo(cx+Math.cos(a)*inner, canvas.height*.35+Math.sin(a)*inner*.3);
    ctx.lineTo(cx+Math.cos(a)*outer, canvas.height*.35+Math.sin(a)*outer*.3);
    ctx.stroke();
  }
  ctx.globalAlpha=1;
}

// ── DRAGON BALLS ──
function makeDball(size){
  const c=document.createElement('canvas'); c.width=size; c.height=size;
  const ctx=c.getContext('2d');
  const g=ctx.createRadialGradient(size*.35,size*.35,0,size*.5,size*.5,size*.5);
  g.addColorStop(0,'#fffcdd'); g.addColorStop(.4,'#ffd700'); g.addColorStop(.8,'#ff6a00'); g.addColorStop(1,'#8b4500');
  ctx.beginPath(); ctx.arc(size/2,size/2,size/2,0,Math.PI*2); ctx.fillStyle=g; ctx.fill();
  ctx.fillStyle='#cc3300';
  [[.5,.38],[.38,.5],[.62,.5],[.5,.62],[.38,.38],[.62,.62],[.5,.5]].forEach(([x,y],i)=>{
    ctx.beginPath(); ctx.arc(x*size,y*size,size*.07,0,Math.PI*2);
    if(i<7)ctx.fill();
  });
  return c.toDataURL();
}

const sleep = ms => new Promise(r=>setTimeout(r,ms));
let running = true;

window.__dbzSkip = function(){
  running=false;
  const intro=document.getElementById('dbz-intro');
  intro.style.transition='opacity .4s'; intro.style.opacity='0';
  setTimeout(()=>{ intro.style.display='none'; sessionStorage.setItem('dbz_done','1'); },400);
};

async function run(){
  const iFlash=document.getElementById('iFlash');
  const iCharge=document.getElementById('iCharge');
  const iTitle=document.getElementById('iTitle');
  const iParade=document.getElementById('iParade');

  const fade=(el,o,d=300)=>new Promise(r=>{
    el.style.transition=`opacity ${d}ms`;
    el.style.opacity=o;
    setTimeout(r,d+20);
  });

  // ── PHASE 0: Flash ──
  await sleep(150);
  if(!running)return;
  await fade(iFlash,1,60); await fade(iFlash,0,60);
  await sleep(80);
  await fade(iFlash,1,50); await fade(iFlash,0,80);

  // ── PHASE 1: Energy Charge ──
  if(!running)return;
  await fade(iCharge,1,300);

  const scout=document.getElementById('iScout');
  scout.style.transition='opacity .3s'; scout.style.opacity='1';

  // Power level count
  const plEl=document.getElementById('iPL');
  let plVal=0, plTarget=530000;
  const plInterval=setInterval(()=>{
    if(!running){clearInterval(plInterval);return;}
    plVal=Math.min(plVal+Math.floor(plTarget/120)+1000,plTarget);
    plEl.textContent=String(plVal).padStart(6,'0');
    if(plVal>=plTarget)clearInterval(plInterval);
  },20);

  // Aura rise
  const iAura=document.getElementById('iAura');
  iAura.style.transition='height 2s ease-out,opacity .3s';
  iAura.style.opacity='0.9';
  setTimeout(()=>{iAura.style.height='70vh';},50);

  // Pixel silhouette
  const silCanvas=document.getElementById('iSilCanvas');
  silCanvas.width=120; silCanvas.height=160;
  drawGrid(silCanvas,GOKU_GRID,10);
  const iSil=document.getElementById('iSil');
  await sleep(500);
  if(!running)return;
  iSil.style.transition='opacity .4s'; iSil.style.opacity='1';

  // Shockwaves
  const shockWrap=document.getElementById('iShockWrap');
  [['#ff6a00',600,0],['#ffd700',800,150],['#ffffff88',1000,300]].forEach(([col,size,delay])=>{
    setTimeout(()=>{
      const s=document.createElement('div');
      s.style.cssText=`position:absolute;left:50%;top:50%;border-radius:50%;border:3px solid ${col};width:0;height:0;margin-left:0;margin-top:0;opacity:1;transition:all 700ms ease-out;`;
      shockWrap.appendChild(s);
      setTimeout(()=>{
        s.style.width=size+'px'; s.style.height=Math.round(size*.35)+'px';
        s.style.marginLeft=-(size/2)+'px'; s.style.marginTop=-(size*.175)+'px';
        s.style.opacity='0';
      },30);
      setTimeout(()=>s.remove(),800);
    },delay);
  });

  // Lightning
  await sleep(600);
  if(!running)return;
  const lc=document.getElementById('iLCanvas');
  lc.style.transition='opacity .2s'; lc.style.opacity='0.8';
  let lTick=0;
  const lInterval=setInterval(()=>{
    if(!running){clearInterval(lInterval);return;}
    drawLightning(lc,lTick%2===0?'#ffd700':'#fff',7);
    if(++lTick>18)clearInterval(lInterval);
  },100);

  // Scream
  await sleep(400);
  if(!running)return;
  const scr=document.getElementById('iScream');
  scr.style.opacity='1'; scr.style.transform='translate(-50%,-50%) scale(1)';
  await sleep(180); scr.style.transform='translate(-50%,-50%) scale(1.12)';
  await sleep(180); scr.style.transform='translate(-50%,-50%) scale(0.97)';

  // Scouter breaks
  await sleep(350);
  if(!running)return;
  scout.textContent="IT'S OVER 9000!!";
  scout.style.color='#ff0000'; scout.style.fontSize='1rem';

  await sleep(700);
  if(!running)return;

  // Flash transition
  await fade(iFlash,1,70);
  iCharge.style.opacity='0';
  await fade(iFlash,0,80);

  // ── PHASE 2: Title ──
  if(!running)return;
  await fade(iTitle,1,350);

  // Speed lines
  const sc=document.getElementById('iSpeedCanvas');
  drawSpeed(sc);

  // Dragon balls
  const dbWrap=document.getElementById('iDBalls');
  const dbImg=makeDball(30);
  for(let i=0;i<7;i++){
    const img=document.createElement('img');
    img.src=dbImg; img.width=30; img.height=30;
    img.style.cssText=`border-radius:50%;box-shadow:0 0 10px rgba(255,215,0,.5);animation:dballspin 2s ease-in-out ${i*.12}s infinite;transform:translateY(-30px);opacity:0;transition:transform .45s cubic-bezier(.34,1.56,.64,1) ${i*.08}s, opacity .3s ${i*.08}s;`;
    dbWrap.appendChild(img);
  }
  dbWrap.style.transition='opacity .2s'; dbWrap.style.opacity='1';
  await sleep(50);
  dbWrap.querySelectorAll('img').forEach(img=>{ img.style.transform='translateY(0)'; img.style.opacity='1'; });

  await sleep(500);
  if(!running)return;

  // Title slam
  const tEl=document.getElementById('iTitleText');
  const pgTitle=document.title.replace(/\s*-.*$/,'').trim()||'CTF';
  tEl.textContent=pgTitle;
  tEl.style.transition='none'; tEl.style.opacity='0'; tEl.style.transform='scale(4)';
  await sleep(30);
  tEl.style.transition='all .3s cubic-bezier(.34,1.56,.64,1)';
  tEl.style.opacity='1'; tEl.style.transform='scale(1)';

  // Screen shake
  const intro=document.getElementById('dbz-intro');
  ['-4px,2px','4px,-3px','-2px,3px','1px,-1px','0,0'].forEach((t,i)=>{
    setTimeout(()=>{const[x,y]=t.split(',');intro.style.transform=`translate(${x},${y})`;},i*45);
  });

  await sleep(280);
  if(!running)return;

  const sub=document.getElementById('iSub');
  sub.style.transition='opacity .4s,transform .4s'; sub.style.opacity='1'; sub.style.transform='translateY(0)';

  // Loading bar
  await sleep(200);
  if(!running)return;
  const bWrap=document.getElementById('iBarWrap');
  bWrap.style.transition='opacity .3s'; bWrap.style.opacity='1';
  const bar=document.getElementById('iBar');
  let bp=0;
  const barInterval=setInterval(()=>{
    if(!running){clearInterval(barInterval);return;}
    bp=Math.min(100,bp+2);
    bar.style.width=bp+'%';
    if(bp>=100)clearInterval(barInterval);
  },28);

  await sleep(1700);
  if(!running)return;

  // Flash to parade
  await fade(iFlash,1,70);
  iTitle.style.opacity='0';
  await fade(iFlash,0,80);

  // ── PHASE 3: Character Parade ──
  if(!running)return;
  await fade(iParade,1,300);

  let parT=0;
  const pCanvas=document.getElementById('iParadeCanvas');
  let parAF=null;
  function paradeLoop(){
    if(!running)return;
    drawParadeLines(pCanvas,CHARS_PARADE[Math.min(charIdx,CHARS_PARADE.length-1)].aura+'88',parT);
    parT+=0.04;
    parAF=requestAnimationFrame(paradeLoop);
  }
  let charIdx=0;
  paradeLoop();

  const cCanvas=document.getElementById('iCharCanvas');
  cCanvas.width=120; cCanvas.height=160;
  const cName=document.getElementById('iCharName');
  const cQuote=document.getElementById('iCharQuote');
  const vsFlash=document.getElementById('iVsFlash');

  for(charIdx=0;charIdx<CHARS_PARADE.length;charIdx++){
    if(!running)break;
    const cd=CHARS_PARADE[charIdx];
    // Reset
    cCanvas.style.transform='scale(0)';
    cName.style.opacity='0'; cName.style.transform='translateY(16px)';
    cQuote.style.opacity='0'; cQuote.style.transform='translateY(8px)';
    vsFlash.style.opacity='0';

    await sleep(80);
    if(!running)break;

    drawGrid(cCanvas,cd.grid,10);
    cName.textContent=cd.name;
    cName.style.color=cd.aura;
    cName.style.textShadow=`0 0 20px ${cd.aura}`;
    cQuote.textContent=cd.quote;
    cCanvas.style.filter=`drop-shadow(0 0 20px ${cd.aura}) drop-shadow(0 0 40px ${cd.aura}88)`;

    cCanvas.style.transform='scale(1)';
    await sleep(350);
    if(!running)break;
    cName.style.opacity='1'; cName.style.transform='translateY(0)';
    await sleep(280);
    if(!running)break;
    cQuote.style.opacity='1'; cQuote.style.transform='translateY(0)';

    // Flash
    await sleep(120);
    if(!running)break;
    vsFlash.style.transition='opacity .08s'; vsFlash.style.background=`radial-gradient(ellipse at center,rgba(255,255,255,.88),${cd.aura}66,transparent 60%)`;
    vsFlash.style.opacity='0.6';
    await sleep(80); vsFlash.style.transition='opacity .35s'; vsFlash.style.opacity='0';
    await sleep(charIdx<CHARS_PARADE.length-1?1200:600);
  }

  if(parAF) cancelAnimationFrame(parAF);
  if(!running)return;

  // Final: show enter button
  await fade(iFlash,1,80);
  iParade.style.opacity='0';
  await fade(iFlash,0,80);
  iTitle.style.opacity='1';
  const enterBtn=document.getElementById('iEnterBtn');
  const barWrapEl=document.getElementById('iBarWrap');
  if(enterBtn) enterBtn.style.display='block';
  if(barWrapEl) barWrapEl.style.display='none';

  // Auto-dismiss after 4s
  setTimeout(()=>{ if(running && window.__dbzSkip) window.__dbzSkip(); },4000);
}

run();
})();
</script>
"""

BASE_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');
:root{--orange:#ff6a00;--yellow:#ffd700;--gold:#ffb300;--red:#ff1a1a;--blue:#00aaff;--white:#fff;--dark:#0a0500;--card:#120800;--border:#ff6a0044;--glow:#ff6a00;--ki:#ffe066;--aura:#ff4400}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--dark);color:#f5e6c8;font-family:'Rajdhani',sans-serif;min-height:100vh;overflow-x:hidden;cursor:crosshair}
body::before{content:'';position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 80% 60% at 50% 0%,#ff6a0022,transparent 70%),radial-gradient(ellipse 40% 40% at 80% 80%,#ffd70011,transparent 60%),linear-gradient(180deg,#0a0500,#0d0300 50%,#080200);pointer-events:none}
body::after{content:'';position:fixed;inset:0;z-index:0;background-image:radial-gradient(circle 1px at 20% 30%,#ff6a0033,transparent 1px),radial-gradient(circle 1px at 80% 70%,#ffd70022,transparent 1px),radial-gradient(circle 2px at 10% 80%,#ff6a0044,transparent 2px),radial-gradient(circle 1px at 90% 20%,#ffd70033,transparent 1px);animation:stardrift 20s linear infinite;pointer-events:none}
@keyframes stardrift{0%{transform:translateY(0)}100%{transform:translateY(-100px)}}
#characters-layer{position:fixed;inset:0;z-index:4;pointer-events:none;overflow:hidden}
#characters-layer > div{pointer-events:auto}
@keyframes explosion{0%{transform:scale(0);opacity:1}60%{opacity:.8}100%{transform:scale(4);opacity:0}}
.energy-lines{position:fixed;inset:0;z-index:1;pointer-events:none;overflow:hidden}
.energy-lines span{position:absolute;height:1px;background:linear-gradient(90deg,transparent,#ff6a0055,transparent);animation:energyflow 3s linear infinite;opacity:0}
@keyframes energyflow{0%{opacity:0;transform:scaleX(0) translateX(-100%)}20%{opacity:1}80%{opacity:1}100%{opacity:0;transform:scaleX(1) translateX(100%)}}
.header{position:sticky;top:0;z-index:100;padding:1rem 2rem;display:flex;align-items:center;justify-content:space-between;background:linear-gradient(180deg,rgba(10,5,0,.98),rgba(10,5,0,.9));border-bottom:2px solid var(--orange);box-shadow:0 2px 30px #ff6a0044}
.header::after{content:'';position:absolute;bottom:-4px;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--yellow),var(--orange),var(--yellow),transparent);animation:headershine 3s linear infinite}
@keyframes headershine{0%{opacity:.3}50%{opacity:1}100%{opacity:.3}}
.logo{font-family:'Bangers',cursive;font-size:2rem;letter-spacing:.15em;text-decoration:none;background:linear-gradient(135deg,var(--yellow),var(--orange),var(--red));-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 10px #ff6a0088);transition:filter .3s}
.logo:hover{filter:drop-shadow(0 0 20px #ffd700)}
.logo span{background:linear-gradient(135deg,#fff,var(--yellow));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.power-level{font-family:'Bangers',cursive;font-size:.9rem;letter-spacing:.1em;color:var(--yellow);border:1px solid var(--orange);padding:4px 12px;border-radius:2px;background:rgba(255,106,0,.1);animation:powerpulse 2s ease-in-out infinite}
@keyframes powerpulse{0%,100%{box-shadow:0 0 10px #ff6a0033}50%{box-shadow:0 0 20px #ff6a0077}}
nav{display:flex;align-items:center;gap:1.5rem}
nav a{color:#c8a878;text-decoration:none;font-family:'Rajdhani',sans-serif;font-weight:700;font-size:.85rem;letter-spacing:.15em;text-transform:uppercase;transition:all .2s;position:relative}
nav a::after{content:'';position:absolute;bottom:-4px;left:0;right:0;height:2px;background:var(--orange);transform:scaleX(0);transition:transform .2s}
nav a:hover{color:var(--yellow);text-shadow:0 0 10px #ffd70088}
nav a:hover::after,nav a.active::after{transform:scaleX(1)}
nav a.active{color:var(--orange)}
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
.container{max-width:480px;margin:4rem auto;padding:0 1rem;position:relative;z-index:10}
.wide{max-width:1100px;margin:2rem auto;padding:0 1rem;position:relative;z-index:10}
.card{background:linear-gradient(135deg,rgba(18,8,0,.97),rgba(10,5,0,.99));border:1px solid var(--orange);border-radius:4px;padding:2rem;box-shadow:0 0 40px #ff6a0022,inset 0 0 40px rgba(255,106,0,.03);position:relative;overflow:hidden}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,transparent,var(--orange),var(--yellow),var(--orange),transparent);animation:cardshine 4s linear infinite}
@keyframes cardshine{0%{opacity:.5}50%{opacity:1}100%{opacity:.5}}
.card h2{font-family:'Bangers',cursive;font-size:1.8rem;letter-spacing:.2em;color:var(--orange);margin-bottom:1.5rem;text-shadow:0 0 20px #ff6a0066}
.form-group{margin-bottom:1.2rem}
.form-group label{display:block;font-size:.75rem;color:#c8a878;letter-spacing:.15em;margin-bottom:.4rem;font-family:'Rajdhani',sans-serif;font-weight:700;text-transform:uppercase}
.form-group input{width:100%;padding:.75rem 1rem;background:rgba(255,106,0,.05);border:1px solid rgba(255,106,0,.3);color:#f5e6c8;font-family:'Share Tech Mono',monospace;font-size:.9rem;border-radius:2px;outline:none;transition:all .2s}
.form-group input:focus{border-color:var(--orange);box-shadow:0 0 15px rgba(255,106,0,.3);background:rgba(255,106,0,.08)}
.form-group input::placeholder{color:#5a3a20}
.pw-wrap{position:relative}
.pw-wrap input{padding-right:3rem}
.pw-toggle{position:absolute;right:.75rem;top:50%;transform:translateY(-50%);background:none;border:none;color:#c8a878;cursor:pointer;font-size:1rem;padding:0;line-height:1;transition:color .2s}
.pw-toggle:hover{color:var(--yellow)}
.alert{padding:.75rem 1rem;border-radius:2px;margin-bottom:1rem;font-size:.9rem;font-weight:600}
.alert-error{background:rgba(255,26,26,.1);border:1px solid rgba(255,26,26,.4);color:#ff6666}
.alert-success{background:rgba(255,215,0,.1);border:1px solid rgba(255,215,0,.4);color:var(--yellow)}
.link{color:var(--orange);text-decoration:none;font-size:.85rem;font-weight:600}
.link:hover{color:var(--yellow);text-shadow:0 0 8px #ffd70088}
.text-center{text-align:center;margin-top:1rem}
table{width:100%;border-collapse:collapse}
th{text-align:left;padding:.75rem 1rem;font-size:.95rem;letter-spacing:.15em;color:var(--orange);border-bottom:2px solid rgba(255,106,0,.3);font-family:'Bangers',cursive}
td{padding:.75rem 1rem;border-bottom:1px solid rgba(255,106,0,.1);font-size:.9rem}
tr:hover td{background:rgba(255,106,0,.05)}
.badge{font-size:.7rem;padding:2px 8px;border-radius:2px;letter-spacing:.1em;font-weight:700}
.badge-green{background:rgba(0,255,100,.1);color:#00ff88;border:1px solid rgba(0,255,100,.3)}
.badge-red{background:rgba(255,26,26,.1);color:#ff4444;border:1px solid rgba(255,26,26,.3)}
.badge-blue{background:rgba(0,170,255,.1);color:var(--blue);border:1px solid rgba(0,170,255,.3)}
.badge-yellow{background:rgba(255,215,0,.1);color:var(--yellow);border:1px solid rgba(255,215,0,.3)}
.stat-card{background:linear-gradient(135deg,rgba(18,8,0,.9),rgba(10,5,0,.95));border:1px solid rgba(255,106,0,.3);border-radius:4px;padding:1.5rem;text-align:center;position:relative;overflow:hidden;transition:all .3s;cursor:default}
.stat-card:hover{border-color:var(--orange);box-shadow:0 0 20px #ff6a0044;transform:translateY(-3px)}
.stat-value{font-family:'Bangers',cursive;font-size:2.5rem;background:linear-gradient(135deg,var(--yellow),var(--orange));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.stat-label{font-size:.75rem;color:#c8a878;letter-spacing:.15em;margin-top:.25rem;font-weight:700;text-transform:uppercase}
.section-title{font-family:'Bangers',cursive;font-size:1.5rem;color:var(--orange);letter-spacing:.2em;margin-bottom:1.5rem;padding-bottom:.5rem;border-bottom:2px solid rgba(255,106,0,.3);text-shadow:0 0 15px #ff6a0055}
.tabs{display:flex;margin-bottom:2rem}
.tab{padding:.75rem 1.5rem;cursor:pointer;border:1px solid rgba(255,106,0,.3);border-right:none;font-family:'Bangers',cursive;font-size:1rem;letter-spacing:.15em;color:#c8a878;transition:all .2s;text-transform:uppercase}
.tab:last-child{border-right:1px solid rgba(255,106,0,.3)}
.tab:hover{color:var(--yellow);background:rgba(255,106,0,.1)}
.tab.active{color:var(--orange);background:rgba(255,106,0,.15);border-color:var(--orange);box-shadow:inset 0 -2px 0 var(--orange)}
.panel{display:none}.panel.active{display:block}
.hero{text-align:center;padding:4rem 2rem 2rem;position:relative;z-index:10}
.dragon-radar{position:relative;width:140px;height:140px;margin:0 auto 2rem}
.radar-circle{position:absolute;inset:0;border-radius:50%;border:2px solid var(--orange);animation:radarping 2s ease-out infinite}
.radar-circle:nth-child(2){animation-delay:.5s;border-color:var(--yellow)}
.radar-circle:nth-child(3){animation-delay:1s;border-color:var(--red);opacity:.5}
@keyframes radarping{0%{transform:scale(.3);opacity:1}100%{transform:scale(1.5);opacity:0}}
.radar-dot{position:absolute;top:50%;left:50%;width:16px;height:16px;border-radius:50%;background:radial-gradient(circle,#fff,var(--yellow),var(--orange));transform:translate(-50%,-50%);box-shadow:0 0 20px var(--yellow),0 0 40px var(--orange);animation:dotpulse 1s ease-in-out infinite alternate}
@keyframes dotpulse{0%{transform:translate(-50%,-50%) scale(1)}100%{transform:translate(-50%,-50%) scale(1.3)}}
.hero-title{font-family:'Bangers',cursive;font-size:clamp(2.5rem,8vw,5.5rem);letter-spacing:.1em;line-height:1;margin-bottom:.5rem;background:linear-gradient(135deg,#fff,var(--yellow) 30%,var(--orange) 60%,var(--red));-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 20px #ff6a0088);animation:titlepulse 3s ease-in-out infinite}
@keyframes titlepulse{0%,100%{filter:drop-shadow(0 0 20px #ff6a0088)}50%{filter:drop-shadow(0 0 40px #ffd70088) drop-shadow(0 0 60px #ff6a0066)}}
.hero-subtitle{font-family:'Bangers',cursive;font-size:1.1rem;letter-spacing:.3em;color:var(--orange);margin-bottom:2rem;opacity:.8}
.power-display{display:inline-block;background:rgba(0,0,0,.7);border:2px solid var(--orange);padding:.75rem 2.5rem;border-radius:4px;margin-bottom:2rem;box-shadow:0 0 30px #ff6a0044;position:relative;overflow:hidden}
.power-display::before{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,215,0,.05),transparent);animation:scanline 2s linear infinite}
@keyframes scanline{0%{transform:translateX(-100%)}100%{transform:translateX(100%)}}
.power-label{font-size:.7rem;color:#c8a878;letter-spacing:.3em;margin-bottom:.25rem;font-weight:700;text-transform:uppercase}
.power-number{font-family:'Bangers',cursive;font-size:2.5rem;color:var(--yellow);letter-spacing:.1em}
.stats-bar{display:flex;justify-content:center;max-width:700px;margin:0 auto 2rem;border:1px solid rgba(255,106,0,.3);background:rgba(0,0,0,.5);border-radius:4px;overflow:hidden}
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
.hints-section{margin-top:1.5rem;border-top:1px solid rgba(255,106,0,.2);padding-top:1rem}
.hints-title{font-size:.75rem;color:#c8a878;letter-spacing:.2em;margin-bottom:.75rem;font-weight:700;text-transform:uppercase}
.hint-item{background:rgba(255,106,0,.05);border:1px solid rgba(255,106,0,.2);border-radius:2px;padding:.75rem;margin-bottom:.5rem;font-size:.85rem}
.hint-locked{display:flex;justify-content:space-between;align-items:center}
.hint-cost{color:#ff6666;font-size:.75rem;font-weight:700}
.hint-text{color:#c8a878;line-height:1.6}
.hint-unlock-btn{padding:.35rem .75rem;font-family:'Bangers',cursive;font-size:.85rem;border:1px solid var(--red);background:transparent;color:var(--red);cursor:pointer;border-radius:2px;transition:all .2s;letter-spacing:.1em}
.hint-unlock-btn:hover{background:rgba(255,26,26,.1);box-shadow:0 0 10px rgba(255,26,26,.3)}
.live-feed{max-height:400px;overflow-y:auto}
.feed-item{padding:.6rem 0;border-bottom:1px solid rgba(255,106,0,.1);font-size:.88rem;display:flex;gap:.75rem;align-items:center;flex-wrap:wrap;transition:background .2s}
.feed-item:hover{background:rgba(255,106,0,.05);padding-left:.5rem}
.feed-time{color:#806040;flex-shrink:0;font-family:'Share Tech Mono',monospace;font-size:.8rem}
.feed-team{color:var(--yellow);font-weight:700}
.feed-pts{color:var(--orange);margin-left:auto;font-family:'Bangers',cursive;font-size:1.1rem}
.graph-container{background:rgba(0,0,0,.5);border:1px solid rgba(255,106,0,.2);border-radius:4px;padding:1.5rem;margin-bottom:2rem}
.graph-title{font-family:'Bangers',cursive;font-size:1.1rem;color:var(--orange);letter-spacing:.2em;margin-bottom:1rem}
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
.dragonballs{display:flex;justify-content:center;gap:.75rem;margin:1rem auto}
.dball{width:18px;height:18px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#fff8e0,var(--yellow) 40%,var(--orange) 80%,#8b4500);box-shadow:0 0 8px rgba(255,215,0,.5);transition:transform .2s;cursor:default}
.dball:hover{transform:scale(1.3);box-shadow:0 0 15px rgba(255,215,0,.8)}
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:2rem}
::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:#0a0500}::-webkit-scrollbar-thumb{background:var(--orange);border-radius:3px}
.scouter-scan{position:fixed;inset:0;pointer-events:none;z-index:3;background:linear-gradient(0deg,transparent 48%,rgba(0,255,0,.02) 50%,transparent 52%);animation:scouterscan 5s linear infinite}
@keyframes scouterscan{0%{transform:translateY(-100%)}100%{transform:translateY(100%)}}
.ki-particle{position:fixed;pointer-events:none;z-index:9999;border-radius:50%;background:radial-gradient(circle,#fff,var(--yellow),var(--orange));animation:kiblast .6s ease-out forwards}
@keyframes kiblast{0%{transform:scale(0);opacity:1}50%{opacity:.8}100%{transform:scale(3);opacity:0}}
@keyframes kicharge{0%{box-shadow:0 0 5px var(--orange)}50%{box-shadow:0 0 30px var(--yellow),0 0 60px var(--orange)}100%{box-shadow:0 0 5px var(--orange)}}
.ki-charging{animation:kicharge 1s ease-in-out infinite}
""" + PIXEL_ART_CSS

TIMER_JS = """
function updateTimer(){
  const start=new Date("{{ start_time }}").getTime(),end=new Date("{{ end_time }}").getTime(),now=new Date().getTime();
  const te=document.getElementById('timer'),tl=document.getElementById('timer-label');
  if(!te)return;
  if(!start||isNaN(start)){te.textContent='OPEN';return}
  if(now<start){tl.textContent='BATTLE BEGINS IN';te.textContent=fmt(start-now);}
  else if(now<end){const d=end-now;tl.textContent='POWER REMAINING';te.textContent=fmt(d);te.style.color=d<3600000?'var(--red)':'var(--yellow)';}
  else{tl.textContent='BATTLE OVER';te.textContent='00:00:00';te.style.color='var(--red)';}
}
function fmt(ms){const h=Math.floor(ms/3600000),m=Math.floor(ms%3600000/60000),s=Math.floor(ms%60000/1000);return`${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;}
updateTimer();setInterval(updateTimer,1000);
"""

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Login - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + """
.login-wrapper{min-height:100vh;display:flex;align-items:center;justify-content:center;position:relative;z-index:10}
</style></head><body>
""" + DBZ_INTRO + """
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
      <div class="dragonballs"><div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div></div>
    </div>
    <div class="card">
      <h2>⚡ WARRIOR LOGIN</h2>
      <div class="form-group"><label>TEAM NAME</label><input type="text" id="team" placeholder="Enter your warrior name"/></div>
      <div class="form-group"><label>PASSWORD</label>
        <div class="pw-wrap"><input type="password" id="password" placeholder="••••••••"/>
          <button class="pw-toggle" onclick="togglePw('password','eye1')" type="button"><span id="eye1">👁</span></button></div></div>
      <button class="btn btn-full btn-ki" id="login-btn" onclick="doLogin()">⚡ POWER UP & LOGIN</button>
      <div class="text-center"><a href="/register" class="link">No account? Join the battle →</a></div>
    </div>
  </div>
</div>
<script>
function togglePw(i,e){const inp=document.getElementById(i),eye=document.getElementById(e);inp.type=inp.type==='password'?'text':'password';eye.textContent=inp.type==='password'?'👁':'🙈'}
function spawnKi(x,y){const p=document.createElement('div');p.className='ki-particle';const s=10+Math.random()*15;p.style.cssText=`left:${x-s/2}px;top:${y-s/2}px;width:${s}px;height:${s}px`;document.body.appendChild(p);setTimeout(()=>p.remove(),600)}
document.addEventListener('click',e=>{if(e.target.closest&&e.target.closest('#characters-layer'))return;spawnKi(e.clientX,e.clientY)});
async function doLogin(){
  const team=document.getElementById('team').value.trim(),password=document.getElementById('password').value;
  document.querySelectorAll('.alert').forEach(m=>m.remove());
  if(!team||!password)return showAlert('⚠ Fill in all fields!','error');
  const btn=document.getElementById('login-btn');
  btn.textContent='⚡ CHARGING KI...';btn.disabled=true;btn.classList.add('ki-charging');
  try{
    const r=await fetch('/api/v1/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({team_name:team,password})});
    const data=await r.json();
    if(data.success){
      localStorage.setItem('ctf_token',data.token);localStorage.setItem('ctf_team',data.team);localStorage.setItem('ctf_is_admin',data.is_admin?'true':'false');
      showAlert('🐉 POWER LEVEL MAXIMUM!','success');
      setTimeout(()=>window.location.href=data.is_admin?'/admin':'/',1000);
    }else{showAlert('💀 '+(data.message||'Login failed'),'error');btn.textContent='⚡ POWER UP & LOGIN';btn.disabled=false;btn.classList.remove('ki-charging')}
  }catch(e){showAlert('⚠ Network error','error');btn.textContent='⚡ POWER UP & LOGIN';btn.disabled=false;btn.classList.remove('ki-charging')}
}
function showAlert(msg,type){document.querySelector('.card').insertAdjacentHTML('afterbegin',`<div class="alert alert-${type}">${msg}</div>`)}
document.addEventListener('keydown',e=>{if(e.key==='Enter')doLogin()});
</script>
<script>""" + PIXEL_CHARS_JS + """</script>
</body></html>"""

REGISTER_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Register - {{ ctf_name }}</title>
<style>""" + BASE_STYLE + """</style></head><body>
""" + DBZ_INTRO + """
<div id="characters-layer"></div>
<div class="scouter-scan"></div>
<header class="header">
  <a class="logo" href="/">{{ ctf_name }}<span> CTF</span></a>
  <nav><a href="/login">LOGIN</a><a href="/register" class="active">REGISTER</a></nav>
</header>
<div style="display:flex;align-items:center;justify-content:center;min-height:calc(100vh - 80px);position:relative;z-index:10">
  <div class="container" style="margin:2rem auto;width:100%">
    <div style="text-align:center;margin-bottom:1rem">
      <div class="dragonballs"><div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div></div>
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
      <button class="btn btn-full btn-ki" id="reg-btn" onclick="doRegister()">🐉 SUMMON THE DRAGON</button>
      <div class="text-center"><a href="/login" class="link">Already a warrior? Login →</a></div>
    </div>
  </div>
</div>
<script>
function togglePw(i,e){const inp=document.getElementById(i),eye=document.getElementById(e);inp.type=inp.type==='password'?'text':'password';eye.textContent=inp.type==='password'?'👁':'🙈'}
function spawnKi(x,y){const p=document.createElement('div');p.className='ki-particle';const s=10+Math.random()*15;p.style.cssText=`left:${x-s/2}px;top:${y-s/2}px;width:${s}px;height:${s}px`;document.body.appendChild(p);setTimeout(()=>p.remove(),600)}
document.addEventListener('click',e=>{if(e.target.closest&&e.target.closest('#characters-layer'))return;spawnKi(e.clientX,e.clientY)});
async function doRegister(){
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
    if(data.success)setTimeout(()=>window.location.href='/login',2500);
    else{btn.textContent='🐉 SUMMON THE DRAGON';btn.disabled=false;btn.classList.remove('ki-charging')}
  }catch(e){showAlert('⚠ Network error','error');btn.textContent='🐉 SUMMON THE DRAGON';btn.disabled=false;btn.classList.remove('ki-charging')}
}
function showAlert(msg,type){document.querySelector('.card').insertAdjacentHTML('afterbegin',`<div class="alert alert-${type}">${msg}</div>`)}
document.addEventListener('keydown',e=>{if(e.key==='Enter')doRegister()});
</script>
<script>""" + PIXEL_CHARS_JS + """</script>
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
<script>""" + PIXEL_CHARS_JS + """</script>
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
    <table><thead><tr><th>WARRIOR</th><th>EMAIL</th><th>ORIGIN</th><th>POWER</th><th>VICTORIES</th><th>STATUS</th><th>ACTIONS</th></tr></thead><tbody id="teams-body"></tbody></table>
  </div>
  <div class="panel" id="panel-challenges">
    <div class="section-title">🐉 CHALLENGES</div>
    <table><thead><tr><th>NAME</th><th>CATEGORY</th><th>POWER</th><th>DIFFICULTY</th><th>SOLVED</th><th>HINTS</th></tr></thead><tbody id="challenges-body"></tbody></table>
  </div>
  <div class="panel" id="panel-solves">
    <div class="section-title">⚡ BATTLE LOG</div>
    <table><thead><tr><th>TIME</th><th>WARRIOR</th><th>CHALLENGE</th><th>POWER</th><th>FIRST BLOOD</th></tr></thead><tbody id="solves-body"></tbody></table>
  </div>
</div>
<script>
const token=localStorage.getItem('ctf_token'),isAdmin=localStorage.getItem('ctf_is_admin')==='true';
if(!token||!isAdmin)window.location.href='/login';
let allTeams=[];
async function api(path,opts={}){const h={'Content-Type':'application/json','Authorization':`Bearer ${token}`};const r=await fetch('/api/v1'+path,{headers:h,...opts});if(r.status===401||r.status===403){window.location.href='/login';return{}}return r.json()}
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
async function banTeam(n){if(!confirm(`Ban "${n}"?`))return;await api('/admin/teams/ban',{method:'POST',body:JSON.stringify({team_name:n})});loadStats()}
async function unbanTeam(n){if(!confirm(`Unban "${n}"?`))return;await api('/admin/teams/unban',{method:'POST',body:JSON.stringify({team_name:n})});loadStats()}
async function resetScore(n){if(!confirm(`Reset score for "${n}"?`))return;await api('/admin/teams/reset',{method:'POST',body:JSON.stringify({team_name:n})});loadStats()}
async function deleteTeam(n){if(!confirm(`DELETE "${n}"?`))return;await api('/admin/teams/delete',{method:'POST',body:JSON.stringify({team_name:n})});loadStats()}
function switchTab(n){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));document.getElementById('tab-'+n).classList.add('active');document.getElementById('panel-'+n).classList.add('active')}
function logout(){fetch('/api/v1/auth/logout',{method:'POST',headers:{'Authorization':`Bearer ${token}`}});localStorage.clear();window.location.href='/login'}
loadStats();setInterval(loadStats,30000);
</script>
<script>""" + PIXEL_CHARS_JS + """</script>
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
</head><body>
""" + DBZ_INTRO + """
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
  <div class="dragonballs"><div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div><div class="dball"></div></div>
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
    <div class="challenges-grid" id="challenges-grid"><div style="color:#806040;padding:2rem;font-family:'Bangers',cursive;font-size:1.2rem">⚡ LOADING...</div></div>
  </div>
  <div class="panel" id="panel-scoreboard">
    <div class="section-title">🏆 POWER RANKINGS</div>
    <div class="graph-container"><div class="graph-title">⚡ POWER LEVEL PROGRESSION</div><canvas id="scoreGraph" height="120"></canvas></div>
    <table><thead><tr><th>RANK</th><th>WARRIOR</th><th>POWER LEVEL</th><th>VICTORIES</th><th>LAST BATTLE</th><th></th></tr></thead><tbody id="scoreboard-body"></tbody></table>
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
async function api(path,opts={}){const h={'Content-Type':'application/json'};if(token)h['Authorization']=`Bearer ${token}`;return(await fetch('/api/v1'+path,{headers:h,...opts})).json()}
async function loadChallenges(){
  const data=await api('/challenges'),myData=token?await api('/me/solves'):{solves:[]};
  const mySolves=new Set((myData.solves||[]).map(s=>s.challenge_id));
  const grid=document.getElementById('challenges-grid'),prompt=document.getElementById('login-prompt-box');
  if(!token)prompt.innerHTML=`<div class="login-prompt"><p>⚡ Login to submit flags and compete!</p><a href="/login">⚡ LOGIN</a><a href="/register">🐉 REGISTER</a></div>`;
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
  const data=await api('/feed');const feed=document.getElementById('live-feed');
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
async function unlockHint(cid,hi,cost){if(!token)return window.location.href='/login';if(!confirm(`Sacrifice ${cost} power level for this hint?`))return;const r=await api('/hints/unlock',{method:'POST',body:JSON.stringify({challenge_id:cid,hint_index:hi})});if(r.success)await loadHints(currentChallenge);else alert(r.message||'Failed')}
function closeModal(){document.getElementById('modal').classList.remove('active');currentChallenge=null}
async function submitFlag(){
  if(!currentChallenge)return;
  const flag=document.getElementById('flag-input').value.trim();if(!flag)return;
  const btn=document.querySelector('#modal .btn-ki');btn.textContent='⚡ CHARGING...';btn.disabled=true;
  const r=await fetch('/api/v1/submit',{method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`},body:JSON.stringify({challenge_id:currentChallenge.id,flag,team})});
  const data=await r.json();btn.textContent='⚡ RELEASE KI BLAST';btn.disabled=false;
  const msg=document.getElementById('result-msg');msg.style.display='block';
  msg.className='result-msg '+(data.correct?'correct':'wrong');
  msg.textContent=data.correct?'🐉 CHALLENGE CONQUERED! POWER LEVEL RISING!':'💀 '+data.message;
  if(data.correct){for(let i=0;i<20;i++)setTimeout(()=>spawnKi(Math.random()*window.innerWidth,Math.random()*window.innerHeight),i*60);setTimeout(()=>{closeModal();loadChallenges();loadScoreboard();loadFeed()},2000)}
}
function getCertificate(teamName,rank){window.open(`/certificate/${teamName}?rank=${rank}`,'_blank')}
function switchTab(name){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));document.getElementById('tab-'+name).classList.add('active');document.getElementById('panel-'+name).classList.add('active');if(name==='scoreboard')loadScoreboard();if(name==='feed')loadFeed()}
function logout(){fetch('/api/v1/auth/logout',{method:'POST',headers:{'Authorization':`Bearer ${token}`}});localStorage.clear();window.location.href='/login'}
document.getElementById('flag-input')?.addEventListener('keydown',e=>{if(e.key==='Enter')submitFlag()});
document.getElementById('modal')?.addEventListener('click',e=>{if(e.target===document.getElementById('modal'))closeModal()});
loadChallenges();loadFeed();setInterval(()=>{loadScoreboard();loadFeed()},30000);
</script>
<script>""" + TIMER_JS + """</script>
<script>""" + PIXEL_CHARS_JS + """</script>
</body></html>"""

CERT_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Certificate - {{ team }}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Rajdhani:wght@400;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{background:radial-gradient(ellipse at center,#1a0800,#0a0300 60%,#050100);display:flex;align-items:center;justify-content:center;min-height:100vh;padding:2rem;font-family:'Rajdhani',sans-serif}
.cert{background:linear-gradient(135deg,rgba(25,12,0,.98),rgba(10,5,0,.99));border:3px solid #ff6a00;border-radius:8px;padding:4rem;max-width:800px;width:100%;text-align:center;position:relative;box-shadow:0 0 80px rgba(255,106,0,.3),0 0 160px rgba(255,106,0,.1)}
.cert::before{content:'';position:absolute;inset:10px;border:1px solid rgba(255,215,0,.2);border-radius:4px;pointer-events:none}
.corner{position:absolute;width:24px;height:24px;border-color:#ffd700;border-style:solid}
.corner-tl{top:18px;left:18px;border-width:3px 0 0 3px}.corner-tr{top:18px;right:18px;border-width:3px 3px 0 0}
.corner-bl{bottom:18px;left:18px;border-width:0 0 3px 3px}.corner-br{bottom:18px;right:18px;border-width:0 3px 3px 0}
.cert-title{font-family:'Bangers',cursive;font-size:3rem;background:linear-gradient(135deg,#fff,#ffd700,#ff6a00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.5rem;letter-spacing:.1em}
.cert-subtitle{color:rgba(255,215,0,.7);font-size:.9rem;letter-spacing:.3em;margin-bottom:3rem;font-weight:700}
.cert-name{font-family:'Bangers',cursive;font-size:2.5rem;color:#fff;margin:1rem 0;padding:.75rem 2rem;border:2px solid rgba(255,215,0,.5);display:inline-block;background:rgba(255,215,0,.05);border-radius:4px;letter-spacing:.1em}
.cert-rank{font-family:'Bangers',cursive;font-size:3.5rem;color:#ffd700;margin:1rem 0}
.cert-details{display:flex;justify-content:center;gap:3rem;margin:2rem 0;padding:1.5rem;border-top:1px solid rgba(255,106,0,.3);border-bottom:1px solid rgba(255,106,0,.3)}
.cert-detail-value{font-family:'Bangers',cursive;font-size:1.8rem;color:#ffd700}
.cert-detail-label{font-size:.7rem;color:#806040;letter-spacing:.15em;margin-top:.25rem;font-weight:700;text-transform:uppercase}
.print-btn{margin-top:2rem;padding:.75rem 2rem;background:transparent;border:2px solid #ff6a00;color:#ffd700;font-family:'Bangers',cursive;font-size:1rem;cursor:pointer;border-radius:2px;letter-spacing:.15em}
.dball{width:20px;height:20px;border-radius:50%;display:inline-block;background:radial-gradient(circle at 35% 35%,#fff8e0,#ffd700 40%,#ff6a00 80%,#8b4500);box-shadow:0 0 10px rgba(255,215,0,.5)}
@media print{.print-btn{display:none}}
</style></head><body>
<div class="cert">
  <div class="corner corner-tl"></div><div class="corner corner-tr"></div>
  <div class="corner corner-bl"></div><div class="corner corner-br"></div>
  <div style="margin-bottom:1rem"><div class="dball"></div> <div class="dball"></div> <div class="dball"></div> <div class="dball"></div> <div class="dball"></div> <div class="dball"></div> <div class="dball"></div></div>
  <div class="cert-title">CERTIFICATE</div>
  <div class="cert-subtitle">⚡ Of Warrior Achievement ⚡</div>
  <div style="color:#a08060;margin-bottom:.75rem">This certifies that the mighty warrior</div>
  <div class="cert-name">{{ team }}</div>
  <div style="color:#a08060;margin:.75rem 0">has proven their power in</div>
  <div style="color:#ff6a00;font-size:1.2rem;font-family:'Bangers',cursive;letter-spacing:.1em">{{ ctf_name }}</div>
  <div class="cert-rank">{{ rank_emoji }} RANK #{{ rank }}</div>
  <div class="cert-details">
    <div><div class="cert-detail-value">{{ score }}</div><div class="cert-detail-label">⚡ Power Level</div></div>
    <div><div class="cert-detail-value">{{ solves }}</div><div class="cert-detail-label">⚔ Victories</div></div>
    <div><div class="cert-detail-value">{{ rank }}</div><div class="cert-detail-label">🏆 Final Rank</div></div>
  </div>
  <div style="color:#5a3a20;font-size:.75rem;letter-spacing:.1em">🐉 {{ ctf_name }} — {{ date }} 🐉</div>
  <div style="color:#3a2010;font-size:.65rem;margin-top:.5rem">Certificate ID: {{ cert_id }}</div>
  <button class="print-btn" onclick="window.print()">🖨️ CLAIM YOUR SCROLL</button>
</div></body></html>"""


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


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))