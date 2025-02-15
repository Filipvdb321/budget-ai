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
        logger.info("Auth payload from request: %s", request.auth['payload'])
        auth_id = request.auth['payload']['sub']
        logger.info("Found auth_id: %s", auth_id)
        
        if not auth_id:
            logger.warning("No auth_id found in request")
            return None
        
        user = get_user_by_auth_id(auth_id)
        if not user:
            logger.warning(f"No user found for auth_id {auth_id}")
            return None
            
        logger.info("Found user: %s", user)
        return user
    except Exception as e:
        logger.error(f"Error getting user from request: {str(e)}")
        return None

def get_budget(budget_uuid, user):
    """Get budget by UUID and verify it belongs to user."""
    try:
        logger.info(f"Looking for budget with uuid: {budget_uuid}")
        logger.info(f"User data: {user}")
        
        budget = db.localbudgets.find_one({"uuid": budget_uuid})
        if not budget:
            logger.warning(f"Budget with uuid {budget_uuid} not found in database")
            return None
            
        logger.info(f"Found budget: {budget}")
        
        # Verify budget belongs to user by checking if user._id is in the users array
        user_id = user.get('_id')
        budget_users = budget.get('users', [])
        logger.info(f"Checking if user {user_id} is in budget users: {budget_users}")
        
        if not any(str(uid) == str(user_id) for uid in budget_users):
            logger.warning(f"Budget {budget_uuid} does not belong to user {user_id}")
            return None
            
        return budget
    except Exception as e:
        logger.error(f"Error fetching budget {budget_uuid}: {str(e)}")
        return None 