# activate env

```
source env/bin/activate

```

# install deps

```
pip install -r requirements.txt
```

# Step 4: Run the Flask App

With dependencies installed, you can start the Flask app.

## Set the Flask app environment:

```bash
export FLASK_APP=app/app.py      # Replace `app.py` with your main app file if different
export FLASK_ENV=development  # This enables debug mode
```

## Run the Flask app:

```bash
flask run
```

## balance predictions

### Interactive

http://127.0.0.1:5000/balance-prediction/interactive?budget_id=1b443ebf-ea07-4ab7-8fd5-9330bf80608c&days_ahead=120

### non interactive json

http://127.0.0.1:5000/balance-prediction/data?budget_id=1b443ebf-ea07-4ab7-8fd5-9330bf80608c&days_ahead=120

## sheduled transactions

http://127.0.0.1:5000/sheduled-transactions?budget_id=1b443ebf-ea07-4ab7-8fd5-9330bf80608c

# category suggestions

http://127.0.0.1:5000/uncategorised-transactions/suggest-categories?budget_id=1b443ebf-ea07-4ab7-8fd5-9330bf80608c

# apply suggestions

POST http://127.0.0.1:5000/uncategorised-transactions/apply-categories?budget_id=1b443ebf-ea07-4ab7-8fd5-9330bf80608c

# Math API

This API provides mathematical calculations and predictions for budgeting purposes.

## Installation

```bash
pip install -r requirements.txt
```

## Running Tests

To run all tests:
```bash
PYTHONPATH=. python -m pytest
```

### Test Fixtures

The tests use fixtures stored in `app/tests/fixtures/`:
- `input_data.json`: Contains test data (categories, accounts, scheduled transactions)
- `expected_output.json`: Contains expected prediction results

To update the test fixtures with real data:
```bash
# Make sure you're in the mathapi directory
cd packages/mathapi

# Record new fixtures (this will use real API data)
PYTHONPATH=. RECORD_FIXTURES=1 python -m pytest app/tests/test_prediction_api.py::TestPredictionApi::test_record_new_fixtures -v

# Verify the tests pass with new fixtures
PYTHONPATH=. python -m pytest app/tests/test_prediction_api.py -v
```

Note: Recording new fixtures will use real data from your YNAB budget and MongoDB database. Make sure your `.env` file is properly configured.

## Testing

### Running Tests
To run the tests:
```bash
python -m pytest tests/
```

To run tests with verbose output:
```bash
python -m pytest tests/ -v
```

### Code Coverage
You can check the code coverage in different ways:

1. Terminal output with missing lines:
```bash
python -m pytest tests/ --cov=app --cov-report=term-missing -v
```

2. Generate an HTML report (recommended for detailed analysis):
```bash
python -m pytest tests/ --cov=app --cov-report=html
```
The report will be generated in the `htmlcov` directory. Open `htmlcov/index.html` in your browser to view it.

3. Generate an XML report (useful for CI/CD):
```bash
python -m pytest tests/ --cov=app --cov-report=xml
```

You can also run tests for specific functions:
```bash
python -m pytest tests/ -k "test_function_name"
```

Or show only missing coverage:
```bash
python -m pytest tests/ --cov=app --cov-report=term-missing:skip-covered
```
