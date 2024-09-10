from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Product, SearchHistory
from typing import List, Dict
import numpy as np

# Function to get recommendations using user-based collaborative filtering
async def get_recommendations_user_based(user_id: int, db: AsyncSession) -> List[Dict[str, str]]:
    # Fetch user ratings from the database
    query = """
    SELECT sh.user_id, p.title, sh.results->>'rating' as rating
    FROM search_history sh
    JOIN products p ON p.id = sh.results->>'product_id'
    WHERE sh.user_id = :user_id
    """
    result = await db.execute(query, {"user_id": user_id})
    user_data = result.fetchall()

    if not user_data:
        return []  # Return an empty list if no user data

    # Convert user data to a list of dictionaries
    user_ratings = [{"user_id": row[0], "title": row[1], "rating": float(row[2])} for row in user_data]

    # Fetch all user ratings for collaborative filtering
    query_all = """
    SELECT sh.user_id, p.title, sh.results->>'rating' as rating
    FROM search_history sh
    JOIN products p ON p.id = sh.results->>'product_id'
    """
    result_all = await db.execute(query_all)
    all_data = result_all.fetchall()

    # Convert all data to a list of dictionaries
    all_ratings = [{"user_id": row[0], "title": row[1], "rating": float(row[2])} for row in all_data]

    # Create a user-item matrix
    users = list(set(rating["user_id"] for rating in all_ratings))
    items = list(set(rating["title"] for rating in all_ratings))
    user_item_matrix = np.zeros((len(users), len(items)))

    user_index = {user: i for i, user in enumerate(users)}
    item_index = {item: i for i, item in enumerate(items)}

    for rating in all_ratings:
        user_idx = user_index[rating["user_id"]]
        item_idx = item_index[rating["title"]]
        user_item_matrix[user_idx, item_idx] = rating["rating"]

    # Compute cosine similarity between users
    similarity_matrix = cosine_similarity(user_item_matrix)

    # Get similar users to the target user
    target_user_idx = user_index[user_id]
    similar_users = sorted(range(len(users)), key=lambda i: similarity_matrix[target_user_idx, i], reverse=True)
    similar_users = [users[i] for i in similar_users if users[i] != user_id]

    # Get recommendations based on similar users' ratings
    recommendations = {}
    for similar_user in similar_users:
        similar_user_idx = user_index[similar_user]
        for item_idx, rating in enumerate(user_item_matrix[similar_user_idx]):
            if rating > 0:
                item = items[item_idx]
                if item not in recommendations and item not in [r["title"] for r in user_ratings]:
                    recommendations[item] = rating

    # Get top 10 recommendations
    top_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:10]

    return [{"title": item, "rating": 0} for item, _ in top_recommendations]

# Function to get recommendations using item-based collaborative filtering
async def get_recommendations_item_based(user_id: int, db: AsyncSession) -> List[Dict[str, str]]:
    # Fetch user ratings from the database
    query = """
    SELECT sh.user_id, p.title, sh.results->>'rating' as rating
    FROM search_history sh
    JOIN products p ON p.id = sh.results->>'product_id'
    WHERE sh.user_id = :user_id
    """
    result = await db.execute(query, {"user_id": user_id})
    user_data = result.fetchall()

    if not user_data:
        return []  # Return an empty list if no user data

    # Convert user data to a list of dictionaries
    user_ratings = [{"user_id": row[0], "title": row[1], "rating": float(row[2])} for row in user_data]

    # Fetch all user ratings for collaborative filtering
    query_all = """
    SELECT sh.user_id, p.title, sh.results->>'rating' as rating
    FROM search_history sh
    JOIN products p ON p.id = sh.results->>'product_id'
    """
    result_all = await db.execute(query_all)
    all_data = result_all.fetchall()

    # Convert all data to a list of dictionaries
    all_ratings = [{"user_id": row[0], "title": row[1], "rating": float(row[2])} for row in all_data]

    # Create an item-user matrix
    items = list(set(rating["title"] for rating in all_ratings))
    users = list(set(rating["user_id"] for rating in all_ratings))
    item_user_matrix = np.zeros((len(items), len(users)))

    item_index = {item: i for i, item in enumerate(items)}
    user_index = {user: i for i, user in enumerate(users)}

    for rating in all_ratings:
        item_idx = item_index[rating["title"]]
        user_idx = user_index[rating["user_id"]]
        item_user_matrix[item_idx, user_idx] = rating["rating"]

    # Compute cosine similarity between items
    similarity_matrix = cosine_similarity(item_user_matrix)

    # Get similar items to the items rated by the target user
    rated_items = [rating["title"] for rating in user_ratings]
    similar_items = {}
    for item in rated_items:
        item_idx = item_index[item]
        for other_item_idx, similarity in enumerate(similarity_matrix[item_idx]):
            other_item = items[other_item_idx]
            if other_item not in rated_items:
                similar_items[other_item] = similar_items.get(other_item, 0) + similarity

    # Get top 10 recommendations
    top_recommendations = sorted(similar_items.items(), key=lambda x: x[1], reverse=True)[:10]

    return [{"title": item, "rating": 0} for item, _ in top_recommendations]