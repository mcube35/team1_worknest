from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client['mydatabase']
inquiries_collection = db['inquiries']
useinquiries_collection = db['useinquiries']

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/inquiries')
def inquiries():
    inquiries = list(inquiries_collection.find())
    return render_template('inquiries.html', inquiries=inquiries)

@app.route('/inquiries_list', methods=['GET', 'POST'])
def inquiries_list():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        print(f"POST 받은 데이터 - 제목: {title}, 내용: {content}")  # 데이터 제대로 받았는지 확인용
        
        # MongoDB에 저장
        result = inquiries_collection.insert_one({
            'title': title,
            'content': content
        })
        
        print(f"저장된 문서 ID: {result.inserted_id}")  # 저장 성공 여부 확인용

        return redirect(url_for('inquiries_list'))

    else:
        inquiries = list(inquiries_collection.find())
        for inquiry in inquiries:
            inquiry['id'] = str(inquiry['_id'])
        return render_template('inquiries_list.html', inquiries_list=inquiries)


@app.route('/inquiry/<inquiry_id>')
def inquiry_detail(inquiry_id):
    try:
        # ObjectId로 변환해서 MongoDB에서 하나만 조회
        inquiry = inquiries_collection.find_one({'_id': ObjectId(inquiry_id)})
        if inquiry:
            inquiry['id'] = str(inquiry['_id'])  # id를 문자열로 변환
            return render_template('inquiry_detail.html', inquiry=inquiry)
        else:
            return "해당 문의를 찾을 수 없습니다.", 404
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}", 500

@app.route('/useinquiries')
def useinquiries():
    useinquiries = list(useinquiries_collection.find())
    return render_template('useinquiries.html', useinquiries=useinquiries)

@app.route('/useinquiries_list', methods=['GET', 'POST'])
def useinquiries_list():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        # ✅ MongoDB 저장
        useinquiries_collection.insert_one({
            'title': title,
            'content': content
        })

        return redirect(url_for('useinquiries_list'))
    else:
        useinquiries = list(useinquiries_collection.find())
        return render_template('useinquiries_list.html', useinquiries_list=useinquiries)

if __name__ == '__main__':
    app.run(debug=True)
