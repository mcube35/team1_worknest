from flask import Flask, render_template, request, redirect, url_for, abort
from bson.objectid import ObjectId
from pymongo import MongoClient
import datetime
from markupsafe import Markup, escape


app = Flask(__name__)

def nl2br(value):
    # 줄바꿈(\n)을 <br> 태그로 바꾸고 안전하게 마크업 처리
    return Markup('<br>'.join(escape(value).split('\n')))

app.jinja_env.filters['nl2br'] = nl2br


# MongoDB 클라이언트 연결 (자신 환경에 맞게 URI 변경)
client = MongoClient('mongodb://localhost:27017/')
db = client.community_db
posts_collection = db.posts

# 메인 - 게시글 목록
@app.route('/')
def index():
    posts = list(posts_collection.find().sort('createdAt', -1))
    return render_template('index.html', posts=posts)

# 글쓰기 페이지
@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = request.form.get('author')

        if not title or not content or not author:
            return "모든 필드를 입력하세요.", 400

        post = {
            'title': title,
            'content': content,
            'author': author,
            'createdAt': datetime.datetime.utcnow(),
            'updatedAt': None,
            'comments': []
        }
        posts_collection.insert_one(post)
        return redirect(url_for('index'))

    return render_template('write.html')

# 게시글 상세 페이지 + 댓글 표시
@app.route('/post/<post_id>', methods=['GET', 'POST'])
def detail(post_id):
    post = posts_collection.find_one({'_id': ObjectId(post_id)})
    if not post:
        abort(404)

    if request.method == 'POST':
        # 댓글 작성 처리
        comment_author = request.form.get('comment_author')
        comment_content = request.form.get('comment_content')

        if not comment_author or not comment_content:
            return "댓글 작성자와 내용을 입력하세요.", 400

        comment = {
            'author': comment_author,
            'content': comment_content,
            'createdAt': datetime.datetime.utcnow()
        }
        posts_collection.update_one(
            {'_id': ObjectId(post_id)},
            {'$push': {'comments': comment}}
        )
        return redirect(url_for('detail', post_id=post_id))

    return render_template('detail.html', post=post)

# 게시글 수정 페이지
@app.route('/edit/<post_id>', methods=['GET', 'POST'])
def edit(post_id):
    post = posts_collection.find_one({'_id': ObjectId(post_id)})
    if not post:
        abort(404)

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title or not content:
            return "제목과 내용을 입력하세요.", 400

        posts_collection.update_one(
            {'_id': ObjectId(post_id)},
            {'$set': {
                'title': title,
                'content': content,
                'updatedAt': datetime.datetime.utcnow()
            }}
        )
        return redirect(url_for('detail', post_id=post_id))

    return render_template('write.html', post=post)

# 게시글 삭제
@app.route('/delete/<post_id>', methods=['POST'])
def delete(post_id):
    result = posts_collection.delete_one({'_id': ObjectId(post_id)})
    if result.deleted_count == 0:
        abort(404)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
