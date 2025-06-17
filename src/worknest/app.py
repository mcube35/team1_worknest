from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017/')
db = client['task_db']
users = db['users']
tasks = db['tasks']

# Flask-Login 설정
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# 사용자 클래스
class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc['_id'])
        self.username = user_doc['username']

@login_manager.user_loader
def load_user(user_id):
    user_doc = users.find_one({'_id': ObjectId(user_id)})
    return User(user_doc) if user_doc else None

# 메인 화면
@app.route('/')
def home():
    return render_template('home.html')

# 회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.find_one({'username': username}):
            return '이미 존재하는 사용자입니다.'
        users.insert_one({'username': username, 'password': password})
        return redirect(url_for('login'))
    return render_template('register.html')

# 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = users.find_one({'username': request.form['username']})
        if user and user['password'] == request.form['password']:
            login_user(User(user))
            return redirect(url_for('dashboard'))
        return '로그인 실패'
    return render_template('login.html')

# 로그아웃
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# 대시보드
@app.route('/dashboard')
@login_required
def dashboard():
    query = {}
    team = request.args.get('team')
    status = request.args.get('status')
    date = request.args.get('date')

    if team:
        query['team'] = team
    if status:
        query['status'] = status
    if date:
        query['date'] = date

    all_tasks = tasks.find(query).sort('date', -1)
    return render_template('dashboard.html', tasks=all_tasks)

# 업무 추가
@app.route('/add', methods=['POST'])
@login_required
def add_task():
    task = {
        'title': request.form['title'],
        'team': request.form['team'],
        'status': request.form['status'],
        'date': request.form['date'],
        'created_by': current_user.username,
        'created_at': datetime.now()
    }
    tasks.insert_one(task)
    return redirect(url_for('dashboard'))

# 업무 수정
@app.route('/edit/<task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = tasks.find_one({'_id': ObjectId(task_id)})
    if request.method == 'POST':
        tasks.update_one({'_id': ObjectId(task_id)}, {
            '$set': {
                'title': request.form['title'],
                'team': request.form['team'],
                'status': request.form['status'],
                'date': request.form['date']
            }
        })
        return redirect(url_for('dashboard'))
    return render_template('edit_task.html', task=task)

# 업무 삭제
@app.route('/delete/<task_id>')
@login_required
def delete_task(task_id):
    tasks.delete_one({'_id': ObjectId(task_id)})
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)