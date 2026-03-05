# 🐉 Dragon Ball Z — Capture The Flag Platform

> *"It's over 9000!!"* — A fully-featured cybersecurity CTF competition platform with a Dragon Ball Z theme, pixel art characters, esports team system, and animated intro sequence.

---

## ✨ Features

### 🎮 Platform Core
- **11 Challenges** across 7 categories (Web, Crypto, Forensics, Reverse, Pwn, OSINT, Misc)
- **Dynamic scoring** — points visible per challenge
- **Flag submission** with rate limiting and brute-force protection
- **Hint system** — unlock hints by spending points (configurable cost per hint)
- **Live scoreboard** with Chart.js score progression graph
- **Live battle feed** — real-time solve events with first blood tracking
- **Competition timer** — countdown to start/end, auto-updates
- **Certificate generator** — downloadable PDF-style cert per team rank

### 👥 Esports Team System *(NEW)*
- **Team registration** — captain creates a team with name, tag, color, avatar, and motto
- **Invite codes** — 8-character code for members to join (up to 5 per team)
- **Team roles** — Captain + up to 4 Members
- **Pixel avatar selector** — choose from Goku, Vegeta, Piccolo, Gohan, Frieza
- **Team aura color picker** — custom color shows on scoreboard and characters
- **Team cards** on scoreboard — esports-style card with avatar, tag, roster, power level

### 🔐 Authentication
- Email + password registration
- Email verification via Gmail SMTP
- Session tokens (Bearer auth)
- Login brute-force protection
- Password show/hide toggle
- Admin account with protected panel

### 🛡️ Admin Panel
- View all warriors (teams), verify/ban/unban/delete/reset
- Challenge overview with solve counts
- Full battle log
- Live stats (teams, challenges, solves, verified count)
- Search/filter teams

### 🎨 Dragon Ball Z Theme
- Orange/gold/dark color palette with Bangers + Rajdhani fonts
- Animated background — star drift, energy scan lines, scouter effect
- Dragon Radar with 7 Dragon Balls on homepage
- Ki blast particles on every click
- Power level displays and animated counters
- Screen shake, speed lines, shockwave rings

### 🕹️ Pixel Art Characters
- **5 fully animated pixel sprites** — Goku, Vegeta, Piccolo, Gohan, Frieza
- **Goku SSJ transformation** — golden hair, enhanced aura (random trigger)
- Autonomous AI state machine: walk, run, idle, jump, fight, float, powerup
- Per-character speech bubbles with DBZ quotes
- Ki blast system — characters fire at each other with arc physics
- Explosion particles and aura glow effects
- Click a character to make them jump and speak
- Character name tags with matching aura color

### 🎬 Intro Animation (plays once per session)
- **Phase 1 — Energy Charge**: power level counter (0→530,000), aura pillar, shockwave rings, lightning bolts, pixel Goku silhouette, "AAAAHHHHH!!!" scream, scouter "IT'S OVER 9000!!"
- **Phase 2 — Title Card**: speed lines, 7 dragon balls drop with bounce, CTF name slams in, loading bar, screen shake
- **Phase 3 — Character Parade**: each of 5 characters shown with animated pixel sprite, name, and signature quote
- **Enter button** or auto-dismiss after 4 seconds
- Skip button works at any time
- Session storage prevents repeat on refresh

---

## 🚀 Deployment

### Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + Flask |
| Database | PostgreSQL (production) / SQLite (dev) |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Hosting | Render.com |
| Email | Gmail SMTP |
| Charts | Chart.js 4.4 + Moment.js |

### Environment Variables
Create a `.env` file (or set in Render dashboard):

```env
# Core
CTF_NAME=Your CTF Name
CTF_DESCRIPTION=Your description
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:pass@host/dbname

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-admin-password
ADMIN_EMAIL=admin@yourdomain.com

# Email verification
MAIL_USERNAME=youremail@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_FROM=youremail@gmail.com

# Competition timing (ISO 8601)
START_TIME=2025-01-01T00:00:00
END_TIME=2025-01-02T00:00:00
```

