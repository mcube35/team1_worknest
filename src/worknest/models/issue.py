from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Issue:
    _id: Optional[str] = None
    title: str = ""
    description: str = ""
    status: str = "open"
    priority: str = "medium"
    assigned_to: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @staticmethod
    def from_dict(d):
        d['_id'] = str(d['_id'])
        return Issue(**d)

    def to_dict(self):
        d = {
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at
        }
        if self._id:
            d['_id'] = self._id
        return d
