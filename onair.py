import requests
import json
from datetime import datetime, timedelta, timezone

with open("config.json", "r") as file:
    config = json.load(file)

# API URL and Key
base_url = config.get("base_url")
api_key = config.get("oa_apikey")
company_id = config.get("oa_companyid")
company_url = "/api/v1/company/" + company_id
# Headers
headers = {"oa-apikey": api_key}

data_json = {
    "time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
    "aircrafts": [],
    "notifications": []
}

aircraft_mapping = {}

# Load airport data
airport_data_path = "data/airports_from_flight.json"
with open(airport_data_path, "r") as arpt_file:
    arpt_data = json.load(arpt_file)

def get_airport_id_by_icao(icao_code):
    airports = arpt_data.get("Airports", [])
    for airport in airports:
        if airport.get("Id") == icao_code:
            return airport.get("ICAO")
    return None  # Return None if ICAO not found

# Make the request
try:
    request_url = base_url + company_url + "/fleet"
    # print(f"Requesting: {request_url}")
    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        fleet_data = response.json().get("Content",[])

        for aircraft in fleet_data:
            data_json["aircrafts"].append({
                "TailNumber": aircraft.get("Identifier", ""),
                "AircraftId": aircraft.get("Id", ""),
                "InFlight": 1 if aircraft.get("InFlightStatus", 0) > 0 else 0
            })

            aircraft_mapping[aircraft.get("Id", "")] = aircraft.get("Identifier", "")

    else:
        print(f"Error: {response.status_code}, {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")

try:
    request_url = base_url + company_url + "/notifications"
    # print(f"Requesting: {request_url}")
    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        notifications_data = response.json()
        notifications_data = notifications_data.get("Content", [])

        # Get current UTC time and calculate 5 minutes ago (timezone-aware)
        current_time = datetime.now(timezone.utc)
        five_minutes_ago = current_time - timedelta(minutes=600)

        for notification in notifications_data:
            notification_time = notification.get("ZuluEventTime")

            if notification_time:
                try:
                    # Attempt to parse time with milliseconds
                    event_time = datetime.strptime(notification_time, "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
                except ValueError:
                    # Fallback for time without milliseconds
                    event_time = datetime.strptime(notification_time, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
                
                if event_time >= five_minutes_ago:
                    # Convert aircraft id to tail-number
                    aircraft = notification.get("AircraftId", "")
                    airport = notification.get("AirportId", "")
                    for aircraft_id, tail_number in aircraft_mapping.items():
                        aircraft = aircraft.replace(aircraft_id, tail_number)

                    notification_entry = {
                        "Id": notification.get("Id", ""),
                        "Time": notification_time,
                        "Notification": notification.get("Description")
                    }

                    if aircraft:
                        notification_entry["Aircraft"] = aircraft

                    if airport:
                        notification_entry["Airport"] = get_airport_id_by_icao(airport)

                    data_json["notifications"].append(notification_entry)
    else:
        print(f"Error: Received status code {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")

json_output = json.dumps(data_json, indent=2)
print(json_output)  # Print to console