### Gmail App Password Setup
1. Go to [Google Account](https://myaccount.google.com) → Security
2. Enable 2-Factor Authentication
3. Search "App Passwords" → Generate one for "Mail"
4. Use that 16-character password as `MAIL_PASSWORD`

### Run Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Seed challenges
python seed.py

# Start server
python web/app.py
# or
gunicorn web.app:app
```

### Deploy to Render
```bash
git add .
git commit -m "deploy"
git push
```
Render auto-deploys on push. Make sure `Procfile` contains:
```
web: gunicorn web.app:app
```

---

## 📁 Project Structure

```
ctf-platform/
├── web/
│   └── app.py              # Main Flask app (all HTML/CSS/JS embedded)
├── ctf_core/
│   ├── config.py           # Config loader (env vars)
│   ├── auth.py             # Registration, login, sessions, teams
│   ├── challenge_manager.py # Challenge CRUD
│   ├── flag_validator.py   # Flag checking + submission tracking
│   └── scoreboard.py       # Rankings, timelines, feed
├── challenges/             # Challenge definitions (YAML/JSON)
├── seed.py                 # Database seeder
├── requirements.txt
├── Procfile
└── README.md
```

---

## 🎮 How It Works

### For Participants
1. **Register** — Create a team account (captain) or join with an invite code
2. **Pick your warrior** — Choose a pixel avatar and team aura color
3. **Browse challenges** — Organized by category and difficulty
4. **Submit flags** — Format: `CTF{...}`
5. **Use hints** — Spend power level (points) to unlock hints
6. **Climb the ranks** — Scoreboard updates live with power level graph
7. **Earn a certificate** — Download your rank certificate at the end

### For Admins
1. Login with admin credentials → redirected to `/admin`
2. Manage teams — ban, unban, reset, delete
3. Monitor solves and battle feed
4. View all challenges and solve statistics

---

## 🏆 Scoring

| Action | Effect |
|--------|--------|
| Solve a challenge | +points (as configured per challenge) |
| Unlock a hint | −10% of challenge points per hint |
| First blood | 🩸 Badge in battle feed |

---

## 🕹️ Characters & Avatars

| Character | Aura Color | Style |
|-----------|-----------|-------|
| 🟡 Goku | Gold `#ffd700` | Orange gi, black hair (SSJ: golden) |
| 🟣 Vegeta | Purple `#8800ff` | White Saiyan armor, widow peak |
| 🟢 Piccolo | Green `#00aa44` | Purple gi, white cape, antennae |
| 🟡 Gohan | Gold `#ffd700` | Purple gi, yellow belt |
| 🟣 Frieza | Violet `#cc44ff` | White/purple armor, floats |

---

## 🛠️ Adding Challenges

Create a YAML file in `challenges/`:

```yaml
id: web-001
name: "Dragon Ball Web"
category: Web
difficulty: easy
points: 100
description: "Find the hidden flag on the server."
flag: "CTF{dr4g0n_b4ll_w3b}"
hints:
  - "Check the page source"
  - "Look at HTTP headers"
files: []
```

Then run:
```bash
python seed.py
```

---

## 📸 Pages

| Route | Description |
|-------|-------------|
| `/` | Main arena — challenges, scoreboard, feed |
| `/login` | Warrior login |
| `/register` | Team registration (esports style) |
| `/admin` | Admin command center |
| `/certificate/<team>` | Rank certificate |
| `/verify/<token>` | Email verification |

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | — | Register team |
| POST | `/api/v1/auth/login` | — | Login |
| POST | `/api/v1/auth/logout` | ✓ | Logout |
| GET | `/api/v1/challenges` | — | List challenges |
| POST | `/api/v1/submit` | ✓ | Submit flag |
| GET | `/api/v1/scoreboard` | — | Top teams |
| GET | `/api/v1/scoreboard/timeline` | — | Score graph data |
| GET | `/api/v1/feed` | — | Live battle feed |
| GET | `/api/v1/hints/<id>` | ✓ | Get unlocked hints |
| POST | `/api/v1/hints/unlock` | ✓ | Unlock a hint |
| GET | `/api/v1/me` | ✓ | My team info |
| GET | `/api/v1/me/solves` | ✓ | My solved challenges |
| POST | `/api/v1/teams/join` | ✓ | Join team with invite code |
| GET | `/api/v1/admin/teams` | Admin | All teams |
| POST | `/api/v1/admin/teams/ban` | Admin | Ban a team |
| POST | `/api/v1/admin/teams/unban` | Admin | Unban a team |
| POST | `/api/v1/admin/teams/reset` | Admin | Reset team score |
| POST | `/api/v1/admin/teams/delete` | Admin | Delete a team |

---

## 📦 Requirements

```
flask
python-dotenv
psycopg2-binary
bcrypt
pyjwt
gunicorn
```

---

## 🐉 Credits

Built with 🔥 using Flask, PostgreSQL, Chart.js, and pure canvas pixel art.  
Dragon Ball Z characters and names are property of Akira Toriyama / Toei Animation.  
This platform is for educational/competition use only.

---

*"The Saiyan Prince does not lose. Neither will your team."* — Vegeta, probably