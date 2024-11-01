from fastapi import APIRouter, HTTPException, Body
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from models.ticket import TicketSchema, UpdateTicketSchema, PatchTicketSchema
from config.database import ticket_collection
import asyncio

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
        "point": ticket["point"],
        "is_deleted": ticket["is_deleted"],
        "change": ticket.get("change", []),  # Include change if exists
    }


# Create Ticket - POST /ticket
@router.post("/ticket", tags=["Ticket"], response_description="Create a new ticket")
async def create_ticket(ticket: TicketSchema = Body(...)):
    ticket = jsonable_encoder(ticket)
    new_ticket = await ticket_collection.insert_one(ticket)
    created_ticket = await ticket_collection.find_one({"_id": new_ticket.inserted_id})
    return ticket_helper(created_ticket)


# Update Ticket - PUT /ticket/{id}
@router.put("/ticket/{id}", tags=["Ticket"], response_description="Update a ticket")
async def update_ticket(id: str, ticket: UpdateTicketSchema = Body(...)):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    existing_ticket = await ticket_collection.find_one({"_id": obj_id})
    if not existing_ticket:
        raise HTTPException(status_code=404, detail=f"Ticket with ID {id} not found")

    update_data = {k: v for k, v in ticket.dict().items() if v is not None}
    change_list = existing_ticket.get("change", [])

    change_object = {
        "change_from": {},
        "change_key": [],
        "change_to": {},
        "blame": "user@example.com",  # Replace with actual user information
        "action_date": datetime.utcnow().isoformat(),
    }

    for field in ["issue_type", "status", "assignee", "duedate", "point"]:
        old_value = existing_ticket.get(field, None)
        new_value = update_data.get(field)
        if old_value != new_value and new_value is not None:
            change_object["change_from"][field] = old_value
            change_object["change_key"].append(field)
            change_object["change_to"][field] = new_value

    if change_object["change_key"]:
        change_list.append(change_object)
        update_data["change"] = change_list

    update_result = await ticket_collection.update_one(
        {"_id": obj_id}, {"$set": update_data}
    )

    if update_result.modified_count == 1:
        updated_ticket = await ticket_collection.find_one({"_id": obj_id})
        return ticket_helper(updated_ticket)

    raise HTTPException(status_code=404, detail=f"Ticket with ID {id} not found")


# Delete Ticket - DELETE /ticket/{id}
@router.delete("/ticket/{id}", tags=["Ticket"], response_description="Delete a ticket")
async def soft_delete_ticket(id: str):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    update_result = await ticket_collection.update_one(
        {"_id": obj_id}, {"$set": {"is_deleted": True}}
    )

    if update_result.modified_count == 1:
        return {"message": f"Ticket with ID {id} soft deleted successfully"}

    raise HTTPException(status_code=404, detail=f"Ticket with ID {id} not found")


# List Tickets - GET /ticket
@router.get("/ticket", tags=["Ticket"], response_description="List all tickets")
async def list_tickets(page: int = 1):
    limit = 4
    skip = (page - 1) * limit

    total_tickets = await ticket_collection.count_documents({})

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


# Get a Single Ticket - GET /ticket/{id}
@router.get("/ticket/{id}", tags=["Ticket"], response_description="Get a single ticket")
async def get_ticket(id: str):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    ticket = await ticket_collection.find_one({"_id": obj_id})

    if ticket:
        return ticket_helper(ticket)

    raise HTTPException(status_code=404, detail=f"Ticket with ID {id} not found")


# Patch Ticket - PATCH /ticket/{id}
@router.patch("/ticket/{id}", tags=["Ticket"], response_description="Patch a ticket")
async def patch_ticket(id: str, ticket: PatchTicketSchema = Body(...)):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    existing_ticket = await ticket_collection.find_one({"_id": obj_id})

    if not existing_ticket:
        raise HTTPException(status_code=404, detail=f"Ticket with ID {id} not found")

    update_data = {k: v for k, v in ticket.dict().items() if v is not None}
    change_list = existing_ticket.get("change", [])

    change_object = {
        "change_from": {},
        "change_key": [],
        "change_to": {},
        "blame": "user@example.com",
        "action_date": datetime.utcnow().isoformat(),
    }

    for field in ["issue_type", "status", "assignee", "duedate", "point"]:
        old_value = existing_ticket.get(field, None)
        new_value = update_data.get(field)

        if old_value != new_value and new_value is not None:
            change_object["change_from"][field] = old_value
            change_object["change_key"].append(field)
            change_object["change_to"][field] = new_value

    if change_object["change_key"]:
        change_list.append(change_object)
        update_data["change"] = change_list

    update_result = await ticket_collection.update_one(
        {"_id": obj_id}, {"$set": update_data}
    )

    if update_result.modified_count == 1:
        updated_ticket = await ticket_collection.find_one({"_id": obj_id})
        return ticket_helper(updated_ticket)

    raise HTTPException(status_code=404, detail=f"Ticket with ID {id} not found")
