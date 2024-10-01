from fastapi import APIRouter, HTTPException, Body
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from bson import ObjectId
from models.ticket import TicketSchema, UpdateTicketSchema, PatchTicketSchema
from config.database import ticket_collection

router = APIRouter()
app = FastAPI()


def ticket_helper(ticket) -> dict:
    return {
        "ticket_id": str(ticket["_id"]),
        "issue_type": ticket["issue_type"],
        "status": ticket["status"],
        "assignee": ticket["assignee"],
        "created_date": ticket["created_date"],
        "duedate": ticket.get("duedate"),
        "change": ticket["change"],
        "point": ticket["point"],
        "is_deleted": ticket["is_deleted"],
    }


# Create Ticket - POST /ticket
@router.post("/ticket", tags=["Ticket"], response_description="Create a new ticket")
async def create_ticket(ticket: TicketSchema = Body(...)):
    ticket = jsonable_encoder(ticket)
    new_ticket = await ticket_collection.insert_one(ticket)
    created_ticket = await ticket_collection.find_one({"_id": new_ticket.inserted_id})
    return ticket_helper(created_ticket)


# Update Ticket - PUT /ticket/{ticket_id}
@router.put(
    "/ticket/{ticket_id}", tags=["Ticket"], response_description="Update a ticket"
)
async def update_ticket(ticket_id: str, ticket: UpdateTicketSchema = Body(...)):
    ticket = {k: v for k, v in ticket.dict().items() if v is not None}
    if len(ticket) >= 1:
        update_result = await ticket_collection.update_one(
            {"ticket_id": ticket_id}, {"$set": ticket}
        )
        if update_result.modified_count == 1:
            updated_ticket = await ticket_collection.find_one({"ticket_id": ticket_id})
            if updated_ticket:
                return ticket_helper(updated_ticket)
    raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")


# Delete Ticket - DELETE /ticket/{ticket_id}
@router.delete(
    "/ticket/{ticket_id}", tags=["Ticket"], response_description="Delete a ticket"
)
async def soft_delete_ticket(ticket_id: str):
    update_result = await ticket_collection.update_one(
        {"ticket_id": ticket_id}, {"$set": {"is_deleted": True}}
    )
    if update_result.modified_count == 1:
        return {"message": f"Ticket {ticket_id} soft deleted successfully"}
    raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")


# Get All Tickets - GET /ticket
@router.get("/ticket", tags=["Ticket"], response_description="List all tickets")
async def list_tickets(page: int = 1):
    limit = 4  # Number of items per page
    skip = (page - 1) * limit
    # skip là số item trên một trang còn skip là số items bỏ qua trên mỗi trang
    # Get the total number of tickets
    total_tickets = await ticket_collection.count_documents({})

    # Check if the page number is valid
    if skip >= total_tickets:
        raise HTTPException(status_code=404, detail="Page number out of range")

    tickets = (
        await ticket_collection.find().skip(skip).limit(limit).to_list(length=limit)
    )
    return {
        "page": page,
        "total_pages": (total_tickets + limit - 1) // limit,
        "total_tickets": total_tickets,
        "tickets": [ticket_helper(ticket) for ticket in tickets],
    }


# Get Ticket by ID - GET /ticket/{ticket_id}
@router.get(
    "/ticket/{ticket_id}", tags=["Ticket"], response_description="Get a single ticket"
)
async def get_ticket(ticket_id: str):
    ticket = await ticket_collection.find_one({"ticket_id": ticket_id})
    if ticket:
        return ticket_helper(ticket)
    raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")


# Patch Ticket - PATCH /ticket/{ticket_id}
@router.patch(
    "/ticket/{ticket_id}", tags=["Ticket"], response_description="Patch a ticket"
)
async def patch_ticket(ticket_id: str, ticket: PatchTicketSchema = Body(...)):
    ticket = {k: v for k, v in ticket.dict().items() if v is not None}
    if len(ticket) >= 1:
        update_result = await ticket_collection.update_one(
            {"ticket_id": ticket_id}, {"$set": ticket}
        )
        if update_result.modified_count == 1:
            updated_ticket = await ticket_collection.find_one({"ticket_id": ticket_id})
            if updated_ticket:
                return ticket_helper(updated_ticket)
    raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
