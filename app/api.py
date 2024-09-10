from fastapi import APIRouter, HTTPException, Depends, status
from app.scraper import scrape_all
from typing import List, Dict
from app.models import User
from app.recommender import get_recommendations_user_based, get_recommendations_item_based
from app.auth.deps import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.nlp_module import handle_conversation
import logging

# Initialize the router
router = APIRouter()

# Initialize logger
logger = logging.getLogger(__name__)

# Define the data model for user messages
class UserMessage(BaseModel):
    user_id: int
    message: str

# Define the data model for bot responses
class BotResponse(BaseModel):
    response: str

# Chat endpoint - interacts with the NLP module
@router.post("/chat", response_model=BotResponse)
async def chat(user_message: UserMessage, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Received message from user {user_message.user_id}: {user_message.message}")
        
        # Process the user message using the NLP module
        response_text = await handle_conversation(user_message.user_id, user_message.message, db)
        
        logger.info(f"Generated response: {response_text}")
        return BotResponse(response=response_text)
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Chat processing failed.")

# Scrape endpoint - scrapes products from multiple sources
@router.get("/scrape", response_model=List[Dict[str, str]])
async def scrape(product_name: str) -> List[Dict[str, str]]:
    try:
        logger.info(f"Scraping for product: {product_name}")
        
        # Scrape the product data from all platforms
        products = await scrape_all(product_name)
        
        return products
    
    except Exception as e:
        logger.error(f"Error in scraping products: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Scraping failed.")

# Recommendations endpoint - gets item-based recommendations for the current user
@router.get("/recommendations", response_model=Dict[str, List[Dict[str, str]]])
async def recommendations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        logger.info(f"Fetching item-based recommendations for user: {current_user.id}")
        
        # Get item-based recommendations for the user
        recommendations = await get_recommendations_item_based(current_user.id, db)
        
        # Return recommendations as a list of dictionaries
        return {"recommendations": recommendations.to_dict(orient='records')}
    
    except Exception as e:
        logger.error(f"Error in fetching recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Recommendation fetching failed.")

# User-based recommendations endpoint - gets user-based recommendations by user ID
@router.get("/recommendations/user_based/{user_id}", response_model=List[Dict[str, str]])
async def user_based_recommendations(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Fetching user-based recommendations for user: {user_id}")
        
        # Get user-based recommendations for the specified user
        recommendations_df = await get_recommendations_user_based(user_id, db)
        
        # Check if no recommendations are found
        if recommendations_df.empty:
            raise HTTPException(status_code=404, detail="No recommendations found for this user.")
        
        # Return the recommendations as a list of dictionaries
        return recommendations_df.to_dict(orient="records")
    
    except Exception as e:
        logger.error(f"Error in fetching user-based recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: User-based recommendation fetching failed.")

# Item-based recommendations endpoint - gets item-based recommendations by user ID
@router.get("/recommendations/item_based/{user_id}", response_model=List[Dict[str, str]])
async def item_based_recommendations(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Fetching item-based recommendations for user: {user_id}")
        
        # Get item-based recommendations for the specified user
        recommendations_df = await get_recommendations_item_based(user_id, db)
        
        # Check if no recommendations are found
        if recommendations_df.empty:
            raise HTTPException(status_code=404, detail="No recommendations found for this user.")
        
        # Return the recommendations as a list of dictionaries
        return recommendations_df.to_dict(orient="records")
    
    except Exception as e:
        logger.error(f"Error in fetching item-based recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Item-based recommendation fetching failed.")
