"""
Simple sensor simulator to generate test data for the IoT Dashboard
"""
import requests
import random
import time
from datetime import datetime
import json

# Configuration
API_URL = "http://localhost:8000/api/sensors/data"
SEND_INTERVAL = 2  # seconds between readings

# Sensor definitions
SENSORS = [
    {"id": "temperature_living_room", "type": "temperature", "unit": "°C", "min": 18, "max": 32},
    {"id": "temperature_bedroom", "type": "temperature", "unit": "°C", "min": 18, "max": 25},
    {"id": "humidity_living_room", "type": "humidity", "unit": "%", "min": 30, "max": 90},
    {"id": "humidity_bedroom", "type": "humidity", "unit": "%", "min": 35, "max": 75}
]

def generate_reading(sensor):
    """Generate a random sensor reading within the defined range"""
    return round(random.uniform(sensor["min"], sensor["max"]), 2)

def send_data(sensor_id, value, unit):
    """Send data to the API endpoint"""
    data = {
        "sensor_id": sensor_id,
        "value": value,
        "unit": unit
    }
    
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Sent {sensor_id}: {value} {unit}")
            return True
        else:
            print(f"❌ Failed to send data: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending data: {e}")
        return False

def main():
    """Main simulation loop"""
    print("🔌 IoT Sensor Simulator")
    print(f"🔄 Sending data every {SEND_INTERVAL} seconds to {API_URL}")
    print("Press Ctrl+C to stop")
    print("-------------------")
    
    try:
        while True:
            # Check if API is available by sending a status request
            try:
                status_response = requests.get("http://localhost:8000/api/status")
                if status_response.status_code != 200:
                    print("⚠️ API not responding correctly. Waiting...")
                    time.sleep(5)
                    continue
            except Exception:
                print("⚠️ API not available. Waiting...")
                time.sleep(5)
                continue
            
            # Generate and send readings for each sensor
            for sensor in SENSORS:
                value = generate_reading(sensor)
                send_data(sensor["id"], value, sensor["unit"])
                time.sleep(0.5)  # Short delay between sensors
            
            # Occasionally send an anomaly
            if random.random() < 0.1:  # 10% chance per cycle
                # Choose a random sensor
                sensor = random.choice(SENSORS)
                
                # Generate an anomalous value (either too high or too low)
                if random.choice([True, False]):
                    # High value
                    value = round(sensor["max"] + random.uniform(2, 10), 2)
                else:
                    # Low value
                    value = round(sensor["min"] - random.uniform(2, 10), 2)
                
                print(f"⚠️ Sending ANOMALY for {sensor['id']}: {value} {sensor['unit']}")
                send_data(sensor["id"], value, sensor["unit"])
            
            time.sleep(SEND_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n✋ Simulator stopped")

if __name__ == "__main__":
    main()