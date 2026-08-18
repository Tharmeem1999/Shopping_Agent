"""
Reviews API - reads from 'reviews' table in store.db and returns aggregated reating information for products. 
"""

import sqlite3
import os

PATH_DB = os.path.join(os.path.dirname(__file__),"store.db")

def get_product_rating(product_id: int) -> dict:

    """Return average rating and review count for a single product"""

    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT AVG(rating), COUNT(*) FROM reviews WHERE product_id=?",
        (product_id,),
    )
    row = cursor.fetchone()
    conn.close()

    avg = round(row[0], 2) if row and row[0] is not None else 0.0
    count = row[1] if row else 0

    return {"product_id": product_id, "average_rating":avg, "review_count":count}

def get_ratings_for_products(product_ids: list[dict]) -> dict[dict]:

    """Return rating for list of product ids"""

    if not product_ids:
        return []

    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()
    placeholder = ",".join("?"* len(product_ids))
    cursor.execute(
        f"""
            SELECT product_id, AVG(rating), COUNT(*)
            FROM reviews
            WHERE product_id IN ({placeholder})
            GROUP BY product_id
        """,
        product_ids,
    )
    rows = cursor.fetchall()
    conn.close()

    ratings_map = {r[0]: {"average_rating": round(r[1], 2), "review_count": r[2]} for r in rows}
    return [
        {
            "product_id": pid,
            "average_rating": ratings_map.get(pid, {}).get("average_rating", 0.0),
            "review_count": ratings_map.get(pid, {}).get("review_count", 0),
        }
        for pid in product_ids
    ]

if __name__ == "__main__":
    # Single Product
    result = get_product_rating(2)
    print("Single product rating:")
    print(f" Product {result['product_id']}: {result['average_rating']} stars ({result['review_count']} reviews)")

    # Multiple Products
    print("\nBatch Ratings:")
    results = get_ratings_for_products([1,2,3,4])
    for r in results:
        print(f" Product {r['product_id']}: {r['average_rating']} stars ({r['review_count']} reviews)")