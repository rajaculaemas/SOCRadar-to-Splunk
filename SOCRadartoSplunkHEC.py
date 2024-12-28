from datetime import datetime, timedelta
import pytz
import requests
import time
import json

# Konfigurasi API dan Splunk HEC
API_URL = "<your API URL From SOCRadar>"
SPLUNK_HEC_URL = "http://<Splunk IP/Domain>:8088/services/collector"
SPLUNK_HEC_TOKEN = "<Splunk HEC Token>"
API_KEY = "SOCRadar API Key"

# Simpan data terakhir yang ditarik dari API lalu dikirim ke splunk
last_processed_ids = set()

# Mendapatkan tanggal terbaru gais
def get_dynamic_dates():
    utc_now = datetime.now(pytz.utc)  # Waktu saat ini dalam UTC yang aware terhadap zona waktu
    start_date = datetime(2024, 1, 1, tzinfo=pytz.utc)  # Set awal waktu manual (aktifkan ini untuk mengambil data pertama kali)
#   start_date = utc_now - timedelta(minutes=5)  # Data dari 5 menit terakhir
    end_date = utc_now
    return start_date.strftime('%Y-%m-%dT%H:%M:%S'), end_date.strftime('%Y-%m-%dT%H:%M:%S')

# send data ke Splunk via HEC
def send_to_splunk(item):
    payload = {
        "event": item,
        "sourcetype": "<your specific sourcetype in splunk>",
        "index": "<your specific index in splunk>"
    }
    headers = {"Authorization": f"Splunk {SPLUNK_HEC_TOKEN}"}
    response = requests.post(SPLUNK_HEC_URL, headers=headers, json=payload, verify=False)
    if response.status_code == 200:
        print("Data sent to Splunk successfully!")
    else:
        print(f"Failed to send to Splunk: {response.text}")

# tarik dan proses data
def fetch_and_process_data():
    global last_processed_ids

    # Hitung tanggal dinamis
    start_date, end_date = get_dynamic_dates()
    # Ini adalah parameter bersifat optional
    params = {
        'key': API_KEY,
        'start_date': start_date,
        'end_date': end_date,
        'leak_type': '<choose leak type>'
    }

    print(f"Fetching data from {start_date} to {end_date}...")

    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        print("API response received.")

        if 'data' in data and isinstance(data['data'], list):
            for item in data['data']:
                event_id = item.get("id")  # Gunakan ID unik
                if event_id and event_id not in last_processed_ids:
                    print(f"New data found: {item}")
                    send_to_splunk(item)  # Kirim data baru ke Splunk via HEC
                    last_processed_ids.add(event_id)
        else:
            print("No valid data found in the API response.")
    else:
        print(f"Error fetching data: {response.status_code} - {response.text}")

# running secara berkala
def run_periodically(interval=300):  # Default dibikin: 300 detik = 5 menit
    while True:
        fetch_and_process_data()
        time.sleep(interval)

# Mulai program
if __name__ == "__main__":
    run_periodically(interval=300)  # Request setiap 5 menit
