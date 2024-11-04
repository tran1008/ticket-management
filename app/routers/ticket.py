from fastapi import APIRouter, HTTPException, Body
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from typing import List
from bson import ObjectId
from models.ticket import (
    TicketSchema,
    UpdateTicketSchema,
    PatchTicketSchema,
    ChangeSchema,
)  # Ensure ChangeSchema is imported
from config.database import ticket_collection

router = APIRouter()


def ticket_helper(ticket) -> dict:
    return {
        "_id": str(ticket["_id"]),
        "ticket_id": ticket["ticket_id"],
        "issue_type": ticket["issue_type"],
        "status": ticket["status"],
        "assignee": ticket["assignee"],
        "created_date": ticket["created_date"],
        "duedate": ticket.get("duedate"),
        "point": ticket["point"],
        "is_deleted": ticket["is_deleted"],
        "change": ticket.get("change", []),
    }


def track_changes(existing_ticket, update_data):
    changes = []
    for field, new_value in update_data.items():
        if field in existing_ticket and existing_ticket[field] != new_value:
            change_entry = ChangeSchema(
                change_from=str(existing_ticket[field]),  # Chuyển thành chuỗi
                change_from_key=field,
                change_to=str(new_value),  # Chuyển thành chuỗi
                change_to_key=field,
                filed=field,
                blame="system",  # Adjust this if needed
                at=int(datetime.utcnow().timestamp()),
            )
            changes.append(change_entry.dict())
    return changes


# Create Ticket - POST /ticket
@router.post("/ticket", tags=["Ticket"], response_description="Create a new ticket")
async def create_ticket(ticket: TicketSchema = Body(...)):
    ticket_data = jsonable_encoder(ticket)
    new_ticket = await ticket_collection.insert_one(ticket_data)
    created_ticket = await ticket_collection.find_one({"_id": new_ticket.inserted_id})
    return ticket_helper(created_ticket)


# Update Ticket - PUT /ticket/{id}
@router.put("/ticket/{id}", tags=["Ticket"], response_description="Update a ticket")
async def update_ticket(id: str, ticket: UpdateTicketSchema = Body(...)):
    try:
        obj_id = ObjectId(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    existing_ticket = await ticket_collection.find_one({"_id": obj_id})
    if not existing_ticket:
        raise HTTPException(status_code=404, detail=f"Ticket with ID {id} not found")

    update_data = {k: v for k, v in ticket.dict().items() if v is not None}
    changes = track_changes(existing_ticket, update_data)

    if changes:
        # Add changes to the change list in the ticket
        change_list = existing_ticket.get("change", [])
        change_list.extend(changes)
        update_data["change"] = change_list

    update_result = await ticket_collection.update_one(
        {"_id": obj_id}, {"$set": update_data}
    )

    if update_result.modified_count == 1:
        updated_ticket = await ticket_collection.find_one({"_id": obj_id})
        return ticket_helper(updated_ticket)

    raise HTTPException(status_code=404, detail=f"Ticket with ID {id} not found")


# Patch Ticket - PATCH /ticket/{id}
@router.patch("/ticket/{id}", tags=["Ticket"], response_description="Patch a ticket")
async def patch_ticket(id: str, ticket: PatchTicketSchema = Body(...)):
    try:
        obj_id = ObjectId(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    existing_ticket = await ticket_collection.find_one({"_id": obj_id})

    if not existing_ticket:
        raise HTTPException(status_code=404, detail=f"Ticket with ID {id} not found")

    update_data = {k: v for k, v in ticket.dict().items() if v is not None}
    changes = track_changes(existing_ticket, update_data)

    if changes:
        # Add changes to the change list in the ticket
        change_list = existing_ticket.get("change", [])
        change_list.extend(changes)
        update_data["change"] = change_list

    update_result = await ticket_collection.update_one(
        {"_id": obj_id}, {"$set": update_data}
    )

    if update_result.modified_count == 1:
        updated_ticket = await ticket_collection.find_one({"_id": obj_id})
        return ticket_helper(updated_ticket)

    raise HTTPException(status_code=404, detail=f"Ticket with ID {id} not found")
