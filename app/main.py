from fastapi import FastAPI, HTTPException, Request
from routers import ticket
import httpx
from models.ticket import TicketSchema, UpdateTicketSchema, PatchTicketSchema

import uvicorn

app = FastAPI()
# Include routers
app.include_router(ticket.router)


@app.get("/", tags=["Root"])
async def hello_python():
    return {"message": "Welcome to the Ticket Management API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
