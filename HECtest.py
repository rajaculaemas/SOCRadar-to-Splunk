import requests

# Konfigurasi Splunk HEC
SPLUNK_HEC_URL = "http://<Splunk IP/Domain>:8088/services/collector"
SPLUNK_HEC_TOKEN = "<Splunk HEC Token>"

# Payload JSON
payload = {
    "event": "test event"
}

# Header
headers = {
    "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
    "Content-Type": "application/json"
}

# Kirim request ke Splunk
response = requests.post(SPLUNK_HEC_URL, headers=headers, json=payload)

# Cek respons Splunk
print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text}")
