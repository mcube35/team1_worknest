from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client.task_manager
tasks = db.tasks
users = db.users

# Login Manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# User model
class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc['_id'])
        self.username = user_doc['username']
        self.role = user_doc.get('role', 'member')

@login_manager.user_loader
def load_user(user_id):
    user_doc = users.find_one({'_id': ObjectId(user_id)})
    return User(user_doc) if user_doc else None

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        if users.find_one({'username': username}):
            flash('이미 존재하는 사용자입니다.')
        else:
            users.insert_one({'username': username, 'password': password, 'role': role})
            flash('회원가입 성공')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = users.find_one({'username': request.form['username']})
        if user and user['password'] == request.form['password']:
            login_user(User(user))
            return redirect(url_for('dashboard'))
        flash('로그인 실패')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    team_filter = request.args.get('team')
    query = {'team': team_filter} if team_filter else {}
    if current_user.role != 'admin':
        query['team'] = current_user.username  # 팀 이름이 유저명과 동일하다고 가정

    task_list = list(tasks.find(query))
    today = datetime.today().date()
    for task in task_list:
        due_date = datetime.strptime(task['date'], '%Y-%m-%d').date()
        task['due_soon'] = (due_date - today).days <= 2
    return render_template('dashboard.html', tasks=task_list, user=current_user)

@app.route('/add', methods=['POST'])
@login_required
def add_task():
    if current_user.role != 'admin':
        flash('권한이 없습니다.')
        return redirect(url_for('dashboard'))
    file = request.files['file']
    filename = secure_filename(file.filename)
    if filename:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
    tasks.insert_one({
        'title': request.form['title'],
        'team': request.form['team'],
        'status': request.form['status'],
        'date': request.form['date'],
        'filename': filename,
        'created_at': datetime.now()
    })
    return redirect(url_for('dashboard'))

@app.route('/edit/<task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = tasks.find_one({'_id': ObjectId(task_id)})
    if request.method == 'POST':
        update = {
            'title': request.form['title'],
            'team': request.form['team'],
            'status': request.form['status'],
            'date': request.form['date']
        }
        tasks.update_one({'_id': ObjectId(task_id)}, {'$set': update})
        return redirect(url_for('dashboard'))
    return render_template('edit_task.html', task=task)

@app.route('/delete/<task_id>')
@login_required
def delete_task(task_id):
    if current_user.role != 'admin':
        flash('권한이 없습니다.')
        return redirect(url_for('dashboard'))
    tasks.delete_one({'_id': ObjectId(task_id)})
    return redirect(url_for('dashboard'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/chart-data')
@login_required
def chart_data():
    pipeline = [{"$group": {"_id": "$team", "count": {"$sum": 1}}}]
    data = list(tasks.aggregate(pipeline))
    return json.dumps({"labels": [d['_id'] for d in data], "counts": [d['count'] for d in data]})

if __name__ == '__main__':
    app.run(debug=True)
