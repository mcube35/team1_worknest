from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

# DB 초기화 함수
def init_db():
    with sqlite3.connect("tasks.db") as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                assignee TEXT,
                team TEXT,
                status TEXT,
                due_date TEXT
            )
        ''')
        conn.commit()

@app.route('/')
def all_tasks():
    with sqlite3.connect("tasks.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks")
        tasks = cur.fetchall()
    return render_template("tasks.html", tasks=tasks, title="전체 업무현황")

@app.route('/team/<team_name>')
def team_tasks(team_name):
    with sqlite3.connect("tasks.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE team=?", (team_name,))
        tasks = cur.fetchall()
    return render_template("tasks.html", tasks=tasks, title=f"{team_name}팀 업무현황")

@app.route('/add', methods=['POST'])
def add_task():
    data = (
        request.form['title'],
        request.form['description'],
        request.form['assignee'],
        request.form['team'],
        request.form['status'],
        request.form['due_date']
    )
    with sqlite3.connect("tasks.db") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title, description, assignee, team, status, due_date) VALUES (?, ?, ?, ?, ?, ?)", data)
        conn.commit()
    return "업무가 등록되었습니다. <a href='/'>뒤로가기</a>"

@app.route('/form')
def form():
    return '''
    <h2>업무 추가</h2>
    <form method="post" action="/add">
        제목: <input type="text" name="title"><br>
        설명: <input type="text" name="description"><br>
        담당자: <input type="text" name="assignee"><br>
        팀: <input type="text" name="team"><br>
        상태: 
        <select name="status">
            <option>진행중</option>
            <option>완료</option>
            <option>보류</option>
        </select><br>
        마감일: <input type="date" name="due_date"><br>
        <button type="submit">등록</button>
    </form>
    '''

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
