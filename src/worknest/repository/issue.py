from bson import ObjectId
from models.issue import Issue

class IssueRepository:
    def __init__(self, collection):
        self.collection = collection

    def insert(self, issue):
        result = self.collection.insert_one(issue.to_dict())
        return result.inserted_id

    def find_by_id(self, issue_id):
        doc = self.collection.find_one({"_id": ObjectId(issue_id)})
        if doc:
            return Issue.from_dict(doc)
        return None
    
    def find(self, query):
        results = self.collection.find(query)
        return [
            Issue.from_dict({**r, "_id": str(r["_id"])}) for r in results
        ]


