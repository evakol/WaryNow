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

# ── UC6 Entities ───────────────────────────────────────────

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

# ── UC7 Entities ───────────────────────────────────────────

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

# ── UC8 Entities (Φερίτ) ──────────────────────────────────

class AlertZone(Base):
    """Ζώνη παρακολούθησης που ορίζει ο Subscriber (UC8)"""
    __tablename__ = "alert_zones"

    id = Column(Integer, primary_key=True)
    subscriber_id = Column(Integer, nullable=False)  # FK → users.id
    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    radius_km = Column(Float, nullable=False)
    is_active = Column(Integer, default=1)  # 1=ενεργή, 0=ανενεργή
    created_at = Column(DateTime, default=datetime.utcnow)
    country = Column(String)
class Notification(Base):
    """Ειδοποίηση που αποστέλλεται στον Subscriber (UC8)"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    subscriber_id = Column(Integer, nullable=False)  # FK → users.id
    conflict_id = Column(Integer, nullable=False)     # FK → conflicts.id
    zone_id = Column(Integer, nullable=False)          # FK → alert_zones.id
    message = Column(String, nullable=False)
    is_read = Column(Integer, default=0)  # 0=αδιάβαστο, 1=διαβασμένο
    created_at = Column(DateTime, default=datetime.utcnow)

# ── UC9 Entities (Φερίτ) ──────────────────────────────────

class Infrastructure(Base):
    """Κρίσιμη υποδομή κοντά σε σύγκρουση (UC9)"""
    __tablename__ = "infrastructures"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # "military" ή "civilian"
    subcategory = Column(String)  # π.χ. "Βάση", "Νοσοκομείο", "Σχολείο"
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    country = Column(String)
    status = Column(String, default="operational")  # operational/damaged/destroyed

def init_db():
    """Δημιουργία των πινάκων αν δεν υπάρχουν"""
    Base.metadata.create_all(engine)

def init_db():
    """Δημιουργία των πινάκων αν δεν υπάρχουν"""
    Base.metadata.create_all(engine)