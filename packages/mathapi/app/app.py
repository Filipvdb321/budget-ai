import os
import itertools
from flask import Flask, jsonify, request, render_template
from app.ynab_service import apply_suggested_categories_service
from app.ynab_api import get_scheduled_transactions, get_uncategorized_transactions
from app.categories_api import get_categories_for_budget
from app.budget_api import get_objectid_for_budget
from app.accounts_api import get_accounts_for_budget
from app.prediction_api import project_daily_balances_with_reasons, projected_balances_for_budget
from app.categories_api import get_categories_for_budget
from app.ai_api import suggest_category
import logging
import json
from flask_cors import CORS
from dotenv import load_dotenv
from app.auth import requires_auth
from app.models import get_user_from_request, get_budget

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Setup CORS
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, resources={
    r"/*": {
        "origins": CORS_ORIGINS,
        "methods": ["GET", "POST", "PUT", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type"],
        "supports_credentials": True
    }
})

def load_simulations_folder(folder_name="simulations"):
    """Load all simulations from a folder containing JSON files."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(base_dir, folder_name)
    
    simulations = {"Actual Balance": None}  # Treat the baseline as a default simulation
    if not os.path.exists(folder_path):
        logging.warning(f"Simulation folder not found: {folder_path}")
        return simulations

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, "r") as file:
                    simulations[file_name] = json.load(file)
            except Exception as e:
                logging.warning(f"Failed to load simulation file {file_name}: {str(e)}")
    return simulations

def generate_unique_colors():
    """Generate unique colors for the plots."""
    colors = itertools.cycle(["red", "green", "blue", "purple", "orange", "cyan", "magenta"])
    yield "black"  # First color for the baseline
    for color in colors:
        yield color

@app.route('/balance-prediction/interactive', methods=['GET'])
def balance_prediction_interactive():
    # Step 1: Get `budget_id` from query parameters
    budget_uuid = request.args.get('budget_id')
    if not budget_uuid:
        return "budget_id query parameter is required", 400

    # Step 2: Load simulations from folder
    simulations = load_simulations_folder()
    # Handle optional days_ahead parameter
    days_ahead_param = request.args.get('days_ahead')
    try:
        days_ahead = int(days_ahead_param) if days_ahead_param is not None else 300
    except ValueError:
        return "Invalid days_ahead query parameter, it must be an integer.", 400

    # Step 3: Fetch required data
    try:
        budget_id = get_objectid_for_budget(budget_uuid)
        future_transactions = get_scheduled_transactions(budget_uuid)
        categories = get_categories_for_budget(budget_id)
        accounts = get_accounts_for_budget(budget_id)
    except Exception as e:
        return f"Error fetching data: {str(e)}", 500

    # Step 4: Generate plot data for the baseline and all simulations
    plot_data = []
    color_generator = generate_unique_colors()
    for simulation_name, simulation_data in simulations.items():
        try:
            # Get projected balances with raw numeric data
            projected_balances = project_daily_balances_with_reasons(
                accounts, categories, future_transactions, days_ahead, simulation_data
            )
        except Exception as e:
            logging.warning(f"Error processing simulation '{simulation_name}': {str(e)}")
            continue

        # Prepare data for the plot
        dates = list(projected_balances.keys())
        balances = [projected_balances[date]["balance"] for date in dates]  # Raw numbers
        hover_texts = []

        # Calculate hover text for each date
        for i, date in enumerate(dates):
            day_data = projected_balances[date]
            balance = day_data["balance"]  # Raw balance
            balance_diff = day_data.get("balance_diff", 0)  # Raw difference
            changes = day_data["changes"]

            # Format numbers for presentation
            hover_text = f"Date: {date}<br>Balance: {balance:.2f}€<br>Balance Difference: {balance_diff:.2f}€"
            if changes:
                hover_text += "<br>Changes:"
                for change in changes:
                    amount = change["amount"]  # Raw amount
                    if amount == 0:  # Skip zero-value changes
                        continue
                    simulation_flag = "(Simulation)" if change.get("is_simulation", False) else ""
                    hover_text += f"<br>{amount:.2f}€ ({change['category']} - {change['reason']}) {simulation_flag}"
            hover_texts.append(hover_text)

        # Add the line to the plot
        plot_data.append({
            "x": dates,
            "y": balances,
            "type": "scatter",
            "mode": "lines+markers",
            "name": simulation_name,
            "text": hover_texts,
            "hoverinfo": "text",
            "marker": {"color": next(color_generator)}
        })

    # Convert plot data to JSON for the template
    sanitized_plot_data = json.dumps(plot_data)

    # Render HTML template with plot data
    return render_template('balance_projection.html', plot_data=sanitized_plot_data)

@app.route('/balance-prediction/data')
@requires_auth
def get_prediction():
    """Get balance prediction for a budget."""
    try:
        user = get_user_from_request(request)
        if not user:
            return jsonify({"message": "User not found"}), 401
            
        budget_uuid = request.args.get('budget_id')
        if not budget_uuid:
            return jsonify({"message": "No budget_id provided"}), 400
            
        days_ahead = int(request.args.get('days_ahead', 300))
        
        # First get the MongoDB ObjectId for the budget
        budget_id = get_objectid_for_budget(budget_uuid)
        if not budget_id:
            return jsonify({"message": "Budget not found"}), 404
            
        # Then get the full budget document and verify ownership
        budget = get_budget(budget_uuid, user)
        if not budget:
            return jsonify({"message": "Budget not found or access denied"}), 404
            
        # Get YNAB connection details
        ynab_connection = user.get('ynab', {}).get('connection', {})
        if not ynab_connection:
            return jsonify({"message": "No YNAB connection"}), 400
            
        # Load simulations
        simulations = load_simulations_folder()
        
        # Fetch required data
        future_transactions = get_scheduled_transactions(budget_uuid)
        categories = get_categories_for_budget(budget_id)
        accounts = get_accounts_for_budget(budget_id)

        # Process each simulation and collect results
        results = {}
        for simulation_name, simulation_data in simulations.items():
            try:
                projected_balances = project_daily_balances_with_reasons(
                    accounts, categories, future_transactions, days_ahead, simulation_data
                )
                results[simulation_name] = projected_balances
            except Exception as e:
                logger.warning(f"Error processing simulation '{simulation_name}': {str(e)}")
                continue

        return jsonify(results)
        
    except ValueError as e:
        logger.warning(f"Invalid input: {str(e)}")
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        logger.error(f"Error generating prediction: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

@app.route('/sheduled-transactions', methods=['GET'])
def get_scheduled_transactions_route():
    budget_uuid = request.args.get('budget_id')
    if not budget_uuid:
        return "budget_id query parameter is required", 400

    try:
        transactions = get_scheduled_transactions(budget_uuid)
        return jsonify(transactions)
    except Exception as e:
        return f"Error fetching scheduled transactions: {str(e)}", 500
    
@app.route('/uncategorised-transactions/suggest-categories', methods=['GET'])
def suggest_categories_for_unscheduled_transactions():
    budget_uuid = request.args.get('budget_id')
    if not budget_uuid:
        return jsonify({"error": "budget_id query parameter is required"}), 400

    try:
        # Fetch budget ID and data
        budget_id = get_objectid_for_budget(budget_uuid)
        uncategorized_transactions = get_uncategorized_transactions(budget_uuid)
        categories = get_categories_for_budget(budget_id)
    except Exception as e:
        return jsonify({"error": f"Error fetching data: {str(e)}"}), 500

    if not uncategorized_transactions:
        return jsonify([])  # No uncategorized transactions found

    # Suggest categories for each uncategorized transaction
    suggested_transactions = []
    for transaction in uncategorized_transactions:
        try:
            suggested_category_name = suggest_category(transaction, categories)
            suggested_transactions.append({
                "transaction_id": transaction["id"],
                "payee_name": transaction["payee_name"],
                "amount": transaction["amount"],
                "date": transaction["date"],
                "suggested_category_name": suggested_category_name
            })
        except Exception as e:
             return jsonify({"error": f"Error fetching data: {str(e)}"}), 500

    return jsonify(suggested_transactions)

@app.route('/uncategorised-transactions/apply-categories', methods=['POST'])
def apply_suggested_categories():
    """Fetch transactions, suggest categories, and apply them."""
    budget_uuid = request.args.get('budget_id')
    if not budget_uuid:
        return jsonify({"error": "budget_id query parameter is required"}), 400

    try:
        # Delegate business logic to the service layer
        result = apply_suggested_categories_service(budget_uuid)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error applying categories: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
