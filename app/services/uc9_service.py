from app.models.models import get_connection

def filter_by_category(category):
    conn = get_connection()
    cursor = conn.cursor()
    
    if category == "Όλες":
        cursor.execute("SELECT id, name, category, subcategory, status FROM infrastructures")
    else:
        # Μετατροπή των επιλογών του UI στα αγγλικά categories της βάσης
        db_cat = "military" if category == "Στρατιωτικές" else "civilian"
        cursor.execute("SELECT id, name, category, subcategory, status FROM infrastructures WHERE category = ?", (db_cat,))
        
    rows = cursor.fetchall()
    conn.close()
    
    class InfrastructureItem:
        def __init__(self, r):
            self.id, self.name, self.category_en, self.subcategory, self.status = r
            self.category = "Στρατιωτική" if self.category_en == "military" else "Πολιτική"
            
    return [InfrastructureItem(row) for row in rows]