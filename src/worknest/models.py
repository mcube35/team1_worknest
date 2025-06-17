from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ContactLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    contents = db.Column(db.Text)
    action_required = db.Column(db.String(200))
    status = db.Column(db.String(20))
    writer = db.Column(db.String(50))
    email = db.Column(db.String(100))
    company = db.Column(db.String(100))
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state_country = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    position = db.Column(db.String(50))
    job = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    department = db.Column(db.String(50))
    position = db.Column(db.String(50))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    hire_date = db.Column(db.Date)
    employment_type = db.Column(db.String(20))  # 정규직, 계약직 등
