# config.py
# Κεντρικές σταθερές και ρυθμίσεις της εφαρμογής

# Βάση δεδομένων
DATABASE_URL = "sqlite:///warynow.db"

# Κατώφλια γεωγραφικής εγγύτητας για UC7
MERGE_THRESHOLD_KM = 50      # Κάτω από 50km → merge
BORDERLINE_THRESHOLD_KM = 100  # 50-100km → pending

# Λέξεις-κλειδιά για φιλτράρισμα ειδήσεων (UC6)
CONFLICT_KEYWORDS = [
    "war", "attack", "conflict", "explosion",
    "military", "strike", "battle", "shooting"
]

# Scheduler - κάθε πόσα λεπτά τρέχει το UC6
SCHEDULER_INTERVAL_MINUTES = 30

# GDELT API
GDELT_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"