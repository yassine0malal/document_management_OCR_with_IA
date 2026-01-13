
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.services.classifier import classifier_service

def test_logic():
    print("=== Test de Logique Classifieur ===")
    
    # Cas 1: Texte vide ou non pertinent (simulant ChatGPT image)
    text_chatgpt = "Conversation with ChatGPT about python code... image generation..."
    cat, conf = classifier_service.classify(text_chatgpt)
    print(f"ChatGPT Text -> Catégorie: {cat}, Confiance: {conf:.2f}")
    assert cat == "AUTRE", "Devrait être AUTRE"
    
    # Cas 2: Facture évidente (Mots clés "TVA", "Total", "Facture")
    text_facture = "FACTURE N°12345 TOTAL TTC 100€ TVA 20% PAIEMENT PAR VIREMENT"
    cat, conf = classifier_service.classify(text_facture)
    print(f"Facture Text -> Catégorie: {cat}, Confiance: {conf:.2f}")
    assert cat == "FACTURE", "Devrait être FACTURE"
    
    # Cas 3: Contrat (Mots clés)
    text_contrat = "CONTRAT DE TRAVAIL Fait à Paris le... Signature des parties..."
    cat, conf = classifier_service.classify(text_contrat)
    print(f"Contrat Text -> Catégorie: {cat}, Confiance: {conf:.2f}")
    assert cat == "CONTRAT", "Devrait être CONTRAT"
    
    # Cas 4: Médical (Nouveau)
    text_medical = "ORDONNANCE MÉDICALE Dr. Martin - Certificat d'aptitude au travail"
    cat, conf = classifier_service.classify(text_medical)
    print(f"Medical Text -> Catégorie: {cat}, Confiance: {conf:.2f}")
    assert cat == "MEDICAL", "Devrait être MEDICAL"
    
    # Cas 5: Facture Anglaise (Nouveau)
    text_english_invoice = """
    NO. 0000354 DATE 01/01/2019
    Description Price Quantity Total
    Item 1 $100 1 $100
    Total $900
    BILLED TO PAYMENT DETAILS
    Jon Smith Due Date: 02/01/2019
    """
    cat, conf = classifier_service.classify(text_english_invoice)
    print(f"English Invoice Text -> Catégorie: {cat}, Confiance: {conf:.2f}")
    assert cat == "FACTURE", "Devrait être FACTURE"

    print("\n✅ Tous les tests logiques sont passés.")

if __name__ == "__main__":
    test_logic()
