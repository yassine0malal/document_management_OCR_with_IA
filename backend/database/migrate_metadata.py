import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.database import db_manager

def migrate():
    print("Starting migration...")
    try:
        # Add taille column (in bytes)
        db_manager.execute_query("ALTER TABLE Documents ADD COLUMN taille INT AFTER nom_fichier")
        print("Column 'taille' added successfully.")
        
        # Add type_mime column
        db_manager.execute_query("ALTER TABLE Documents ADD COLUMN type_mime VARCHAR(50) AFTER taille")
        print("Column 'type_mime' added successfully.")
        
        print("Migration completed successfully.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
