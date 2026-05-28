# app/services/uc6_service.py
# Υλοποίηση του UC6 - Fetch Conflict Data
# Controls: SchedulerController, APIConnector, KeywordFilter, DataNormalizer

import requests
from datetime import datetime
from app.models.models import NewsSource, RawReport, ErrorLog, Session
import config

# KeywordFilter 
def filter_keywords(results):
    """
    Φιλτράρει τα αποτελέσματα βάσει conflict keywords.
    ALT-B: αν δεν βρεθεί κανένα match επιστρέφει κενή λίστα.
    """
    filtered = []
    for item in results:
        text = (item.get("title", "") + " " + 
                item.get("description", "")).lower()
        if any(kw in text for kw in config.CONFLICT_KEYWORDS):
            filtered.append(item)
    return filtered

# DataNormalizer 
def normalize_and_save(items, source_name):
    """
    Κανονικοποιεί τα δεδομένα και τα αποθηκεύει ως RawReport.
    """
    session = Session()
    try:
        for item in items:
            report = RawReport(
                title=item.get("title", "No title"),
                description=item.get("description", ""),
                location=item.get("location", ""),
                latitude=item.get("latitude"),
                longitude=item.get("longitude"),
                source=source_name,
                status="pending",
                created_at=datetime.utcnow()
            )
            session.add(report)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# APIConnector
def fetch_data(source):
    """
    Κάνει HTTP request στο GDELT API για μια NewsSource.
    ALT-A: αν αποτύχει καταγράφει στο ErrorLog και συνεχίζει.
    """
    session = Session()
    try:
        params = {
            "query": "conflict war attack",
            "mode": "artlist",
            "maxrecords": 10,
            "format": "json"
        }
        response = requests.get(
            config.GDELT_API_URL, 
            params=params, 
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # Εξαγωγή άρθρων από GDELT response
        articles = data.get("articles", [])
        
        # Φιλτράρισμα keywords
        filtered = filter_keywords(articles)
        
        # ALT-B: κανένα match
        if not filtered:
            return
        
        # Αποθήκευση
        normalize_and_save(filtered, source.name)

    except Exception as e:
        # ALT-A: καταγραφή σφάλματος
        log = ErrorLog(
            source=source.name,
            error_message=str(e),
            created_at=datetime.utcnow()
        )
        session.add(log)
        session.commit()
    finally:
        session.close()

#  SchedulerController 
def activate():
    """
    Κεντρική μέθοδος UC6. Διαβάζει τις ενεργές NewsSource
    και καλεί τον APIConnector για κάθε μία.
    """
    session = Session()
    try:
        sources = session.query(NewsSource).filter_by(
            is_active=1
        ).all()
        
        for source in sources:
            fetch_data(source)
    finally:
        session.close()