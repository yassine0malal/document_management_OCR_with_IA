from backend.database import db_manager
try:
    res = db_manager.execute_query("DESCRIBE Utilisateurs")
    print("Utilisateurs table:")
    for row in res:
        print(row)
    
    res = db_manager.execute_query("SELECT * FROM Utilisateurs LIMIT 1")
    print("\nSample user:")
    print(res)
except Exception as e:
    print(f"Error: {e}")
