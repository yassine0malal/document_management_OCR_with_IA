import os
import pickle
import logging

class MLDocumentClassifier:
    def __init__(self, model_path="backend/models/classifier.joblib"):
        self.model_path = model_path
        self.model = None
        
        # Rule-based fallback as a safeguard (EXTENDED V5 - 10 CATEGORIES)
        self.fallback_categories = {
            "FACTURE": [
                "facture", "invoice", "montant", "tva", "total", "prix", "paiement", 
                "solde", "euro", "chèque", "virement", "iban", "bic", "fournisseur", 
                "client", "numéro de facture", "date d'échéance"
            ],
            "RECU": [
                "reçu", "ticket de caisse", "commerce", "marché", "achat", "cb", 
                "monnaie", "carte bancaire", "rendu", "article", "boutique", "vendeur"
            ],
            "CONTRAT": [
                "contrat", "accord", "signature", "partie", "article", "engagement",
                "termes", "conditions", "résiliation", "clause", "avenant",
                "ci-après dénommé", "fait à", "lu et approuvé"
            ],
            "BON_COMMANDE": [
                "bon de commande", "bon de livraison", "expédition", "livraison", 
                "quantité", "produits", "référence", "destinataire", "colis", "transporteur"
            ],
            "ADMINISTRATIF": [
                "attestation", "certificat", "autorisation", "préfecture", "mairie",
                "organisme", "déclaration", "justificatif", "officiel", "administratif"
            ],
            "RAPPORT": [
                "rapport", "compte-rendu", "analyse", "résultats", "conclusion",
                "technique", "annuel", "rapport de stage", "synthèse", "projet"
            ],
            "CV_LETTRE": [
                "cv", "curriculum vitae", "formation", "expérience", "compétences",
                "études", "langues", "loisirs", "parcours", "diplôme", "écoles",
                "lettre de motivation", "candidature", "poste"
            ],
            "ACADEMIQUE": [
                "examen", "mémoire", "thèse", "article scientifique", "recherche",
                "université", "faculté", "étudiant", "académique", "publication", "cours"
            ],
            "JURIDIQUE": [
                "jugement", "acte notarié", "procès-verbal", "avocat", "tribunal",
                "huissier", "juridique", "loi", "code civil", "décret", "ordonnance"
            ],
            "AUTRE": []
        }
        
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logging.info(f"Modèle ML chargé avec succès")
            except Exception as e:
                self.model = None

    def classify(self, text):
        text_lower = text.lower()
        
        # 1. Try ML Model
        if self.model:
            try:
                prediction = self.model.predict([text_lower])[0]
                try:
                    probs = self.model.predict_proba([text_lower])[0]
                    confidence = float(max(probs))
                except:
                    confidence = 0.95
                if confidence > 0.6:
                    return prediction, confidence
            except:
                pass

        # 2. Fallback to Rule-based (Weighted Hits)
        scores = {cat: 0 for cat in self.fallback_categories}
        for cat, keywords in self.fallback_categories.items():
            for kw in keywords:
                scores[cat] += text_lower.count(kw.lower()) * (2 if len(kw) > 5 else 1)
        
        best_cat = max(scores, key=scores.get)
        
        if scores[best_cat] == 0:
            return "AUTRE", 0.3
            
        total_hits = sum(scores.values())
        confidence = min(scores[best_cat] / total_hits if total_hits > 0 else 0.5, 0.85)
        
        return best_cat, confidence

classifier_service = MLDocumentClassifier()
