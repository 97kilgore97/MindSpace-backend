# Calm Connect — Backend Setup Guide

## Project structure

```
Calm_Connect/backend/
├── calmconnect/          ← project config (settings, urls, asgi)
├── core/                 ← shared: permissions, safety, SMS, WebSocket
│   ├── models.py         ← CrisisFlag, SMSLog
│   ├── consumers.py      ← WebSocket chat consumer
│   ├── routing.py        ← WebSocket URL routing
│   ├── middleware.py     ← JWT auth for WebSockets
│   ├── permissions.py    ← IsAdminOrModerator, IsCounselorOrAdmin
│   ├── safety.py         ← keyword detection + crisis escalation
│   ├── sms.py            ← Africa's Talking SMS/USSD
│   └── ussd.py           ← *384# USSD webhook view
├── users/                ← auth, register, anonymous login
├── counselors/           ← profiles, booking, time slots
├── moods/                ← mood logs, journal, summary
├── groups/               ← peer chat rooms, messages, moderation
├── resources/            ← articles and guides
├── requirements.txt
└── .env.example
```

---

## 1. Install dependencies

```bash
cd Calm_Connect/backend
pip install -r requirements.txt
```

---

## 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env and fill in all values
```

Key variables:
| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Long random string |
| `AT_API_KEY` | Africa's Talking API key |
| `AT_USERNAME` | Africa's Talking username (`sandbox` for dev) |
| `CRISIS_COUNSELOR_PHONE` | Phone to receive crisis SMS alerts |
| `REDIS_URL` | Redis URL for WebSocket channel layer |

---

## 3. Run migrations and start

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

For WebSocket support (production), use Daphne:

```bash
daphne -b 0.0.0.0 -p 8000 calmconnect.asgi:application
```

---

## 4. WebSocket connection (frontend)

```javascript
// Connect to a peer chat room
const token = localStorage.getItem('access_token');
const socket = new WebSocket(
  `ws://localhost:8000/ws/chat/<room_id>/?token=${token}`
);

// Send a message
socket.send(JSON.stringify({ type: 'message', content: 'Hello!' }));

// Send typing indicator
socket.send(JSON.stringify({ type: 'typing', is_typing: true }));

// Receive messages
socket.onmessage = (e) => {
  const data = JSON.parse(e.data);
  if (data.type === 'message')  { /* render message */ }
  if (data.type === 'typing')   { /* show typing indicator */ }
  if (data.type === 'presence') { /* user joined/left */ }
  if (data.type === 'flagged')  { /* message held for safety review */ }
};
```

---

## 5. Key API endpoints

### Auth
| Method | URL | Description |
|---|---|---|
| POST | `/api/users/register/` | Create account |
| POST | `/api/users/anonymous/` | Anonymous session |
| POST | `/api/users/login/` | Get JWT tokens |
| POST | `/api/users/logout/` | Blacklist token |
| GET/PATCH | `/api/users/me/` | Own profile |
| POST | `/api/users/token/refresh/` | Refresh access token |

### Counselors
| Method | URL | Description |
|---|---|---|
| GET | `/api/counselors/` | List counselors |
| GET | `/api/counselors/<id>/slots/` | Available slots |
| POST | `/api/counselors/book/` | Book a session |
| GET | `/api/counselors/my-sessions/` | My bookings |
| POST | `/api/counselors/sessions/<id>/cancel/` | Cancel session |

### Moods
| Method | URL | Description |
|---|---|---|
| GET/POST | `/api/moods/` | List / log mood |
| GET | `/api/moods/summary/` | Dashboard summary |
| GET/POST | `/api/moods/journal/` | Journal entries |

### Groups (Peer chat)
| Method | URL | Description |
|---|---|---|
| GET | `/api/groups/` | List rooms |
| POST | `/api/groups/<id>/join/` | Join a room |
| GET/POST | `/api/groups/<id>/messages/` | Messages (REST fallback) |
| GET | `/api/groups/flagged/` | Moderation queue (admin) |

### Resources
| Method | URL | Description |
|---|---|---|
| GET | `/api/resources/` | Published articles |
| GET | `/api/resources/categories/` | Categories |

### USSD
| Method | URL | Description |
|---|---|---|
| POST | `/api/ussd/` | Africa's Talking *384# webhook |

---

## 6. Safety system

Every chat message and journal entry is automatically scanned. Matches trigger:

- **Critical** (suicidal language) → message flagged + on-call counselor receives SMS immediately
- **High** (self-harm) → flagged in moderation queue + counselor SMS
- **Medium** (distress) → flagged for review only

Moderators resolve flags at `/api/groups/flagged/` or via the Django admin.
