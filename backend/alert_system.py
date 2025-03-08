from datetime import datetime, timedelta

from backend.config import settings
from backend.database import Alert

def check_alert_conditions(db, sensor_data):
    """Check if the sensor reading exceeds defined thresholds"""
    sensor_type = sensor_data["sensor_type"]
    value = sensor_data["value"]
    
    # Define threshold 
    if sensor_type == "temperature":
        if value < settings.TEMPERATURE_MIN:
            create_alert(db, sensor_data, settings.TEMPERATURE_MIN, 
                        f"Low temperature alert: {value}°C is below threshold of {settings.TEMPERATURE_MIN}°C")
        elif value > settings.TEMPERATURE_MAX:
            create_alert(db, sensor_data, settings.TEMPERATURE_MAX,
                        f"High temperature alert: {value}°C is above threshold of {settings.TEMPERATURE_MAX}°C")
    
    elif sensor_type == "humidity":
        if value < settings.HUMIDITY_MIN:
            create_alert(db, sensor_data, settings.HUMIDITY_MIN,
                        f"Low humidity alert: {value}% is below threshold of {settings.HUMIDITY_MIN}%")
        elif value > settings.HUMIDITY_MAX:
            create_alert(db, sensor_data, settings.HUMIDITY_MAX,
                        f"High humidity alert: {value}% is above threshold of {settings.HUMIDITY_MAX}%")
    
    # aadd more sensors later

def create_alert(db, sensor_data, threshold, message):
    """Create an alert record and send notifications if needed"""
    # Check if a similar alert was created recently to avoid alert flooding
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_alert = db.query(Alert).filter(
        Alert.sensor_id == sensor_data["sensor_id"],
        Alert.timestamp > one_hour_ago
    ).first()
    
    if not recent_alert:
        alert = Alert(
            sensor_id=sensor_data["sensor_id"],
            timestamp=datetime.utcnow(),
            value=sensor_data["value"],
            threshold=threshold,
            message=message,
            was_notified=0
        )
        db.add(alert)
        db.commit()
        
        # descomentar para uso real
        # send_notifications(alert)
        
        # Update alert as notified
        alert.was_notified = 1
        db.commit()

def send_notifications(alert):
    """
    Send notifications via Telegram and Email (placeholder)
    This is disabled for initial setup to avoid dependencies
    """
    message = f"""
    ALERT: {alert.message}
    Sensor: {alert.sensor_id}
    Time: {alert.timestamp}
    Value: {alert.value}
    """
    
    print(f"NOTIFICATION WOULD BE SENT: {message}")
