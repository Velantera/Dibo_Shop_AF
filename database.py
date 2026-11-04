from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL, MONGO_DB_NAME

_client: AsyncIOMotorClient | None = None
_db = None

def init_db_sync():
    global _client, _db
    _client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    _db = _client[MONGO_DB_NAME]

# ==========================================
# PRODUCTS
# ==========================================
async def add_product(name: str, price: float, description: str, photo_file_id: str, stock: int, sizes: list):
    result = await _db.products.insert_one({
        "name": name, "price": price, "description": description,
        "photo_file_id": photo_file_id, "stock": stock, "sizes": sizes,
        "channel_message_id": None, # <-- NEW: To track the group post
        "created_at": datetime.utcnow(),
    })
    return str(result.inserted_id)

async def update_product(product_id: str, update_data: dict):
    try:
        await _db.products.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})
        return True
    except Exception:
        return False

# ... (Keep get_products, get_all_products, get_product, delete_product, decrement_stock, increment_stock as they are) ...

# ==========================================
# ORDERS
# ==========================================
async def create_order(user_id: int, username: str, items: list, total: float, payment_method: str = "pending"):
    result = await _db.orders.insert_one({
        "user_id": user_id,
        "username": username,
        "items": items,
        "total": total,
        "payment_method": payment_method,
        "status": "pending_details",
        "customer_name": "",
        "phone_number": "",
        "address": "",
        "created_at": datetime.utcnow(),
    })
    return str(result.inserted_id)

async def get_user_orders(user_id: int):
    # Only show orders that are NOT cancelled
    cursor = _db.orders.find({"user_id": user_id, "status": {"$ne": "cancelled"}}).sort("created_at", -1).limit(20)
    return await cursor.to_list(length=20)

# ... (Keep get_order, update_order_details, update_order_status as they are) ...
