import logging
import sys
import os

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ajouter le dossier courant au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.classifier import classifier_service

def main():
    print("=== Lancement de l'entraînement du modèle ===")
    
    # Déterminer le chemin du CSV
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "dataset.csv")
    
    if os.path.exists(csv_path):
        print(f"Source des données : {csv_path} (CSV)")
        success = classifier_service.train_from_csv(csv_path)
    else:
        print("Source des données : uploads/training_data (Dossiers)")
        success = classifier_service.train_from_folder("uploads/training_data")
    
    if success:
        print("\n✅ Entraînement terminé avec succès !")
        print("Le nouveau modèle est sauvegardé dans backend/models/classifier.joblib")
    else:
        print("\n❌ Échec de l'entraînement.")

if __name__ == "__main__":
    main()
