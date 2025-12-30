import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import os

class DocumentClassifier:
    def __init__(self):
        self.categories = ['Facture', 'Contrat', 'CV', 'Lettre', 'Autre']
        self.keywords = {
            'Facture': ['tva', 'facture', 'total', 'montant', 'prix', 'payé', 'commande', 'invoice', 'billing'],
            'Contrat': ['article', 'contrat', 'accord', 'signé', 'clauses', 'engagement', 'durée', 'contract'],
            'CV': ['expérience', 'formation', 'compétences', 'diplôme', 'curriculum', 'projet', 'langues', 'cv', 'resume'],
            'Lettre': ['madame', 'monsieur', 'objet', 'cordialement', 'lettre', 'destinataire', 'expéditeur']
        }
        self.model_path = 'models/classifier_model.pkl'
        self.vectorizer_path = 'models/vectorizer.pkl'
        self.model = None
        self.vectorizer = None
        
        # Load model if exists, otherwise we use keyword logic as fallback
        self._load_models()

    def _load_models(self):
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)

    def preprocess_text(self, text):
        if not text:
            return ""
        text = text.lower()
        # Remove punctuation
        text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', text)
        # Remove numbers
        text = re.sub(r'\d+', ' ', text)
        # Tokenize (simple split)
        return " ".join(text.split())

    def classify(self, text):
        clean_text = self.preprocess_text(text)
        
        # If we have a trained model, use it
        if self.model and self.vectorizer:
            features = self.vectorizer.transform([clean_text])
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            confidence = max(probabilities)
            return prediction, confidence

        # Fallback to keyword-based classification
        scores = {cat: 0 for cat in self.categories}
        total_matches = 0
        
        for cat, keys in self.keywords.items():
            for key in keys:
                count = clean_text.count(key)
                scores[cat] += count
                total_matches += count
        
        if total_matches == 0:
            return 'Autre', 0.5
        
        best_cat = max(scores, key=scores.get)
        confidence = scores[best_cat] / total_matches if total_matches > 0 else 0.5
        return best_cat, round(confidence, 2)

    def train_simple(self, data_list):
        """
        data_list: list of tuples (text, category)
        """
        if not data_list:
            return
        
        texts = [self.preprocess_text(t[0]) for t in data_list]
        labels = [t[1] for t in data_list]
        
        self.vectorizer = TfidfVectorizer()
        x = self.vectorizer.fit_transform(texts)
        self.model = MultinomialNB()
        self.model.fit(x, labels)
        
        # Save models
        os.makedirs('models', exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)

classifier = DocumentClassifier()
