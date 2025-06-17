from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('project_manager.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template('dashboard.html', tasks=tasks)

@app.route('/projects')
def project_list():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template('project_list.html', tasks=tasks)

@app.route('/projects/<int:task_id>')
def project_detail(task_id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    conn.close()
    return render_template('project_detail.html', task=task)

@app.route('/projects/new', methods=('GET', 'POST'))
def create_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        assigned_to = request.form['assigned_to']

        conn = get_db_connection()
        conn.execute('INSERT INTO tasks (title, description, status, assigned_to, created_at) VALUES (?, ?, ?, ?, ?)',
                     (title, description, status, assigned_to, datetime.now()))
        conn.commit()
        conn.close()

        return redirect(url_for('project_list'))

    return render_template('create_task.html')

if __name__ == '__main__':
    app.run(debug=True)
