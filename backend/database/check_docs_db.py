import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.database import db_manager
import mysql.connector

def check_structure():
    conn = db_manager.connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DESCRIBE Documents")
    cols = cursor.fetchall()
    print("Documents Columns:")
    for col in cols:
        print(f"- {col['Field']} ({col['Type']})")
    
    cursor.execute("SELECT * FROM Documents LIMIT 1")
    doc = cursor.fetchone()
    print("\nSample document:")
    print(doc)
    conn.close()

if __name__ == "__main__":
    try:
        check_structure()
    except Exception as e:
        print(f"Error: {e}")
