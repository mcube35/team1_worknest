from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.utils import secure_filename
import time
import io
import gridfs
import mimetypes
from datetime import datetime

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["worknest"]
tasks_collection = db["tasks"]
comments_collection = db["comments"]
created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# GridFS 인스턴스 생성
fs = gridfs.GridFS(db)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

STATUS_ORDER = {'진행중': 0, '대기': 1, '완료': 2}

@app.route('/')
def dashboard():
    tasks = list(tasks_collection.find())
    for task in tasks:
        task['_id'] = str(task['_id'])
        if 'file_id' in task and task['file_id']:
            task['file_id'] = str(task['file_id'])
        # created_at 문자열을 datetime 객체로 변환
        if 'created_at' in task and isinstance(task['created_at'], str):
            try:
                task['created_at'] = datetime.strptime(task['created_at'], '%Y-%m-%d %H:%M:%S')
            except:
                task['created_at'] = datetime.min
        else:
            task['created_at'] = task.get('created_at', datetime.min)

    # 상태 우선 + 생성일 최신순 정렬
    tasks.sort(key=lambda x: (
        STATUS_ORDER.get(x.get('status', ''), 99),
        -x.get('created_at', datetime.min).timestamp()
    ))
    return render_template('dashboard.html', tasks=tasks)

@app.route('/projects')
def project_list():
    search = request.args.get('search', '').strip()
    task_type = request.args.get('type', '').strip()  # 업무유형 파라미터 추가
    query = {}

    filters = []
    if search:
        filters.append({
            "$or": [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"assigned_to": {"$regex": search, "$options": "i"}}
            ]
        })

    if task_type in ['개발', '디자인', '기획', '테스트']:
        filters.append({"type": task_type})

    if filters:
        if len(filters) == 1:
            query = filters[0]
        else:
            query = {"$and": filters}

    tasks = list(tasks_collection.find(query))
    for task in tasks:
        task['_id'] = str(task['_id'])
        if 'file_ids' in task and task['file_ids']:
            task['file_ids'] = [str(fid) for fid in task['file_ids']]
        if 'created_at' in task and isinstance(task['created_at'], str):
            try:
                task['created_at'] = datetime.strptime(task['created_at'], '%Y-%m-%d %H:%M:%S')
            except:
                task['created_at'] = datetime.min
        else:
            task['created_at'] = task.get('created_at', datetime.min)

    tasks.sort(key=lambda x: (
        STATUS_ORDER.get(x.get('status', ''), 99),
        -x.get('created_at', datetime.min).timestamp()
    ))

    task_types = ['개발', '디자인', '기획', '테스트']  # 고정 업무유형 리스트

    return render_template('project_list.html', tasks=tasks, search=search, task_type=task_type, task_types=task_types)

@app.route('/projects/<id>')
def project_detail(id):
    try:
        task = tasks_collection.find_one({"_id": ObjectId(id)})
    except:
        return "Invalid ID", 400
    if not task:
        return "Task not found", 404
    
    task['_id'] = str(task['_id'])
    if 'file_id' in task and task['file_id']:
        task['file_id'] = str(task['file_id'])

    # 댓글 목록 불러오기 (최신순)
    comments_cursor = comments_collection.find({"task_id": ObjectId(id)}).sort("created_at", -1)
    comments = []
    for c in comments_cursor:
        c['_id'] = str(c['_id'])
        comments.append(c)

    return render_template('project_detail.html', task=task, comments=comments)

