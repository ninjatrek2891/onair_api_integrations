import requests
import csv
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

# Headers
headers = {"oa-apikey": api_key}

airports_json = {
    "CreationTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
    "Airports": []
}


# GitHub URL for the CSV
csv_url = config.get("csv_url")
csv_file = config.get("csv_file")

local = config.get("use_local")

# Fetch the CSV content
if local == True:
    with open(csv_file, "r") as file:
        csv_content = file.read()
else:
    response = requests.get(csv_url)
    

    if response.status_code == 200:
        csv_content = response.text
    else:
        print(f"Failed to fetch the CSV file: {response.status_code}")
        exit()

airports_total = len(csv_content.splitlines())-1
count=1
for index, row in enumerate(csv.DictReader(csv_content.splitlines()), start=1):
    gps_code = row.get("gps_code")
    airport_type = row.get("type")
    if gps_code:  # Skip empty ICAO codes
        if not airport_type in ("heliport", "closed"):
            # First get the airport data from OnAir
            print(f"({index}/{airports_total})\tRequesting {gps_code} from OnAir", end="\t\t")
            request_url = base_url + "/api/v1/airports/" + gps_code
            response = requests.get(request_url, headers=headers)
            if response.status_code == 200:
                airport_data = response.json().get("Content",[])
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
                print(f"{response.status_code}")
            
            count = count+1
            # if count % 100 == 0:
                # print("Pausing for 2 seconds\n")
                # time.sleep(2)

    
# Save to JSON
os.makedirs("data", exist_ok=True)
output_file = "data/airports.json"
with open(output_file, "w") as file:
    json.dump(airports_json, file)