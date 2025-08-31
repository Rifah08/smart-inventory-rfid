Purpose: Simulates an RFID scanner for demo purposes.

import requests
import time
API_URL = "http://localhost:5000/api"
def simulate_scan():
    while True:
        time.sleep(5) # Scan every 5 seconds
        requests.post(API_URL + '/scan', json={'tag_id': 'TAG002', 'action': 'remove'})
        print("Scanned Pen and removed one!")
simulate_scan()
