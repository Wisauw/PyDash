import json
import paho.mqtt.client as mqtt
from datetime import datetime

from backend.config import settings
from backend.data_processor import process_sensor_data

#not fully implemented

# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to topic
    client.subscribe(settings.MQTT_TOPIC)

# Callback when a message is received from the server
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        
        # Extract topic parts (e.g., "sensors/temperature/living_room")
        topic_parts = msg.topic.split('/')
        if len(topic_parts) >= 3:
            sensor_type = topic_parts[1]
            location = topic_parts[2]
            
            # Create sensor data object
            sensor_data = {
                "sensor_id": f"{sensor_type}_{location}",
                "name": f"{sensor_type.capitalize()} Sensor",
                "location": location.replace('_', ' ').title(),
                "sensor_type": sensor_type,
                "value": float(payload.get("value", 0)),
                "unit": payload.get("unit", ""),
                "timestamp": datetime.utcnow()
            }
            
            # Process and store the data
            process_sensor_data(sensor_data)
            
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def start_mqtt_client():
    """
    Start the MQTT client.
    Returns the client object if successful, or raises an exception if connection fails.
    """
    try:
        client = mqtt.Client(client_id=settings.MQTT_CLIENT_ID)
        client.on_connect = on_connect
        client.on_message = on_message
        
        # Set a timeout for the connection attempt
        client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 5)
        
        # Start the loop in a non-blocking way
        client.loop_start()
        return client
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        raise