import requests

def fetch_power_breakdown(latitude, longitude):
    url = "https://api.electricitymap.org/v3/power-breakdown/history"
    headers = {"auth-token": "0WZOCxfi4Tbx3"}
    params = {"lat": latitude, "lon": longitude}

    try:
        # Make the GET request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        # Parse the response
        data = response.json()

        # Extract historical data
        historical_data = data.get("history", [])
        if not historical_data:
            print("No historical data available.")
            return

        # Initialize variables for computation
        total_production_by_source = {}
        renewable_percentages = []

        # Process historical data
        for entry in historical_data:
            datetime = entry.get("datetime")
            production = entry.get("powerProductionBreakdown", {})
            if not production:
                continue

            # Sum production by source and calculate total production
            total_production = 0
            renewable_production = 0
            for source, value in production.items():
                if value is not None:
                    total_production += value
                    total_production_by_source[source] = (
                        total_production_by_source.get(source, 0) + value
                    )
                    if source in ["wind", "solar", "hydro"]:
                        renewable_production += value

            if total_production > 0:
                renewable_percentage = (renewable_production / total_production) * 100
                renewable_percentages.append((datetime, renewable_percentage))

        # Sort by renewable percentage in descending order
        renewable_percentages.sort(key=lambda x: x[1], reverse=True)

        # Get the top 5 hours
        top_5_renewable_hours = renewable_percentages[:5]

        print("\nTop 5 Hours with Highest Renewable Power Percentage:")
        for datetime, percentage in top_5_renewable_hours:
            print(f"- {datetime}: {percentage:.2f}% renewable")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")


def main():
    # Input latitude and longitude from the user
    try:
        latitude = float(input("Enter latitude: "))
        longitude = float(input("Enter longitude: "))

        fetch_power_breakdown(latitude, longitude, "0WZOCxfi4Tbx3")
    except ValueError:
        print("Invalid input. Please enter numeric values for latitude and longitude.")

if __name__ == "__main__":
    main()
