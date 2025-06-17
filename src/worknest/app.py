from flask import Flask
from flask_pymongo import PyMongo
from repository.issue import IssueRepository
from routes.issue_routes import *

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/issue_db"

mongo = PyMongo(app)
repo = IssueRepository(mongo.db.issues)

init_issue_repo(repo)
app.register_blueprint(issue_bp)

if __name__ == "__main__":
    for rule in app.url_map.iter_rules():
        print(rule)
    
    app.run(debug=True)
