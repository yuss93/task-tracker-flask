# 📝 Task Tracker Flask App

A lightweight, personal task manager built with Flask, SQLite, and Flask-Login. Users can securely register, log in, and manage their own to-do list. Tasks are stored per user, with real-time status updates and progress tracking.

---

## 🚀 Features

- ✅ User registration and secure login (passwords hashed with Werkzeug)
- 🔐 Per-user task isolation — each user sees only their tasks
- 📋 Add, complete, toggle, delete, and edit tasks
- 📈 Progress bar showing % of completed tasks
- 🎨 Clean, styled UI with dynamic feedback
- 🔓 Logout and session reset functionality
- 🧠 Personalized greeting based on the current time

---

## 🛠️ Tech Stack

| Tech            | Purpose                       |
|-----------------|-------------------------------|
| **Flask**       | Web framework                 |
| **SQLite**      | Lightweight embedded database |
| **Flask-Login** | User authentication/session   |
| **Werkzeug**    | Password hashing              |
| **HTML + CSS**  | Frontend templates & styling  |
| **Jinja2**      | Template rendering engine     |

---

## 🧭 How It Works

1. User signs up with a unique username and password.
2. After logging in, the user is greeted and redirected to their task dashboard.
3. Tasks can be added, marked as complete/incomplete, edited, or deleted.
4. The task list is user-specific and stored in a shared SQLite database.
5. The progress bar dynamically shows the percentage of completed tasks.
6. User can log out or reset their session at any time.

---

## 🧪 Local Setup

Clone the repository and run the app locally:

```bash
git clone https://github.com/yuss93/task-tracker-flask.git
cd task-tracker-flask
pip install -r requirements.txt
python app.py
