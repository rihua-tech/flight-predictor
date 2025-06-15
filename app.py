from flask import Flask, request, jsonify  
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

TRAVELPAYOUTS_TOKEN = os.getenv("TRAVELPAYOUTS_TOKEN")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    origin = data.get('from', '').upper()
    destination = data.get('to', '').upper()
    date = data.get('date')

    if not origin or not destination or not date:
        return jsonify({'error': 'Missing input'}), 400

    month = date[:7]  # format YYYY-MM
    api_url = "https://api.travelpayouts.com/v2/prices/month-matrix"
    params = {
        "currency": "usd",
        "origin": origin,
        "destination": destination,
        "month": month,
        "token": TRAVELPAYOUTS_TOKEN
    }

    response = requests.get(api_url, params=params)
    if response.status_code != 200:
        return jsonify({'error': 'API failed', 'details': response.text}), 500

    try:
        full_data = response.json()
        results = full_data.get("data", [])

        if not isinstance(results, list) or not results:
            return jsonify({'error': 'No flights found'}), 404

        # 🟡 Find best date by lowest price
        best_day = min(results, key=lambda f: f.get("value", float('inf')))
        best_price = best_day.get("value")
        best_date = best_day.get("depart_date")

        if best_price is None or best_date is None:
            return jsonify({'error': 'No valid price/date found'}), 500

        # 🔮 Optional: Fake forecasting logic (for now)
        # Here we define forecast_percent as an integer (e.g. 80),
        # and forecast_trend must be defined before returning.
        # In real logic, you might compute these based on historical data.
        forecast_percent = 80      # e.g. 80% chance prices will move
        forecast_days = 3          # in 3 days
        forecast_trend = "increase"  # or "decrease" based on your logic

        # 🔮 Optional: Fake AI suggestion logic
        ai_days = 3
        ai_savings = 240

        # Build response JSON
        response_data = {
            "date": best_date,
            # Return savings as numeric or string; front-end handles either.
            # Here we return numeric:
            "savings": best_price,
            "forecast_percent": forecast_percent,
            "forecast_days": forecast_days,
            "forecast_trend": forecast_trend,
            "ai_savings": ai_savings,
            "ai_days": ai_days
        }
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': 'Failed to parse API result', 'details': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
