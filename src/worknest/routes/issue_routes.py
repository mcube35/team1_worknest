import datetime
import os
from flask import Blueprint, abort, request, jsonify, render_template, redirect, url_for, flash, current_app
from models.issue import Comment, Issue
from werkzeug.utils import secure_filename

issue_bp = Blueprint('issue', __name__, url_prefix='/issue')

repo = None

def init_issue_repo(issue_repo):
    global repo
    repo = issue_repo

@issue_bp.route('/<id>', methods=['GET'])
def view_issue(id):
    issue_data = repo.find_by_id(id)
    return render_template('issue/detail.html', issue=issue_data)


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
    
    return render_template('issue/list.html', issues=issues, current_status=status, current_priority=priority)


@issue_bp.route('/issue', methods=['POST'])
def create_issue():
    data = request.form
    
    filename = None
    file = request.files.get('attachment')
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

    issue = Issue(
        title=data.get("title"),
        description=data.get("description"),
        priority=data.get("priority"),
        assigned_to=data.get("assigned_to"),
        attachments=[filename] if filename else []
    )

    id = repo.insert(issue)
    return redirect(url_for('issue.view_issue', id=id))

@issue_bp.route('/new', methods=['GET'])
def new_issue_form():
    return render_template('issue/form.html')


@issue_bp.route('/<id>/edit', methods=['GET', 'POST'])
def edit_issue(id):
    if request.method == "POST":
        data = request.form
        issue = Issue(
            title=data.get("title"),
            description=data.get("description"),
            priority=data.get("priority"),
            status=data.get("status"),
            assigned_to=data.get("assigned_to")
        )
        updated = repo.update(id, issue.to_dict())
        if updated:
            return redirect(url_for('issue.view_issue', id=id))
        
    issue = repo.find_by_id(id)
    return render_template('issue/edit.html', issue=issue)


@issue_bp.route('/<id>/delete', methods=['POST'])
def delete_issue(id):
    repo.delete(id)
    return redirect(url_for('issue.list_issues'))


@issue_bp.route('/<id>/comment', methods=['POST'])
def add_comment(id):
    author = request.form.get('author')
    content = request.form.get('content')
    if not author or not content:
        return redirect(url_for('issue.view_issue', id=id))
    
    comment = Comment(author=author, content=content)
    repo.add_comment(id, comment)
    return redirect(url_for('issue.view_issue', id=id))