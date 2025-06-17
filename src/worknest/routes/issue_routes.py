from flask import Blueprint, abort, request, jsonify, render_template
from models.issue import Issue

issue_bp = Blueprint('issue', __name__, url_prefix='/issue')

repo = None

def init_issue_repo(issue_repo):
    global repo
    repo = issue_repo

@issue_bp.route('/<id>', methods=['GET'])
def view_issue(id):
    print(id)
    try:
        issue_data = repo.find_by_id(id)
    except Exception:
        abort(400, "잘못된 ID 형식입니다.")

    if not issue_data:
        abort(404, "이슈를 찾을 수 없습니다.")

    return render_template('issue/detail.html', issue=issue_data)


@issue_bp.route('/new', methods=['GET'])
def new_issue_form():
    return render_template('issue/form.html')


@issue_bp.route('/', methods=['POST'])
def create_issue():
    data = request.form
    required_fields = ["title", "description", "priority", "assigned_to"]
    for field in required_fields:
        if not data.get(field):
            return "필수 입력 항목이 누락되었습니다."

    issue = Issue(
        title=data.get("title"),
        description=data.get("description"),
        priority=data.get("priority"),
        assigned_to=data.get("assigned_to")
    )
    inserted_id = repo.insert(issue)
    return f"이슈가 생성되었습니다. ID: {inserted_id}"


@issue_bp.route('/', methods=['GET'])
def list_issues():
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    query = {}
    if status:
        query['status'] = status
    if priority:
        query['priority'] = priority
    
    issues = repo.find(query)
    
    return render_template('issue/list.html', issues=issues, selected_status=status, selected_priority=priority)
