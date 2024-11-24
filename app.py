from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__)

def fetch_power_breakdown(latitude, longitude, api_key):
    url = "https://api.electricitymap.org/v3/power-breakdown/history"
    headers = {"auth-token": api_key}
    params = {"lat": latitude, "lon": longitude}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        historical_data = data.get("history", [])
        if not historical_data:
            return {"error": "No historical data available."}

        renewable_percentages = []

        for entry in historical_data:
            datetime = entry.get("datetime")
            production = entry.get("powerProductionBreakdown", {})
            if not production:
                continue

            total_production = sum(v for v in production.values() if v is not None)
            renewable_production = sum(
                v for k, v in production.items() if k in ["wind", "solar", "hydro"] and v is not None
            )

            if total_production > 0:
                renewable_percentage = (renewable_production / total_production) * 100
                renewable_percentages.append((datetime, renewable_percentage))

        renewable_percentages.sort(key=lambda x: x[1], reverse=True)
        top_5_renewable_hours = renewable_percentages[:5]
        return {"top_5": top_5_renewable_hours}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


@app.route("/")
def serve_home():
    return send_from_directory(".", "index.html")


@app.route("/fetch_power", methods=["POST"])
def fetch_power():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    api_key = data.get("api_key")

    if not latitude or not longitude or not api_key:
        return jsonify({"error": "Missing parameters"}), 400

    result = fetch_power_breakdown(latitude, longitude, api_key)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
