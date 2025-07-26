# 🧠 AI‑Generated Project Management Tool

A minimal, fully prompt‑engineered project management web application built entirely using AI‑generated code through prompt engineering.

---

## 🚀 Key Features

- **Authentication & Authorization**  
  Role-based access (Admin, Manager, Team Member) via AI‑generated auth flows.

- **Project & Task Boards**  
  Kanban‑style interface with drag‑and‑drop columns and detailed task views.

- **Notifications**  
  In‑app alerts for task assignments and upcoming due dates.

- **Progress Dashboard**  
  Visual analytics (charts, task breakdowns, status tracking).

- **File Attachments & Comments**  
  Upload files to tasks and support threaded comments for team collaboration.

---

## 🧩 Project Overview

All logic, functionality, and UI were created through prompt engineering. Prompts were delivered to an AI model to scaffold the entire application, including backend APIs, frontend components, and deployment setup.

---

## 📝 Prompt Log & Development History

You can review the full prompt log and associated AI responses in:

➡️ **`prompt_log.md`** — contains every prompt you used and the AI-generated code or actions in response.

➡️ **`/images`** — contains all screenshots that document the implementation process, which are referenced in the prompt log.

---

## ⚙️ Running the Application Locally

```bash
git clone https://github.com/9sreerag7/eweb.git
cd eweb

# Install dependencies
cd backend/
npm install      # or pip install -r requirements.txt
cd ../frontend/
npm install

# Run servers
cd ../backend && npm run dev     # or python app.py
# In another terminal:
cd frontend && npm start
