from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId

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
    phone = request.form.get('phone') 
    email = request.form.get('email')

    if name:
        collection.insert_one({
            'name': name,
            'contact': contact,
            'phone': phone, 
            'email': email
        })
    return redirect('/')
# 고객사 목록 조회
@app.route('/customers')
def customer_list():
    customers = list(collection.find())
    return render_template('customer_list.html', customers=customers)

# 고객사 정보 수정
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_customer(id):
    customer = collection.find_one({"_id": ObjectId(id)})
    if request.method == 'POST':
        collection.update_one({"_id": ObjectId(id)}, {
            "$set": {
                "name": request.form['name'],
                "contact": request.form['contact'],
                "phone": request.form['phone'], 
                "email": request.form['email']
            }
        })
        return redirect('/customers')
    return render_template('edit_customer.html', customer=customer)

# 고객사 삭제
@app.route('/delete/<id>')
def delete_customer(id):
    collection.delete_one({"_id": ObjectId(id)})
    return redirect('/customers')

if __name__ == '__main__':
    app.run(debug=True)