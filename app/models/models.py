# app/models/models.py
# Ορισμός των κλάσεων της βάσης δεδομένων
# Αντιστοιχούν ακριβώς στις entities του Domain Model

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
import config

Base = declarative_base()
engine = create_engine(config.DATABASE_URL)
Session = sessionmaker(bind=engine)

class NewsSource(Base):
    """Πηγές από τις οποίες αντλούμε δεδομένα (UC6)"""
    __tablename__ = "news_sources"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    is_active = Column(Integer, default=1)  # 1=ενεργή, 0=ανενεργή

class RawReport(Base):
    """Ακατέργαστες αναφορές που αποθηκεύει το UC6"""
    __tablename__ = "raw_reports"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    source = Column(String)
    status = Column(Enum("pending", "processed", "flagged"),
        default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class Conflict(Base):
    """Κεντρική εγγραφή σύγκρουσης - ενημερώνεται από UC7"""
    __tablename__ = "conflicts"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow)

class Coordinate(Base):
    """Γεωγραφικές συντεταγμένες κάθε Conflict (UC7)"""
    __tablename__ = "coordinates"

    id = Column(Integer, primary_key=True)
    conflict_id = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

class ErrorLog(Base):
    """Καταγραφή σφαλμάτων API - εναλλακτική ροή UC6"""
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True)
    source = Column(String)
    error_message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Δημιουργία των πινάκων αν δεν υπάρχουν"""
    Base.metadata.create_all(engine)