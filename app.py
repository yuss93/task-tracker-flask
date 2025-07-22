from flask import Flask, render_template, request, redirect, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'
#-----LOGIN SETUP------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # to force login
#user class flask to login
class User(UserMixin):
    def __init__(self, id_, username, password_hash):
        self.id = id_
        self.username = username
        self.password_hash = password_hash
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
# user loader callback for flask-login
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("SELECT id, username, password_hash FROM users WHERE id = ?",(user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1], user[2])
    return None

# Create database table if not exists
def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        status TEXT NOT NULL,
        username TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()
    
    
#-----signup--------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?",(username,))
        if c.fetchone():
            flash('Username already exists')
            conn.close()
            return redirect('/signup')
        password_hash = generate_password_hash(password)
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",(username, password_hash))
        conn.commit()
        conn.close()
        flash('Account created! please log in.')
        return redirect('/login')
    return render_template('signup.html')
    
#---------login-----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj)
            flash('Logged in successfully!')
            return redirect('/')
        else:
            flash('Invalid username or password')
    return render_template('login.html')
#--------logout--------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('you have been logged out.')
    return render_template('logout.html')

#-------HOME/TASKS-------
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    init_db()
    
    name = current_user.username
    #Greeting based on time
    hour = datetime.datetime.now().hour
    if hour <12:
        greeting = "Good morning"
    elif hour <18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    name = current_user.username
    message = f"{greeting}, {name}! What would you like to do today?"
    #handle tasks
    if request.method == 'POST':
        title = request.form['title'].strip()
        status = request.form['status']
        if not title:
            flash('Task title cannot be empty')
            return redirect('/')
        username = current_user.username # to get current user
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("INSERT INTO tasks (title, status, username) VALUES (?, ?, ?)", (title, status, username))
        conn.commit()
        conn.close()
        return redirect('/')
#show all task
    username = current_user.username
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE username = ?",(username,))
    tasks = c.fetchall()
    conn.close()
    # calculate completion
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task[2]=="Complete")
    if total_tasks > 0:
        percent_complete = int((completed_tasks/total_tasks)*100)
    else:
        percent_complete = 0
# set color for completetion
    if percent_complete < 40:
        color_class = "red"
    elif percent_complete < 80:
        color_class = "orange"
    else:
        color_class = "green"
    
    return render_template('index.html', tasks=tasks, message=message, percent_complete=percent_complete, color_class=color_class)

#----DELETE--------
@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ? AND username = ?", (task_id, current_user.username))
    conn.commit()
    conn.close()
    return redirect('/')
# change status from complete/incomplete and vice-versa
@app.route('/toggle/<int:task_id>')
@login_required
def toggle_status(task_id):
    init_db()  # Ensure table exists
    conn = sqlite3.connect('tasks.db')  # ✅ FIXED filename
    c = conn.cursor()
    
    # Get current status
    c.execute("SELECT status FROM tasks WHERE id = ? AND username = ?", (task_id, current_user.username))
    row = c.fetchone()

    if row is None:
        conn.close()
        return "Task not found", 404

    current_status = row[0]

    # Toggle status
    new_status = "Incomplete" if current_status == "Complete" else "Complete"
    c.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    
    conn.commit()
    conn.close()
    return redirect('/')

# adding reset/logout session
@app.route('/reset', methods=['POST'])
@login_required
def reset():
    logout_user()           # Log user out
    session.clear()         # Clear session
    flash('You have been logged out.')
    return render_template('logout.html')  # Show the nice logout page

#---- edit tasks--------
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()

    if request.method == 'POST':
        new_title = request.form['title'].strip()
        new_status = request.form['status']
        
        if not new_title:
            flash('Task title cannot be empty.')
            return redirect(f'/edit/{task_id}')
        
        c.execute("UPDATE tasks SET title = ?, status = ? WHERE id = ?", (new_title, new_status, task_id))
        conn.commit()
        conn.close()
        flash('Task updated successfully!')
        return redirect('/')
    
    # GET: show form
    c.execute("SELECT * FROM tasks WHERE id = ? AND username = ?", (task_id, current_user.username))
    task = c.fetchone()
    conn.close()

    if not task:
        return "Task not found", 404
    
    return render_template('edit.html', task=task)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
