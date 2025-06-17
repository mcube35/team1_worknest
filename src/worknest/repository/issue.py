from bson import ObjectId
from models.issue import Comment, Issue

class IssueRepository:
    def __init__(self, collection):
        self.collection = collection

    def insert(self, issue):
        result = self.collection.insert_one(issue.to_dict())
        return result.inserted_id

    def add_comment(self, id, comment: Comment):
        result = self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$push": {"comments": comment.to_dict()}}
        )
        return result.modified_count > 0
    
    def find_by_id(self, id):
        doc = self.collection.find_one({"_id": ObjectId(id)})
        if doc:
            return Issue.from_dict(doc)
        return None
    
    def find(self, query):
        results = self.collection.find(query)
        return [
            Issue.from_dict({**r, "_id": str(r["_id"])}) for r in results
        ]
        
    def update(self, id, data: dict):
        result = self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )
        return result.modified_count > 0
    
    def update_attachments(self, id, new_attachments: list[str]):
        issue = self.find_by_id(id)
        if not issue:
            return False
        updated_attachments = (issue.attachments or []) + new_attachments
        result = self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"attachments": updated_attachments}}
        )
        return result.modified_count > 0
    
    
    def delete(self, id):
        result = self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0



