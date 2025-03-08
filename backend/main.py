from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from backend.database import get_db, init_db, Sensor as DBSensor, SensorReading as DBSensorReading, Alert as DBAlert
from backend.mqtt_client import start_mqtt_client
from backend.data_processor import process_sensor_data

# Pydantic models for API
class SensorBase(BaseModel):
    sensor_id: str
    name: str
    location: str
    sensor_type: str

    class Config:
        from_attributes = True  # This replaces orm_mode=True in Pydantic v2

class Sensor(SensorBase):
    id: int

class SensorData(BaseModel):
    sensor_id: str
    value: float
    unit: Optional[str] = ""

class SensorReadingResponse(BaseModel):
    id: int
    sensor_id: str
    timestamp: datetime
    value: float
    unit: str
    
    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: int
    sensor_id: str
    timestamp: datetime
    value: float
    threshold: float
    message: str
    
    class Config:
        from_attributes = True

# Initialize FastAPI app
app = FastAPI(title="IoT Sensor Dashboard API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start MQTT client when app starts
@app.on_event("startup")
def startup_event():
    init_db()
    global mqtt_client
    try:
        mqtt_client = start_mqtt_client()
    except Exception as e:
        print(f"Warning: Could not start MQTT client: {e}")
        print("The application will continue without MQTT support.")

# API endpoints
@app.post("/api/sensors/data")
async def add_sensor_data(data: SensorData, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Endpoint to receive sensor data via REST API"""
    sensor = db.query(DBSensor).filter(DBSensor.sensor_id == data.sensor_id).first()
    
    # Prepare full sensor data
    sensor_data = {
        "sensor_id": data.sensor_id,
        "name": sensor.name if sensor else data.sensor_id,
        "location": sensor.location if sensor else "unknown",
        "sensor_type": sensor.sensor_type if sensor else data.sensor_id.split('_')[0],
        "value": data.value,
        "unit": data.unit,
        "timestamp": datetime.utcnow()
    }
    
    # Process sensor data in the background
    background_tasks.add_task(process_sensor_data, sensor_data)
    
    return {"status": "success", "message": "Data received"}

@app.get("/api/sensors", response_model=List[Sensor])
async def get_sensors(db: Session = Depends(get_db)):
    """Get all registered sensors"""
    return db.query(DBSensor).all()

@app.get("/api/sensors/{sensor_id}/readings", response_model=List[SensorReadingResponse])
async def get_sensor_readings(
    sensor_id: str, 
    limit: int = 100, 
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get readings for a specific sensor with optional time filtering"""
    query = db.query(DBSensorReading).filter(DBSensorReading.sensor_id == sensor_id)
    
    if start_time:
        query = query.filter(DBSensorReading.timestamp >= start_time)
    if end_time:
        query = query.filter(DBSensorReading.timestamp <= end_time)
    
    return query.order_by(DBSensorReading.timestamp.desc()).limit(limit).all()

@app.get("/api/alerts", response_model=List[AlertResponse])
async def get_alerts(
    limit: int = 50,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get recent alerts"""
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    return db.query(DBAlert).filter(
        DBAlert.timestamp >= time_threshold
    ).order_by(DBAlert.timestamp.desc()).limit(limit).all()

# Add a simple status endpoint for testing
@app.get("/api/status")
async def get_status():
    """Get API status"""
    return {"status": "online", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)