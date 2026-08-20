
# ApplyPulse

Personal job application tracker with a web dashboard and a Chrome extension.

**Live demo:** [https://applypulse.onrender.com](https://applypulse.onrender.com)

---

## What it does

- Save a job from the page you are viewing (LinkedIn, Indeed, and most career pages)
- Track status: Saved → Applied → Interview → Offer / Rejected
- Filter, search, and view applications as a table or board
- Export data (CSV / JSON) and follow-up reminders (calendar)
- Sign in with email or Google

Built as a full-stack portfolio project: API + dashboard + browser extension + cloud deploy.

---

## Stack

| Part | Technology |
|------|------------|
| Backend | Python, FastAPI |
| Database | MongoDB |
| Auth | JWT, password hashing, Google sign-in |
| Frontend | HTML, Tailwind CSS, JavaScript |
| Extension | Chrome Manifest V3 |
| Hosting | Render |

---

## Features

**Extension**
- One-click “Save this job”
- Best-effort title / company / location extraction
- Optional note before save

**Dashboard**
- Login and session handling
- Application list with search and filters
- Status updates and kanban-style board
- Manual add when the extension is not used
- Basic stats (totals, interview-related metrics, follow-ups)

---

## Local setup

```bash
git clone https://github.com/jawadahmadliaqat-dot/ApplyPulse.git
cd ApplyPulse
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```bash
.venv\Scripts\activate
```

Create a `.env` file from `.env.example` and set:

- MongoDB connection string
- A long random `SECRET_KEY`
- Other auth-related values as shown in `.env.example`

```bash
uvicorn main:app --reload --port 8000
```

- App: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`

**Extension:** open `chrome://extensions` → enable Developer mode → Load unpacked → select the `extension` folder. Point the extension API URL at your local or production host as needed.

---

## Project layout

```text
ApplyPulse/
├── main.py
├── database.py
├── models.py
├── security.py
├── routes/
├── index.html
├── extension/
├── requirements.txt
└── render.yaml
```

---

## Security notes

- Never commit `.env` or real credentials
- Use a strong `SECRET_KEY` in production
- Restrict MongoDB network access
- Treat the live demo as a public instance; do not store sensitive personal data there

---

## Scope

ApplyPulse helps you track jobs you choose to save. It is not a bulk scraper or an auto-apply bot.

---

## Author

**Jawad Ahmad**  
GitHub: [jawadahmadliaqat-dot](https://github.com/jawadahmadliaqat-dot)

---

## License

See `LICENSE` in this repository.
```
