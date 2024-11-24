from flask import Flask, request, render_template, jsonify
import requests
import matplotlib
matplotlib.use('Agg')  # Use the non-GUI backend before importing pyplot
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import json

app = Flask(__name__)

# Function to fetch power data
def fetch_power_data(latitude, longitude, api_key):
    url = "https://api.electricitymap.org/v3/power-breakdown/history"
    headers = {"auth-token": api_key}
    params = {"lat": latitude, "lon": longitude}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Helper function to process data for visualization
def process_power_data(data):
    hourly_data = data.get('powerProductionBreakdownHistory', [])
    top_5_hours = []
    renewable_averages = {}

    if hourly_data:
        renewables = []
        for hour in hourly_data:
            renewable_power = sum([hour['powerProductionBreakdown'].get(src, 0) for src in ['solar', 'wind', 'hydro', 'biomass']])
            renewables.append((hour['datetime'], renewable_power))

        # Find top 5 renewable hours
        renewables.sort(key=lambda x: x[1], reverse=True)
        top_5_hours = renewables[:5]

        # Calculate average power production per source
        source_totals = {}
        for hour in hourly_data:
            for source, value in hour['powerProductionBreakdown'].items():
                if source not in source_totals:
                    source_totals[source] = 0
                source_totals[source] += value

        renewable_averages = {src: total / len(hourly_data) for src, total in source_totals.items()}

    return top_5_hours, renewable_averages

# Route for the main page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        api_key = request.form.get('api_key')

        data = fetch_power_data(latitude, longitude, api_key)

        if 'error' in data:
            return render_template('index.html', error=data['error'])

        top_5_hours, renewable_averages = process_power_data(data)

        # Generate pie chart for average production per source
        labels = renewable_averages.keys()
        values = renewable_averages.values()

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')

        pie_chart = BytesIO()
        plt.savefig(pie_chart, format='png')
        pie_chart.seek(0)
        pie_chart_url = base64.b64encode(pie_chart.getvalue()).decode('utf-8')
        
        print(f"Pie Chart URL: {pie_chart_url[:50]}...")  # Print first 50 characters of the base64 string


        return render_template('index.html', top_5_hours=top_5_hours, pie_chart_url=pie_chart_url)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)