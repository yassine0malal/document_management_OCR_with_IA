import os
import pickle
import logging

class MLDocumentClassifier:
    def __init__(self, model_path="backend/models/classifier.joblib"):
        self.model_path = model_path
        self.model = None
        
        # Rule-based fallback as a safeguard
        self.fallback_categories = {
            "FACTURE": ["facture", "invoice", "montant", "tva", "total"],
            "CONTRAT": ["contrat", "accord", "signature", "partie", "article"],
            "ID": ["identite", "passeport", "nationalite", "naissance"]
        }
        
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logging.info(f"Modèle ML chargé avec succès depuis {self.model_path}")
            except Exception as e:
                logging.error(f"Erreur lors du chargement du modèle ML : {e}")
                self.model = None
        else:
            logging.warning("Le modèle ML n'a pas été trouvé. Utilisation du mode règle (fallback).")

    def classify(self, text):
        text_lower = text.lower()
        
        # 1. Try ML Model
        if self.model:
            try:
                # Predict returns the category name
                prediction = self.model.predict([text_lower])[0]
                # Try to get probability if supported by the pipeline
                try:
                    probs = self.model.predict_proba([text_lower])[0]
                    confidence = float(max(probs))
                except:
                    confidence = 0.95 # High confidence for direct hit if prob unavailable
                
                return prediction, confidence
            except Exception as e:
                logging.error(f"Erreur lors de la classification ML : {e}")

        # 2. Fallback to Rule-based
        scores = {cat: 0 for cat in self.fallback_categories}
        for cat, keywords in self.fallback_categories.items():
            for kw in keywords:
                if kw in text_lower:
                    scores[cat] += 1
        
        best_cat = max(scores, key=scores.get)
        if scores[best_cat] == 0:
            return "AUTRE", 0.5
            
        total = sum(scores.values())
        return best_cat, scores[best_cat] / total

classifier_service = MLDocumentClassifier()
