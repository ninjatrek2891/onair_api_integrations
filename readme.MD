
# OnAir Data Integration Project

This project integrates with the **OnAir Company API** to collect, process, and store data related to your company in OnAir. It focuses on fetching data about aircraft, airports, and notifications to help manage operations efficiently.

---

## Features

- **Aircraft Data Collection**: Fetch detailed aircraft information, including tail numbers, IDs, and flight statuses for your OnAir company.
- **Airport Data Handling**: Retrieve and store airport details based on ICAO codes, with options to filter out irrelevant types (e.g., heliports or closed airports).
- **Notifications Management**: Process and log notifications such as job completions, fuel deliveries, and work order statuses specific to your company.
- **Efficient Storage**: Data is structured and stored in JSON format for flexibility and compatibility with future integrations.
- **Batch Processing**: Ensures API calls are handled in manageable batches to avoid overloading the server.

---

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ninjatrek2891/onair-integration.git
   cd onair-integration
   ```

2. Create and configure `config.json`:
   - The `config.json` file stores essential configuration values:
     ```json
     {
         "base_url": "https://server1.onair.company",
         "oa_apikey": "your_api_key_here",
         "company_id": "your_company_id_here",
         "csv_url": "https://raw.githubusercontent.com/datasets/airport-codes/main/data/airport-codes.csv",
         "csv_file": "data/airport.csv",
         "use_local": true
     }
     ```
   - **Key Notes**:
     - Replace `your_api_key_here` with your OnAir API key.
     - Replace `your_company_id_here` with your OnAir company ID.
     - Set `"use_local": true` to read the local file defined in `"csv_file"`, or `false` to fetch the file from the `csv_url`.
     - The airports.csv is an example. The most important thing to have in the csv file is gps_code and type.

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
    - **Key Notes**:
        - Not really needed, unless your system is whacko tight. Also I recommend using a venv.
---

## Usage

### Fetching Airport Data
To fetch and store airport details:
```bash
python airports.py
```
- This script processes ICAO codes from the CSV file or URL and stores airport data in `data/airports.json`.
- Beaware! This takes a long time and requests about 42k airports from the OnAir API. Use airports from flights instead!

### Fetching Airport Data from your Company flights
To fetch and store airport details:
```bash
python airports_from_flights.py
```
- This script processes ICAO codes from the CSV file or URL and stores airport data in `data/airports.json`.
- This runs a lot faster and uses your company flights to get the data for enrichment in the onair.py file.

### Processing Notifications
To process recent notifications:
```bash
python onair.py
```
- This script fetches notifications related to your company from the API and appends them to the JSON file for tracking.

### Updating Aircraft Data
To update the status of aircraft:
```bash
python scripts/main.py
```
- This script synchronizes aircraft data for your company from the API and enriches it with local mappings.

---

## Contributing

As this is a hobby project of mine! Use at your own risk! Let me peddle around with Python, so at this moment I won't look into pull requests or issues actively.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## Disclaimer

Because I'm too lazy to write this readme.MD, I used ChatGPT 4o to create it. And modified some stuff.