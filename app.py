from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)


import os
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
        route_key = f"{origin}-{destination}"
        results = full_data.get("data", {}).get(route_key, [])

        if not results:
            return jsonify({'error': 'No flights found'}), 404

        best_day = min(results, key=lambda f: f["value"])
        return jsonify({
            "date": best_day["depart_date"],
            "savings": f"${best_day['value']}"
        })

    except Exception as e:
        return jsonify({'error': 'Failed to parse API result', 'details': str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
