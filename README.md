
# ApplyPulse

Personal job application tracker with a web dashboard and a Chrome extension.

**Live demo:** [https://applypulse.onrender.com](https://applypulse.onrender.com)

---

## What it does

- Save a job from the page you’re viewing (LinkedIn, Indeed, and most career pages)
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
- Manual add when the extension isn’t used
- Basic stats (totals, interview-related metrics, follow-ups)

---

## Local setup

```bash
git clone https://github.com/jawadahmadliaqat-dot/ApplyPulse.git
cd ApplyPulse
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file from `.env.example` and set:

- MongoDB connection string  
- A long random `SECRET_KEY`  
- Auth-related settings as documented in `.env.example`

```bash
uvicorn main:app --reload --port 8000
```

- App: `http://127.0.0.1:8000`  
- API docs: `http://127.0.0.1:8000/docs`  

**Extension:** Chrome → `chrome://extensions` → Developer mode → Load unpacked → select the `extension` folder. Point the extension API URL at your local or production host as needed.

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
- Use strong `SECRET_KEY` in production
- Keep MongoDB network access restricted
- Treat the live demo as a public instance; don’t store sensitive personal data there

---

## Scope (honest)

ApplyPulse helps you track jobs **you choose to save**. It is not a bulk scraper or auto-apply bot.

---

## Author

**Jawad Ahmad**  
GitHub: [jawadahmadliaqat-dot](https://github.com/jawadahmadliaqat-dot)

---

## License

See `LICENSE` in this repository.
```


---

## Animations — **same design**, sirf polish

`index.html` ke existing `<style>` block mein **add** karo (layout mat badlo):

```css
/* Soft page enter */
#app-view, #login-view {
  animation: fadeIn .35s ease both;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: none; }
}

/* Stat cards */
#page-apps .bg-slate-900.border.rounded-xl {
  transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}
#page-apps .bg-slate-900.border.rounded-xl:hover {
  transform: translateY(-2px);
  border-color: #334155;
  box-shadow: 0 8px 24px rgba(0,0,0,.25);
}

/* Table rows */
#job-rows tr {
  transition: background .15s ease;
}

/* Buttons */
button, .nav-item {
  transition: background .2s ease, color .2s ease, transform .15s ease, opacity .2s ease;
}
button:active {
  transform: scale(.98);
}

/* Status badge pulse when Interview */
.status-interview {
  animation: softPulse 2s ease-in-out infinite;
}
@keyframes softPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .75; }
}

/* Kanban cards */
#kanban-board article {
  transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
}
#kanban-board article:hover {
  transform: translateY(-2px);
  border-color: #475569;
}

/* Sidebar nav */
.nav-item:hover {
  transform: translateX(2px);
}
```
