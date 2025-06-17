from dataclasses import dataclass
from datetime import date

@dataclass
class Task:
    id: int
    title: str
    description: str
    assignee: str
    team: str
    status: str  # 예: '진행중', '완료', '보류'
    due_date: date