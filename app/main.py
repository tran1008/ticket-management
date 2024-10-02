from fastapi import FastAPI, HTTPException, Request
from routers import ticket
import httpx
from models.ticket import TicketSchema, UpdateTicketSchema, PatchTicketSchema

app = FastAPI()

# Include routers
app.include_router(ticket.router)


@app.get("/", tags=["Root"])
async def hello_python():
    return {"message": "Welcome to the Ticket Management API"}


# truyền vào một dependencies rỗng đồng nghĩa với việc nó chỉ chạy một lần sau khi component được render lần đầu tiên
# khi tạo một ứng dụng fastapi có một thuộc tính webhook rằng bạn có thể sử dụng để định nghĩa webhooks
# @app.webhooks.post("Create-Webhook")
# # để thiết lập một webhook bạn cần đăng ký một địa chỉ endpoint url cho webhook provider gửi request khi cần
# def create_webhook(body: TicketSchema):
#     if body.is_deleted:
#         raise HTTPException(status_code=400, detail="Cannot create a deleted ticket")
#     if body.status not in {"Resolved", "Late"}:
#         raise HTTPException(status_code=400, detail="Invalid status for the ticket")

#     # Assume we save the ticket to a database (mocked here)
#     # save_to_database(body)

#     # Return a success message with the ticket ID
#     return {"message": "Webhook received successfully", "ticket_id": body.ticket_id}
