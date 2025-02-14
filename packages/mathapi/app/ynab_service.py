from app.ynab_api import fetch, get_uncategorized_transactions
from app.ai_api import suggest_category
from app.categories_api import get_categories_for_budget
from app.budget_api import get_objectid_for_budget, convert_objectid_to_str
import logging

def apply_suggested_categories_service(budget_uuid):
    """Fetch uncategorized transactions, suggest categories, and update them in YNAB."""
    try:
        # Fetch budget ID and uncategorized transactions
        budget_id = get_objectid_for_budget(budget_uuid)
        uncategorized_transactions = get_uncategorized_transactions(budget_uuid)
        categories = get_categories_for_budget(budget_id)

        if not uncategorized_transactions:
            return {"message": "No uncategorized transactions found"}

        updated_transactions = []

        for transaction in uncategorized_transactions:
            try:
                # Suggest a category using AI
                suggested_category_name = suggest_category(transaction, categories)
                suggested_category = next(
                    (cat for cat in categories if cat["name"] == suggested_category_name), None
                )

                if not suggested_category:
                    logging.warning(f"No matching category found for transaction: {transaction['id']}")
                    continue

                # Update transaction in YNAB
                print (f"Updating transaction {transaction['id']} with category {suggested_category}")
                transaction_id = transaction["id"]
                memo = transaction.get("memo") or ""  # Ensure memo is a string
                updated_memo = f"{memo} AI suggested".strip()   

                path = f"budgets/{budget_uuid}/transactions/{transaction_id}"
                body = {
                    "transaction": {
                        "category_id": suggested_category["uuid"],
                        "approved": True,
                        "flag_color": "blue",
                        "memo": updated_memo
                    }
                }
                result = fetch("PUT", path, body)
                if "error" not in result:
                    updated_transactions.append({
                        "transaction_id": transaction_id,
                        "status": "updated",
                        "memo": updated_memo
                    })
                else:
                    logging.warning(f"Failed to update transaction {transaction_id}: {result['error']}")

            except Exception as e:
                logging.warning(f"Error processing transaction {transaction['id']}: {e}")
                continue

        return updated_transactions

    except Exception as e:
        logging.error(f"Error in apply_suggested_categories_service: {e}")
        raise
