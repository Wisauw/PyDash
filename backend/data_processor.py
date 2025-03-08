from sqlalchemy.orm import Session
from datetime import datetime

from backend.database import SessionLocal, Sensor, SensorReading
from backend.alert_system import check_alert_conditions

def process_sensor_data(sensor_data):
    """Process incoming sensor data and store it in the database"""
    db = SessionLocal()
    try:
        # Check if sensor exists, if not create it
        sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_data["sensor_id"]).first()
        if not sensor:
            sensor = Sensor(
                sensor_id=sensor_data["sensor_id"],
                name=sensor_data["name"],
                location=sensor_data["location"],
                sensor_type=sensor_data["sensor_type"]
            )
            db.add(sensor)
            db.commit()
            db.refresh(sensor)
        
        # Create new reading
        reading = SensorReading(
            sensor_id=sensor_data["sensor_id"],
            timestamp=sensor_data.get("timestamp", datetime.utcnow()),
            value=sensor_data["value"],
            unit=sensor_data["unit"]
        )
        db.add(reading)
        db.commit()
        
        # Check for alert conditions
        try:
            check_alert_conditions(db, sensor_data)
        except Exception as e:
            print(f"Error checking alert conditions: {e}")
        
    except Exception as e:
        db.rollback()
        print(f"Error storing sensor data: {e}")
    finally:
        db.close()