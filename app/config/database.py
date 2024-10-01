from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection settings
MONGO_DETAILS = "mongodb+srv://huytq108:135089348709@huytq108.d8m8ux9.mongodb.net/ticket-database?retryWrites=true&w=majority&appName=huytq108"

client = AsyncIOMotorClient(MONGO_DETAILS)
db = client["ticket-database"]
ticket_collection = db.get_collection("tickets")
