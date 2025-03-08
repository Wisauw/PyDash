import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./iot_data.db")
    
    # MQTT settings
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_TOPIC: str = os.getenv("MQTT_TOPIC", "sensors/#")
    MQTT_CLIENT_ID: str = os.getenv("MQTT_CLIENT_ID", "iot_dashboard_client")
    
    # Alert thresholds
    TEMPERATURE_MIN: float = float(os.getenv("TEMPERATURE_MIN", "10.0"))
    TEMPERATURE_MAX: float = float(os.getenv("TEMPERATURE_MAX", "30.0"))
    HUMIDITY_MIN: float = float(os.getenv("HUMIDITY_MIN", "20.0"))
    HUMIDITY_MAX: float = float(os.getenv("HUMIDITY_MAX", "80.0"))
    
    # Notification settings
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_TO: str = os.getenv("EMAIL_TO", "")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))

settings = Settings()