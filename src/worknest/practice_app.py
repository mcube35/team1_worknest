from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
contact_logs = db["contact_logs"]
employees = db["employees"]

# 공통 유틸 함수
def determine_status(reply, manual_status):
    return '답변완료' if reply else (manual_status or '진행중')

# 상담 목록
@app.route('/cs/list')
def cs_list():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')
    page = int(request.args.get('page', 1))
    per_page = 10
    skip = (page - 1) * per_page

    query = {}
    if search:
        query["$or"] = [
            {"client_name": {"$regex": search, "$options": "i"}},
            {"writer": {"$regex": search, "$options": "i"}}
        ]
    if status_filter != 'all':
        query["status"] = status_filter

    contacts = list(contact_logs.find(query).sort("created_at", -1).skip(skip).limit(per_page))
    total_count = contact_logs.count_documents(query)
    message = request.args.get('message')

    return render_template('cs_main.html', 
                        contacts=contacts, 
                        search=search, 
                        status_filter=status_filter,
                        page=page, 
                        total_count=total_count, 
                        message=message)

# 상담 등록
@app.route('/cs/add', methods=['GET', 'POST'])
def cs_new():
    if request.method == 'POST':
        new_contact = {
            "client_name": request.form['client_name'],
            "category": request.form['category'],
            "contents": request.form['contents'],
            "action_required": request.form['action_required'],
            "status": request.form['status'],
            "writer": request.form['writer'],
            "email": request.form['email'],
            "company": request.form['company'],
            "address": request.form['address'],
            "city": request.form['city'],
            "state_country": request.form['state_country'],
            "phone": request.form['phone'],
            "position": request.form['position'],
            "job": request.form['job'],
            "industry": request.form['industry'],
            "created_at": datetime.utcnow()
        }
        contact_logs.insert_one(new_contact)
        return redirect(url_for('cs_list', message='등록완료'))
    return render_template('cs_add.html')

# 상담 상세 보기
@app.route('/cs/detail/<contact_id>')
def cs_detail(contact_id):
    contact = contact_logs.find_one({"_id": ObjectId(contact_id)})
    if not contact:
        return "상담 정보를 찾을 수 없습니다.", 404
    return render_template('cs_detail_view.html', contact=contact)

# 상담 수정 및 삭제
@app.route('/cs/update/<contact_id>', methods=['GET', 'POST'])
def cs_update(contact_id):
    contact = contact_logs.find_one({"_id": ObjectId(contact_id)})
    if not contact:
        return "상담 정보를 찾을 수 없습니다.", 404

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            contact_logs.delete_one({"_id": ObjectId(contact_id)})
            return redirect(url_for('cs_list', message="삭제되었습니다."))

        updated_status = request.form.get('status')
        updated_contents = request.form.get('contents')
        updated_reply = request.form.get('reply')

        update_fields = {
            'status': determine_status(updated_reply, updated_status),
            'contents': updated_contents,
            'reply': updated_reply
        }
        update_fields = {k: v for k, v in update_fields.items() if v}

        if update_fields:
            contact_logs.update_one({"_id": ObjectId(contact_id)}, {"$set": update_fields})
        return redirect(url_for('cs_list', message="수정되었습니다."))

    return render_template('cs_update.html', contact=contact)

# 인사 등록
@app.route('/hr/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        try:
            hire_date = datetime.strptime(request.form.get('hire_date', ''), "%Y-%m-%d")
        except ValueError:
            hire_date = None
        try:
            retire_date = datetime.strptime(request.form.get('retire_date', ''), "%Y-%m-%d")
        except ValueError:
            retire_date = None

        new_emp = {
            "name": request.form['name'],
            "department": request.form['department'],
            "position": request.form['position'],
            "email": request.form['email'],
            "phone": request.form['phone'],
            "hire_date": hire_date,
            "retire_date": retire_date,
            "employment_type": request.form['employment_type']
        }
        employees.insert_one(new_emp)
        return redirect(url_for('add_employee', message='등록완료'))
    return render_template('hr_add.html')

# 인사 목록
@app.route('/hr/list')
def employee_list():
    search = request.args.get('search', '').strip()
    department = request.args.get('department', '')
    position = request.args.get('position', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')

    page = int(request.args.get('page', 1))
    per_page = 10
    skip = (page - 1) * per_page

    # 🔍 검색 조건 구성
    query = {}

    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]

    if department:
        query["department"] = department

    if position:
        query["position"] = position

    if from_date or to_date:
        date_filter = {}
        if from_date:
            date_filter["$gte"] = datetime.strptime(from_date, '%Y-%m-%d')
        if to_date:
            date_filter["$lte"] = datetime.strptime(to_date, '%Y-%m-%d')
        query["hire_date"] = date_filter

    total_count = employees.count_documents(query)
    employee_data = list(employees.find(query).sort("hire_date", -1).skip(skip).limit(per_page))

    for emp in employee_data:
        emp['hire_date_str'] = emp.get('hire_date').strftime('%Y-%m-%d') if isinstance(emp.get('hire_date'), datetime) else '-'
        emp['retire_date_str'] = emp.get('retire_date').strftime('%Y-%m-%d') if isinstance(emp.get('retire_date'), datetime) else '-'

    return render_template('hr_list.html',
                        employees=employee_data,
                        page=page,
                        total_count=total_count,
                        search=search,
                        department=department,
                        position=position,
                        from_date=from_date,
                        to_date=to_date)

# 인사 수정
@app.route('/hr/edit/<emp_id>', methods=['GET', 'POST'])
def edit_employee(emp_id):
    emp = employees.find_one({"_id": ObjectId(emp_id)})
    if not emp:
        return "직원을 찾을 수 없습니다.", 404

    if request.method == 'POST':
        try:
            hire_date = datetime.strptime(request.form.get('hire_date', ''), "%Y-%m-%d")
        except ValueError:
            hire_date = None
        try:
            retire_date = datetime.strptime(request.form.get('retire_date', ''), "%Y-%m-%d")
        except ValueError:
            retire_date = None

        update_data = {
            "name": request.form['name'],
            "department": request.form['department'],
            "position": request.form['position'],
            "email": request.form['email'],
            "phone": request.form['phone'],
            "employment_type": request.form['employment_type'],
            "hire_date": hire_date,
            "retire_date": retire_date
        }
        employees.update_one({"_id": ObjectId(emp_id)}, {"$set": update_data})
        return redirect(url_for('employee_list', message='수정완료'))

    emp['hire_date_str'] = emp.get('hire_date').strftime('%Y-%m-%d') if isinstance(emp.get('hire_date'), datetime) else ''
    emp['retire_date_str'] = emp.get('retire_date').strftime('%Y-%m-%d') if isinstance(emp.get('retire_date'), datetime) else ''

    return render_template('hr_edit.html', emp=emp)

if __name__ == '__main__':
    app.run(debug=True)
