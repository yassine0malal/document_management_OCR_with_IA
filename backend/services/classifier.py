class DocumentClassifier:
    def __init__(self):
        # Basic rule-based classification as a placeholder for ML
        self.categories = {
            "FACTURE": ["facture", "invoice", "montant", "tva", "total"],
            "CONTRAT": ["contrat", "accord", "signature", "partie", "article"],
            "ID": ["identite", "passeport", "nationalite", "naissance"]
        }

    def classify(self, text):
        text = text.lower()
        scores = {cat: 0 for cat in self.categories}
        
        for cat, keywords in self.categories.items():
            for kw in keywords:
                if kw in text:
                    scores[cat] += 1
        
        best_cat = max(scores, key=scores.get)
        if scores[best_cat] == 0:
            return "AUTRE", 0.5
            
        total = sum(scores.values())
        return best_cat, scores[best_cat] / total

classifier_service = DocumentClassifier()