@app.route('/projects/new', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        files = request.files.getlist('file')
        file_ids = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_id = fs.put(file, filename=filename)
                file_ids.append(file_id)

        task = {
            "title": request.form['title'],
            "description": request.form['description'],
            "type": request.form['type'],
            "status": request.form['status'],
            "assigned_to": request.form['assigned_to'],
            "deadline": request.form['deadline'],
            "progress": int(request.form['progress']),
            "file_ids": file_ids,  # GridFS 파일 ObjectId
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        tasks_collection.insert_one(task)
        return redirect(url_for('project_list'))

    return render_template('create_task.html')

@app.route('/file/<file_id>')
def serve_file(file_id):
    try:
        grid_out = fs.get(ObjectId(file_id))
        return Response(
            grid_out.read(),
            mimetype='application/octet-stream',
            headers={"Content-Disposition": f"attachment; filename={grid_out.filename}"}
        )
    except Exception:
        return "File not found", 404

@app.route('/projects/<id>/edit', methods=['GET', 'POST'])
def edit_task(id):
    task = tasks_collection.find_one({"_id": ObjectId(id)})
    if not task:
        return "Task not found", 404

    if request.method == 'POST':
        # 1) 기존 file_ids 리스트를 ObjectId 타입으로 변환
        file_ids = [ObjectId(fid) if isinstance(fid, str) else fid for fid in task.get('file_ids', [])]

        # 2) 삭제 요청된 파일 ID 문자열 리스트 받기
        delete_ids_str = request.form.getlist('delete_files')
        for fid_str in delete_ids_str:
            try:
                fid = ObjectId(fid_str)
                fs.delete(fid)  # GridFS에서 삭제
                if fid in file_ids:
                    file_ids.remove(fid)  # 리스트에서 제거
            except Exception:
                pass  # 삭제 실패해도 무시

        # 3) 새로 업로드된 파일들 추가
        files = request.files.getlist('file')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_id = fs.put(file, filename=filename)
                file_ids.append(file_id)

        updated_task = {
            "title": request.form['title'],
            "description": request.form['description'],
            "type": request.form['type'],
            "status": request.form['status'],
            "assigned_to": request.form['assigned_to'],
            "deadline": request.form['deadline'],
            "progress": int(request.form['progress']),
            "file_ids": file_ids
        }

        tasks_collection.update_one({"_id": ObjectId(id)}, {"$set": updated_task})
        return redirect(url_for('project_detail', id=id))

    # GET 요청 시 문자열 변환 후 렌더링
    # GET 요청 시 문자열 변환 후 렌더링
    task['_id'] = str(task['_id'])

    # file_ids → [{id: ..., filename: ...}, ...] 형태로 가공
    file_infos = []
    for fid_str in task.get('file_ids', []):
        try:
            fid = ObjectId(fid_str)
            grid_file = fs.get(fid)
            file_infos.append({
                "id": str(fid),
                "filename": grid_file.filename
            })
        except:
            continue  # 파일이 없을 경우 건너뜀

    return render_template('edit_task.html', task=task, file_infos=file_infos)

@app.route('/projects/<id>/delete', methods=['POST'])
def delete_task(id):
    try:
        task = tasks_collection.find_one({"_id": ObjectId(id)})
        if not task:
            return "Task not found", 404

        # GridFS 파일 삭제
        file_id = task.get("file_id")
        if file_id:
            try:
                fs.delete(ObjectId(file_id))
            except Exception:
                pass

        # MongoDB에서 업무 문서 삭제
        tasks_collection.delete_one({"_id": ObjectId(id)})
    except:
        return "Invalid ID", 400

    return redirect(url_for('project_list'))

# 댓글 작성
@app.route('/projects/<task_id>/comments', methods=['POST'])
def add_comment(task_id):
    content = request.form.get('content')
    author = request.form.get('author')  # 로그인 구현 안 하면 폼에서 받기

    if not content or not author:
        return "내용과 작성자 필요", 400

    comment = {
        "task_id": ObjectId(task_id),
        "author": author,
        "content": content,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    result = comments_collection.insert_one(comment)
    return redirect(url_for('project_detail', id=task_id))


# 댓글 수정
@app.route('/comments/<comment_id>/edit', methods=['POST'])
def edit_comment(comment_id):
    new_content = request.form.get('content')
    if not new_content:
        return "내용 필요", 400

    comments_collection.update_one(
        {"_id": ObjectId(comment_id)},
        {"$set": {"content": new_content, "updated_at": datetime.now()}}
    )
    # 댓글이 달린 task_id를 찾아서 상세 페이지로 리다이렉트
    comment = comments_collection.find_one({"_id": ObjectId(comment_id)})
    if comment:
        return redirect(url_for('project_detail', id=str(comment['task_id'])))
    else:
        return "댓글이 존재하지 않습니다.", 404


# 댓글 삭제
@app.route('/comments/<comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    comment = comments_collection.find_one({"_id": ObjectId(comment_id)})
    if not comment:
        return "댓글이 존재하지 않습니다.", 404

    comments_collection.delete_one({"_id": ObjectId(comment_id)})
    return redirect(url_for('project_detail', id=str(comment['task_id'])))

if __name__ == '__main__':
    app.run(debug=True)