# main.py
# Κεντρικό αρχείο εκκίνησης της εφαρμογής
# Συνδέει UC6 → UC7 και εκκινεί τον Scheduler

from apscheduler.schedulers.blocking import BlockingScheduler
from app.models.models import init_db
from app.services.uc6_service import activate
from app.services.uc7_service import start_merging
import config

def run_pipeline():
    """
    Εκτελεί UC6 και UC7 διαδοχικά.
    UC6: Ανάκτηση δεδομένων → UC7: Merging
    """
    print(f"[UC6] Έναρξη ανάκτησης δεδομένων...")
    activate()
    print(f"[UC6] Ολοκληρώθηκε.")

    print(f"[UC7] Έναρξη conflict merging...")
    start_merging()
    print(f"[UC7] Ολοκληρώθηκε.")

if __name__ == "__main__":
    # Δημιουργία βάσης αν δεν υπάρχει
    init_db()
    print("Βάση δεδομένων έτοιμη.")

    # Εκκίνηση scheduler
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_pipeline,
        "interval",
        minutes=config.SCHEDULER_INTERVAL_MINUTES
    )

    print(f"Scheduler ενεργός - τρέχει κάθε "
          f"{config.SCHEDULER_INTERVAL_MINUTES} λεπτά.")
    
    # Τρέξε μία φορά αμέσως
    run_pipeline()
    scheduler.start()