from typing import List, Optional
from pydantic import BaseModel, Field


class ChangeSchema(BaseModel):
    change_from: str
    change_key: str
    change_to: str
    blame: str
    action_date: str  # ISO-UTC formatted string


# không định nghĩa webhook bằng các đường dẫn cụ thể trên URL mà chỉ đơn giản là đăng ký sự kiên trên webhook
class TicketSchema(BaseModel):
    ticket_id: str
    issue_type: str = Field(..., pattern="^(ABC|XYZ|GHIK)$")
    status: str = Field(..., pattern="^(Resolved|Late)$")
    assignee: str
    created_date: str  # ISO-UTC format
    duedate: Optional[str]  # ISO-UTC format
    change: List[ChangeSchema]
    point: int
    is_deleted: bool


class UpdateTicketSchema(BaseModel):
    issue_type: Optional[str]
    status: Optional[str]
    assignee: Optional[str]
    created_date: Optional[str]
    duedate: Optional[str]
    change: Optional[List[ChangeSchema]]
    point: Optional[int]
    is_deleted: Optional[bool]


class PatchTicketSchema(BaseModel):
    issue_type: Optional[str] = Field(None, description="Type of the issue")
    status: Optional[str] = Field(None, description="Current status of the ticket")
    assignee: Optional[str] = Field(None, description="Person assigned to the ticket")
    duedate: Optional[str] = Field(None, description="Due date for the ticket")
    change: Optional[List[ChangeSchema]] = Field(
        None, description="Changes related to the ticket"
    )
    point: Optional[int] = Field(None, description="Point value of the ticket")
    is_deleted: Optional[bool] = Field(None, description="Soft delete status")

    class Config:
        schema_extra = {
            "example": {
                "issue_type": "Bug",
                "status": "In Progress",
                "assignee": "John Doe",
                "duedate": "2024-12-31T00:00:00",
                "change": [
                    {
                        "change_from": "Open",
                        "change_key": "status",
                        "change_to": "In Progress",
                        "blame": "John Doe",
                        "action_date": "2024-09-20T12:00:00",
                    }
                ],
                "point": 5,
                "is_deleted": False,
            }
        }
