
# ApplyPulse

**One-click job tracking for real applications.**

Save any job page (LinkedIn, Indeed, company careers, and more) with a Chrome extension, then manage status, notes, and follow-ups in a clean web dashboard.

🌐 **Live app:** [https://applypulse.onrender.com](https://applypulse.onrender.com)  
📦 **Repo:** [github.com/jawadahmadliaqat-dot/ApplyPulse](https://github.com/jawadahmadliaqat-dot/ApplyPulse)

---

## Why ApplyPulse?

Job hunting spreads across LinkedIn, Indeed, email, and spreadsheets. ApplyPulse keeps **the jobs you actually open** in one place — without bulk scraping or breaking site rules.

```text
Open job page → Extension “Save this job” → Track status in dashboard
```

---

## Features

### Chrome extension
- One-click **Save this job** on almost any job page
- Auto-extracts title, company, location (best-effort)
- Detects source (LinkedIn, Indeed, Glassdoor, etc.)
- Optional quick note before save
- Email / Google login

### Web dashboard
- Auth (email + Google OAuth)
- Application list with search & filters
- Status pipeline: Saved → Applied → Interview → Offer / Rejected…
- **Kanban board** with drag-and-drop status updates
- Stats: totals, interview rate, follow-ups due
- Manual add for jobs without the extension
- Export **CSV**, **JSON**, and **calendar (.ics)** follow-ups

### Backend
- FastAPI + MongoDB Atlas
- JWT auth, per-user data isolation
- Duplicate prevention on `(user_id, job_url)`
- URL normalization (strips tracking params)
- Health endpoint + Render deployment

---

## Tech stack

| Layer | Tech |
|--------|------|
| API | Python, FastAPI, Pydantic, Motor |
| DB | MongoDB Atlas |
| Auth | JWT, bcrypt, Google OAuth |
| Frontend | HTML, Tailwind CSS, vanilla JS |
| Extension | Chrome Manifest V3 |
| Deploy | Render (`render.yaml`) |

---

## Project structure

```text
ApplyPulse/
├── main.py              # FastAPI app, static, health
├── database.py          # Mongo client + indexes
├── models.py            # Pydantic schemas
├── security.py          # JWT + password hashing
├── routes/
│   ├── auth_routes.py
│   └── job_routes.py
├── index.html           # Dashboard UI
├── extension/           # Chrome extension
│   ├── manifest.json
│   ├── popup.html / popup.js
│   ├── content.js
│   └── icons
├── requirements.txt
└── render.yaml
```

---

## Quick start (local)

### 1. Clone & install

```bash
git clone https://github.com/jawadahmadliaqat-dot/ApplyPulse.git
cd ApplyPulse
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment

Copy `.env.example` → `.env`:

```env
MONGO_URI=mongodb+srv://USER:PASS@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=applypulse_db
SECRET_KEY=change-me-to-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 3. Run API + dashboard

```bash
uvicorn main:app --reload --port 8000
```

- App: http://127.0.0.1:8000  
- API docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/api/health  

### 4. Load Chrome extension

1. Open `chrome://extensions`
2. Enable **Developer mode**
3. **Load unpacked** → select the `extension/` folder
4. Login in the popup (same account as the web app)
5. Open a job page → **Save this job**

> For local use, extension `BASE_URL` should be `http://127.0.0.1:8000`.  
> For production, point it to `https://applypulse.onrender.com`.

---

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/signup` | Register |
| `POST` | `/api/auth/login` | Email login → JWT |
| `POST` | `/api/auth/google` | Google token → JWT |
| `GET` | `/api/jobs/` | List current user’s jobs |
| `POST` | `/api/jobs/` | Create job |
| `PATCH` | `/api/jobs/{id}` | Update job / status |
| `DELETE` | `/api/jobs/{id}` | Delete job |
| `GET` | `/api/health` | Health + DB status |

Protected routes require:

```http
Authorization: Bearer <access_token>
```

---

## Screenshots

<!-- Add your own after capture -->
| Dashboard | Extension | Kanban |
|-----------|-----------|--------|
| *Add screenshot* | *Add screenshot* | *Add screenshot* |

---

## What this is (and isn’t)

**Is**
- A practical tracker for jobs **you** open and save
- A full-stack portfolio project (API + UI + extension + deploy)

**Isn’t**
- Bulk auto-scraper of LinkedIn/Indeed
- Auto-apply bot
- Guaranteed perfect field extraction on every career site

Honest limits keep the product reliable and ToS-friendly.

---

## Deployment (Render)

Repo includes `render.yaml`. Typical setup:

1. New Web Service from this repo  
2. Set env vars: `MONGO_URI`, `SECRET_KEY`, …  
3. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`  
4. Health check: `/api/health`

Live: [https://applypulse.onrender.com](https://applypulse.onrender.com)

---

## Roadmap

- [ ] Extension default production API URL + env toggle  
- [ ] Edit job modal (notes, follow-up, resume version)  
- [ ] Email reminders for follow-up dates  
- [ ] Better extraction for Greenhouse / Lever / Workday  
- [ ] Demo GIF in README  

---

## Author

**Jawad Ahmad**  
- GitHub: [jawadahmadliaqat-dot](https://github.com/jawadahmadliaqat-dot)  
- Live: [applypulse.onrender.com](https://applypulse.onrender.com)

---

## License

See [LICENSE](LICENSE) in this repository.
```

---
