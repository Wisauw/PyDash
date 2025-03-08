from sqlalchemy import Column, Integer, Float, String, DateTime, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

from backend.config import settings

Base = declarative_base()

class Sensor(Base):
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, unique=True, index=True)
    name = Column(String)
    location = Column(String)
    sensor_type = Column(String)
    readings = relationship("SensorReading", back_populates="sensor")

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, ForeignKey("sensors.sensor_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    value = Column(Float)
    unit = Column(String)
    sensor = relationship("Sensor", back_populates="readings")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, ForeignKey("sensors.sensor_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    value = Column(Float)
    threshold = Column(Float)
    message = Column(String)
    was_notified = Column(Integer, default=0)  # 0: not sent, 1: sent

# Database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)