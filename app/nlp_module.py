from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict, Union
from app.recommender import get_recommendations_user_based, get_recommendations_item_based
from app.scraper import scrape_all
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import SearchHistory
# Load the pre-trained conversational model
model_name = 'microsoft/DialoGPT-medium'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

async def generate_response(prompt: str, history: List[str]) -> str:
    """
    Generate a response from the conversational model.
    """
    input_text = ' '.join(history + [prompt])
    inputs = tokenizer.encode(input_text, return_tensors='pt')
    response = model.generate(inputs, max_length=1000, pad_token_id=tokenizer.eos_token_id)
    response_text = tokenizer.decode(response[:, inputs.shape[-1]:][0], skip_special_tokens=True)
    return response_text

async def handle_query(user_query: str, user_id: int, db: AsyncSession) -> str:
    """
    Handle user queries by integrating with the scraper and recommender.
    """
    # Check if the query relates to recommendations
    if 'recommend' in user_query.lower():
        recommendations = await get_recommendations_user_based(user_id, db)
        if not recommendations:
            recommendations = await get_recommendations_item_based(user_id, db)
        response = f"Based on your query, I recommend the following products: {', '.join([r['title'] for r in recommendations])}"
        return response

    # Check if the query relates to searching for products
    elif 'search' in user_query.lower():
        product_name = user_query.lower().replace('search', '').strip()
        products = await scrape_all(product_name)
        if products:
            response = f"I found these products for you: {', '.join([product['name'] for product in products[:5]])}."
        else:
            response = "Sorry, I couldn't find any products matching your query."
        return response

    # For other queries, generate a conversational response
    else:
        return await generate_response(user_query, [])

async def handle_conversation(user_id: int, message: str, db: AsyncSession) -> str:
    """
    Handle conversation history and provide responses.
    """
    # Retrieve or initialize conversation history
    async with db() as session:
        stmt = select(SearchHistory).where(SearchHistory.user_id == user_id).order_by(SearchHistory.search_time.desc())
        result = await session.execute(stmt)
        history_entries = result.scalars().all()

    history = [entry.query for entry in history_entries]
    
    # Generate a response based on the message
    response = await handle_query(message, user_id, db)
    
    # Update conversation history
    new_history = SearchHistory(user_id=user_id, query=message, results={"response": response})
    async with db() as session:
        session.add(new_history)
        await session.commit()
    
    return response
