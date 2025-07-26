# 🧠 AI-Built Project Management Tool

A minimal, fully prompt-engineered project management web application built using only AI-generated code. Designed as an experimental build task to showcase the power of conversational coding and prompt-driven development.

---

## 🚀 Features

✅ **Authentication & Authorization**  
- Sign-up / Sign-in with JWT-based auth  
- Role-based access control (Admin, Manager, Team Member)

✅ **Project & Task Boards**  
- Kanban-style project dashboard  
- Task creation, updates, and status changes  
- Drag-and-drop column UI  
- Individual task detail views

✅ **Notifications**  
- In-app alerts for task assignments  
- Alerts for upcoming deadlines

✅ **Progress Dashboard**  
- Visual analytics (charts, graphs) for project/task tracking  
- Task completion and status breakdown

✅ **File Attachment & Comments**  
- Upload documents/images to tasks  
- Threaded comments for team collaboration

---

## ⚙️ Tech Stack

- **Frontend:** React.js, Tailwind CSS  
- **Backend:** Node.js / Express or Flask (AI-chosen)  
- **Database:** MongoDB / PostgreSQL (based on prompts)  
- **Auth:** JWT, Role-based Middleware  
- **Charts:** Chart.js / Recharts  
- **File Handling:** Multer / Base64 encoding

> 📌 All code was generated through prompt engineering using AI, not handwritten manually.

---

## 🧪 How to Run

```bash
# Clone the repository
git clone https://github.com/9sreerag7/eweb.git
cd eweb

# Install backend & frontend dependencies
cd backend
npm install         # or pip install -r requirements.txt

cd ../frontend
npm install

# Start development servers
# Backend
npm run dev         # or python app.py

# Frontend (in a separate terminal)
npm start

