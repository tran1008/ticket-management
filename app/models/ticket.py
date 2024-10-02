from typing import List, Optional
from pydantic import BaseModel, Field


class ChangeSchema(BaseModel):
    change_from: str
    change_key: str
    change_to: str
    blame: str
    action_date: str  # ISO-UTC formatted stri


# không định nghĩa webhook bằng các đường dẫn cụ thể trên URL mà chỉ đơn giản là đăng ký sự kiên trên webhook
class TicketSchema(BaseModel):
    ticket_id: str
    issue_type: str = Field(..., pattern="^(ABC|XYZ|GHIK)$")
    status: str = Field(..., pattern="^(Resolved|Late|Waiting for approve)$")
    assignee: str
    created_date: str  # ISO-UTC format
    duedate: Optional[str]  # ISO-UTC format
    point: int
    is_deleted: bool


class UpdateTicketSchema(BaseModel):
    issue_type: Optional[str]
    status: Optional[str]
    assignee: Optional[str]
    created_date: Optional[str]
    duedate: Optional[str]
    point: Optional[int]
    is_deleted: Optional[bool]
    change: Optional[List[ChangeSchema]]


# Patch schema similar to update, but for partial updates
class PatchTicketSchema(BaseModel):
    issue_type: Optional[str]
    status: Optional[str]
    assignee: Optional[str]
    duedate: Optional[str]
    point: Optional[int]
    is_deleted: Optional[bool]
    change: Optional[List[ChangeSchema]]
