from pydantic import BaseModel
from typing import List, Optional

class ChatQuery(BaseModel):
    query: str

class Employee(BaseModel):
    id: int
    name: str
    skills: List[str]
    experience_years: int
    projects: List[str]
    availability: str
    notes: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    retrieved_employees: List[Employee]