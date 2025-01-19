import requests
import json
import os
from datetime import datetime, timedelta, timezone

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

with open("config.json", "r") as file:
    config = json.load(file)

# API URL and Key
base_url = config.get("base_url")
api_key = config.get("oa_apikey")
company_id = config.get("oa_companyid")
company_url = "/api/v1/company/" + company_id
# Headers
headers = {"oa-apikey": api_key}

airports_json = {
    "CreationTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
    "Airports": []
}

work_json = []
try:
    request_url = base_url + company_url + "/flights"
    # print(f"Requesting: {request_url}")
    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        flights_data = response.json().get("Content",[])
    
        for row in flights_data:
            for setting in ["DepartureAirport","ArrivalIntendedAirport", "ArrivalActualAirport"]:
                CurrentAirport = row.get(setting, {}).get("ICAO", "")
                if CurrentAirport:
                    if CurrentAirport and not any(entry.get("ICAO") == CurrentAirport for entry in work_json):
                        work_json.append({"ICAO": CurrentAirport})
                        airport_url = base_url + "/api/v1/airports/" + CurrentAirport
                        airport_resp = requests.get(airport_url, headers=headers)
                        print(f"(Requesting {CurrentAirport} from OnAir", end="\t\t")
                        if airport_resp.status_code == 200:
                            airport_data = airport_resp.json().get("Content",[])
                            if airport_data:
                                airport_entry = {
                                    "Id": airport_data.get("Id", ""),
                                    "ICAO": airport_data.get("ICAO", ""),
                                    "IATA": airport_data.get("IATA", ""),
                                    "Name": airport_data.get("Name", ""),
                                    "CountryCode": airport_data.get("CountryCode", ""),
                                    "CountryName": airport_data.get("CountryName", ""),
                                    "City": airport_data.get("City", ""),
                                    "DisplayName": airport_data.get("DisplayName", ""),
                                    "IsMilitary": airport_data.get("IsMilitary", "")
                                }

                                airports_json["Airports"].append(airport_entry)
                                print(f"{GREEN}DONE{RESET}")
                            else:
                                print(f"{RED}NOT PRESENT{RESET}")

    else:
        print(f"Error: {response.status_code}, {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")

# Save to JSON
os.makedirs("data", exist_ok=True)
output_file = "data/airports_from_flight.json"
with open(output_file, "w") as file:
    json.dump(airports_json, file, indent=2)