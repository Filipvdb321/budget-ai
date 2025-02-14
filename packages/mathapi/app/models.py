from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

try:
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client.get_default_database()
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

def get_user_by_auth_id(auth_id):
    """Get user from MongoDB by Auth0 ID."""
    try:
        return db.users.find_one({"authId": auth_id})
    except Exception as e:
        logger.error(f"Error fetching user {auth_id}: {str(e)}")
        return None

def get_user_from_request(request):
    """Get user from request context."""
    try:
        auth_id = request.auth['payload']['sub']
        if not auth_id:
            logger.warning("No auth_id found in request")
            return None
        
        user = get_user_by_auth_id(auth_id)
        if not user:
            logger.warning(f"No user found for auth_id {auth_id}")
            return None
            
        return user
    except Exception as e:
        logger.error(f"Error getting user from request: {str(e)}")
        return None

def get_budget(budget_uuid, user):
    """Get budget by UUID and verify it belongs to user."""
    try:
        budget = db.budgets.find_one({"uuid": budget_uuid})
        if not budget:
            logger.warning(f"Budget {budget_uuid} not found")
            return None
            
        # Verify budget belongs to user
        if str(budget.get('userId')) != str(user.get('_id')):
            logger.warning(f"Budget {budget_uuid} does not belong to user {user.get('_id')}")
            return None
            
        return budget
    except Exception as e:
        logger.error(f"Error fetching budget {budget_uuid}: {str(e)}")
        return None 