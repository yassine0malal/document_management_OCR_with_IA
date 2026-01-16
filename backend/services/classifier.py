import os
import pickle
import logging
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline




from sklearn.model_selection import train_test_split
from joblib import dump, load

class MLDocumentClassifier:
    def clean_text(self, text):
        """Nettoie le texte pour l'extraction de features."""
        if not text: return ""
        # 1. Remplacement des \n littéraux et réels par des espaces
        text = str(text).replace('\\n', ' ').replace('\n', ' ')
        # 2. Mise en minuscule
        text = text.lower()
        # 3. Suppression des caractères spéciaux
        text = re.sub(r'[^a-zA-Z0-9\sàâäéèêëîïôöùûüç]', ' ', text)
        # 4. Suppression des espaces doubles
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def __init__(self, model_path=None):
        if model_path is None:
            # Resolve path relative to this file's location
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.model_path = os.path.join(base_dir, "models", "classifier.joblib")
        else:
            self.model_path = model_path
            
        self.model = None
        
        # Extended STOP WORDS (French + English)
        self.custom_stop_words = [
            'le', 'la', 'de', 'du', 'des', 'et', 'en', 'un', 'une', 'les', 'au', 'aux',
            'pour', 'avec', 'par', 'est', 'sur', 'dans', 'the', 'and', 'for', 'with', 
            'from', 'this', 'that', 'your', 'our'
        ]
        
        # Rule-based fallback as a safeguard (EXTENDED V5 - 10 CATEGORIES)
        self.fallback_categories = {
            "FACTURE": [
                "facture", "invoice", "tva", "montant ht", "montant ttc", "net à payer", 
                "total à payer", "solde dû", "virement", "iban", "bic", 
                "numéro de facture", "date d'échéance", "siret", "siren", "intracommunautaire",
                "billed to", "due date", "amount due", "subtotal", "tax", "billing",
                "recu", "reçu", "ticket de caisse", "rendu monnaie", "total ttc", "carte bancaire", 
                "merci de votre visite", "ticket", "caisse", "receipt", "cashier", "change",
                "store", "transaction"
            ],
            # "RECU": [
            #     "recu", "reçu", "ticket de caisse", "rendu monnaie", "total ttc", "carte bancaire", 
            #     "merci de votre visite", "ticket", "caisse", "receipt", "cashier", "change",
            #     "store", "transaction"
            # ],
            "CONTRAT": [
                "contrat", "entre les soussignés", "il a été convenu", "article 1", 
                "signature", "engagement", "avenant", "résiliation", "clause",
                "fait à", "lu et approuvé", "parties", "contract", "agreement", "between",
                "signed", "witnessed", "hereby"
            ],
            "BON_COMMANDE": [
                "bon de commande", "bordereau de livraison", "référence client", 
                "adresse de livraison", "mode d'expédition", "colis", "purchase order",
                "shipping address", "delivery note", "customer reference", "package"
            ],
            "ADMINISTRATIF": [
                "attestation", "certificat", "autorisation", "préfecture", "mairie",
                "déclaration", "justificatif de domicile", "avis d'imposition",
                "certificate", "authorization", "permit", "declaration", "official"
            ],
            "RAPPORT": [
                "compte-rendu", "rapport annuel", "analyse technique", "conclusion",
                "synthèse", "projet", "sommaire", "introduction", "report", "summary",
                "analysis", "findings", "objective"
            ],
            "CV_LETTRE": [
                "curriculum vitae", "profil professionnel", "expériences professionnelles", 
                "formation", "compétences", "langues", "centres d'intérêt", "hobbies", 
                "contact", "téléphone", "email", "poste", "stage", "emploi",
                "lettre de motivation", "objets : candidature", "madame, monsieur",
                "université", "étudiant", "école", "diplôme", "alternance", "licence", "master",
                "resume", "work experience", "education", "skills", "languages", "interests",
                "internship", "job", "cover letter", "application", "dear", "sincerely"
            ],
            "ACADEMIQUE": [
                "examen", "mémoire", "thèse", "article scientifique", "recherche",
                "université", "faculté", "étudiant", "académique", "publication", "cours",
                "thesis", "dissertation", "academic", "research", "paper", "professor", "grade"
            ],
            "JURIDIQUE": [
                "jugement", "acte notarié", "procès-verbal", "avocat", "tribunal",
                "huissier", "juridique", "loi", "code civil", "décret", "ordonnance",
                "judgment", "legal", "lawyer", "court", "attorney", "summons", "affidavit"
            ],
            "DIAGRAMME": [
                "architecture", "schema", "schéma", "diagramme", "flux", "workflow",
                "backend", "frontend", "interface", "base de données", "database",
                "utilisateur", "api", "technique", "module", "diagram", "process", "system"
            ],
            "MEDICAL": [
                "certificat médical", "médecin", "docteur", "santé", "patient",
                "ordonnance", "vaccination", "vaccin", "examen périodique", 
                "aptitude", "clinique", "hôpital", "santé au travail", "medical certificate",
                "doctor", "health", "prescription", "vaccine", "clinic", "hospital"
            ],
            "AUTRE": []
        }
        
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                # IMPORTANT: Matching the save method (joblib.dump -> joblib.load)
                self.model = load(self.model_path)
                logging.info(f"Modèle ML chargé avec succès depuis {self.model_path}")
            except Exception as e:
                logging.error(f"Erreur lors du chargement du modèle {self.model_path} : {e}")
                self.model = None
        else:
            logging.warning(f"Fichier modèle non trouvé : {self.model_path}")
            self.model = None

    def train_from_csv(self, csv_path="backend/ml/dataset.csv"):
        """Entraîne le modèle à partir d'un fichier CSV pré-rempli."""
        import pandas as pd
        
        logging.info(f"Démarrage de l'entraînement depuis CSV : {csv_path}")
        if not os.path.exists(csv_path):
            logging.error(f"Fichier CSV non trouvé : {csv_path}")
            return False
            
        try:
            df = pd.read_csv(csv_path)
            # Nettoyage : Garder uniquement les classes avec au moins 2 membres
            class_counts = df['categorie'].value_counts()
            classes_to_keep = class_counts[class_counts >= 2].index
            df = df[df['categorie'].isin(classes_to_keep)]
            
            texts = [self.clean_text(str(t)) for t in df['texte'].tolist()]
            labels = df['categorie'].tolist()
            
            return self._train_from_data(texts, labels)
        except Exception as e:
            logging.error(f"Erreur lors de la lecture du CSV : {e}")
            return False

    def train_from_folder(self, data_path="uploads/training_data"):
        """Entraîne le modèle à partir des dossiers de données réelles (OCR)."""
        from .ocr import ocr_service
        import glob
        
        logging.info("Démarrage de l'entraînement par OCR des dossiers...")
        texts = []
        labels = []
        
        # Parcourir les catégories (dossiers)
        if not os.path.exists(data_path):
            logging.error(f"Dossier d'entraînement non trouvé : {data_path}")
            return False
            
        categories = [d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))]
        
        for category in categories:
            if category == "augmented": continue
            
            files = glob.glob(os.path.join(data_path, category, "*.*"))
            logging.info(f"Traitement catégorie '{category}' : {len(files)} fichiers trouvés.")
            
            for file_path in files:
                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                    
                    text, _ = ocr_service.extract_from_bytes(content, filename=os.path.basename(file_path))
                    
                    if text and len(text) > 10:
                        texts.append(text)
                        labels.append(category)
                except Exception as e:
                    logging.warning(f"Erreur lecture {file_path}: {e}")
                    
        return self._train_from_data(texts, labels)

    def _train_from_data(self, texts, labels):
        """Logique centrale du championnat de modèles."""
        if not texts or len(texts) < 5:
            logging.error("Pas assez de données pour l'entraînement.")
            return False
            
        # Division Training / Test
        X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42, stratify=labels)
        
        models = {
            "LogisticRegression": LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42),
            "RandomForest": RandomForestClassifier(n_estimators=200, random_state=42),
            "NaiveBayes": MultinomialNB(),
            "SVM (Linear)": CalibratedClassifierCV(SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, random_state=42))
        }
        
        best_score = 0
        best_model_name = ""
        best_model_obj = None
        
        print("\n--- Début du Tournoi de Modèles (V2 - Clean Data) ---")
        
        for name, model in models.items():
            pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=5000, 
                    stop_words=self.custom_stop_words,
                    ngram_range=(1, 2) # Capture phrases comme "due date"
                )),
                ('clf', model)
            ])
            
            pipeline.fit(X_train, y_train)
            score = pipeline.score(X_test, y_test)
            print(f"Modèle : {name: <15} | Précision : {score:.2%}")
            
            if score > best_score:
                best_score = score
                best_model_name = name
                best_model_obj = pipeline
        
        print("-" * 40)
        print(f"🏆 VAINQUEUR : {best_model_name} avec {best_score:.2%} de précision")
        print("-" * 40)
        
        self.model = best_model_obj
        
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        try:
            dump(self.model, self.model_path)
            logging.info(f"Modèle vainqueur ({best_model_name}) sauvegardé dans {self.model_path}")
            return True
        except Exception as e:
            logging.error(f"Erreur sauvegarde : {e}")
            return False

    def classify(self, text):
        text_clean = self.clean_text(text)
        text_lower = text_clean
        
        # 1. PRIORITÉ : Mots-clés (Approche MVP simple et efficace)
        scores = {cat: 0 for cat in self.fallback_categories}
        for cat, keywords in self.fallback_categories.items():
            for kw in keywords:
                count = text_lower.count(kw.lower())
                if count > 0:
                    # Bonus pour les mots-clés longs (> 4 chars)
                    scores[cat] += count * (2 if len(kw) > 4 else 1)
        
        best_cat_rules = max(scores, key=scores.get)
        total_hits = sum(scores.values())
        
        # Si on a des correspondances claires par mots-clés
        if total_hits >= 2:
            confidence_rules = min(scores[best_cat_rules] / total_hits, 0.95)
            if confidence_rules >= 0.5:
                logging.info(f"Règles Classifieur - OK : {best_cat_rules} ({confidence_rules:.2f})")
                return best_cat_rules, confidence_rules

        # 2. SECONDAIRE : Modèle ML (si les règles sont incertaines)
        if self.model:
            try:
                prediction = self.model.predict([text_clean])[0]
                try:
                    probs = self.model.predict_proba([text_clean])[0]
                    confidence = float(max(probs))
                except:
                    confidence = 0.85
                
                logging.info(f"ML Classifieur - Prédiction : {prediction} ({confidence:.2f})")
                
                # Si le ML est très sûr de lui, on le suit
                if confidence > 0.80:
                    return prediction, confidence
                
                # Arbitrage : si ML et Règles sont d'accord
                if prediction == best_cat_rules and total_hits > 0:
                    return prediction, max(confidence, 0.70)
                    
            except Exception as e:
                logging.warning(f"Erreur prédiction ML : {e}")

        # 3. FALLBACK FINAL
        if total_hits > 0:
            return best_cat_rules, min(scores[best_cat_rules] / total_hits, 0.80)
            
        return "AUTRE", 0.10

classifier_service = MLDocumentClassifier()
