from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Comment:
    _id: Optional[str] = None
    author: str = ""
    content: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            "_id": self._id,
            "author": self.author,
            "content": self.content,
            "created_at": self.created_at,
        }

@dataclass
class Issue:
    _id: Optional[str] = None
    title: str = ""
    description: str = ""
    status: str = "open"
    priority: str = "medium"
    assigned_to: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    comments: list[Comment] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    
    @staticmethod
    def from_dict(d):
        d['_id'] = str(d['_id'])
        comments_data = d.get('comments', [])
        comments = [Comment(**c) for c in comments_data]
        d['comments'] = comments
        d['attachments'] = d.get('attachments', [])
        return Issue(**d)

    def to_dict(self):
        d = {
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at,
            "comments": [c.__dict__ for c in self.comments],
            "attachments": self.attachments
        }
        if self._id:
            d['_id'] = self._id
        return d