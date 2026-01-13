
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.services.classifier import classifier_service

def test_cv_logic():
    print("=== Test Confusion CV vs Facture ===")
    
    # Simulation d'un CV qui contient des mots pièges
    # "Client" (gestion client), "Total" (total implication), "Prix" (prix d'excellence)
    text_cv_piege = """
    PROFIL PROFESSIONNEL
    Expérience en gestion de la relation client.
    Responsable du total des ventes du secteur.
    Prix d'excellence 2024.
    
    EXPERIENCES PROFESSIONNELLES
    Vendeuse Polyvalente
    Accueil des clients, conseil.
    
    FORMATION
    Licence en Gestion.
    
    CENTRES D'INTÉRÊT
    Football, Lecture.
    """
    
    cat, conf = classifier_service.classify(text_cv_piege)
    print(f"CV Piège Text -> Catégorie: {cat}, Confiance: {conf:.2f}")
    
    # On veut que ce soit CV_LETTRE (ou à la limite AUTRE), mais SURTOUT PAS FACTURE
    assert cat == "CV_LETTRE", f"Erreur: Classé comme {cat} au lieu de CV_LETTRE"
    
    print("\n✅ Le CV n'est plus confondu avec une Facture.")

if __name__ == "__main__":
    test_cv_logic()
