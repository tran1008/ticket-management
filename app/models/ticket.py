from typing import List, Optional
from pydantic import BaseModel, Field


class ChangeSchema(BaseModel):
    change_from: str
    change_from_key: str
    change_to: str
    change_to_key: str
    filed: str
    blame: str
    at: int


class TicketSchema(BaseModel):
    ticket_id: str
    title: str
    issue_type: str
    status: str
    assignee: str
    created_date: str
    duedate: Optional[str]
    point: int
    is_deleted: bool


class UpdateTicketSchema(BaseModel):
    ticket_id: Optional[str] = Field(None, description="Ticket ID")
    title: Optional[str] = Field(None, description="Description for Ticket ID")
    issue_type: Optional[str] = Field(None, description="Type of issue")
    status: Optional[str] = Field(None, description="Status of the ticket")
    assignee: Optional[str] = Field(None, description="Assignee of the ticket")
    created_date: Optional[str] = Field(None, description="Creation date of the ticket")
    duedate: Optional[str] = Field(None, description="Due date of the ticket")
    point: Optional[int] = Field(None, description="Point value of the ticket")
    is_deleted: Optional[bool] = Field(None, description="Soft delete flag")
    change: Optional[List[ChangeSchema]] = Field(None, description="Change history")


class PatchTicketSchema(BaseModel):
    ticket_id: Optional[str] = Field(None, description="Ticket ID")
    title: Optional[str] = Field(None, description="Description for Ticket ID")
    issue_type: Optional[str] = Field(None, description="Type of issue")
    status: Optional[str] = Field(None, description="Status of the ticket")
    assignee: Optional[str] = Field(None, description="Assignee of the ticket")
    created_date: Optional[str] = Field(None, description="Creation date of the ticket")
    duedate: Optional[str] = Field(None, description="Due date of the ticket")
    point: Optional[int] = Field(None, description="Point value of the ticket")
    is_deleted: Optional[bool] = Field(None, description="Soft delete flag")
    change: Optional[List[ChangeSchema]] = Field(None, description="Change history")
