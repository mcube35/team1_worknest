from flask import Flask, render_template, request, redirect
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017/')
db = client['community_db']
collection = db['clients']

# 고객사 등록 폼 페이지
@app.route('/')
def form():
    return render_template('register.html')

# 고객사 등록 처리
@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    contact = request.form.get('contact')
    email = request.form.get('email')

    if name:
        collection.insert_one({
            'name': name,
            'contact': contact,
            'email': email
        })
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
