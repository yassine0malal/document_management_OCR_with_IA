import os
import time
import pickle
import numpy as np
import cv2
import pytesseract
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

from synthetic_gen import SyntheticDataGenerator
from data_augmentation import DataAugmentor

# Configuration
DATA_DIR = "uploads/training_data"
MODEL_PATH = "backend/models/classifier.joblib"
SAMPLES_PER_CAT = 15
AUG_PER_SAMPLE = 5

class ModelTrainer:
    def __init__(self):
        self.generator = SyntheticDataGenerator(output_dir=DATA_DIR)
        self.augmentor = DataAugmentor(output_dir=os.path.join(DATA_DIR, "augmented"))
        self.categories = ["FACTURE", "CONTRAT", "ID"]
        
    def prepare_dataset(self):
        print("--- Étape 1 : Génération de données synthétiques (Images) ---")
        raw_files = []
        labels = []
        
        for cat in self.categories:
            print(f"Génération catégorie : {cat}...")
            for i in range(SAMPLES_PER_CAT):
                if cat == "FACTURE":
                    path = self.generator.generate_invoice_img(i)
                elif cat == "CONTRAT":
                    path = self.generator.generate_contract_img(i)
                elif cat == "ID":
                    path = self.generator.generate_id_img(i)
                
                raw_files.append((path, cat))
                
        print(f"Données brutes générées : {len(raw_files)} images.")
        
        print("\n--- Étape 2 : Data Augmentation ---")
        all_samples = []
        for path, cat in raw_files:
            # Add original
            all_samples.append((path, cat))
            
            # Add augmented versions
            base_name = os.path.basename(path).split('.')[0]
            self.augmentor.augment_file(path, num_variants=AUG_PER_SAMPLE)
            
            for i in range(AUG_PER_SAMPLE):
                aug_path = os.path.join(self.augmentor.output_dir, f"{base_name}_aug_{i}.jpg")
                if os.path.exists(aug_path):
                    all_samples.append((aug_path, cat))
                    
        print(f"Total des échantillons après augmentation : {len(all_samples)}")
        return all_samples

    def extract_features(self, samples):
        print("\n--- Étape 3 : Extraction de texte (OCR) ---")
        texts = []
        labels = []
        
        count = 0
        total = len(samples)
        for path, cat in samples:
            count += 1
            if count % 20 == 0:
                print(f"OCR en cours... {count}/{total}")
            
            try:
                # Use Tesseract to get text
                image = cv2.imread(path)
                text = pytesseract.image_to_string(image, lang='fra')
                
                # Cleanup text
                text = text.lower().strip()
                if len(text) > 5: # Filter out empty or noise-only OCR results
                    texts.append(text)
                    labels.append(cat)
            except Exception as e:
                print(f"Erreur OCR sur {path}: {e}")
                
        print(f"Succès : {len(texts)} documents traitables.")
        return texts, labels

    def train(self, texts, labels):
        print("\n--- Étape 4 : Entraînement du modèle ML (Strategy 80/20) ---")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        print(f"Entraînement sur {len(X_train)} documents, Test sur {len(X_test)} documents.")
        
        # Build Pipeline
        model = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000)),
            ('clf', LogisticRegression(C=10, solver='lbfgs'))
        ])
        
        # Fit
        model.fit(X_train, y_train)
        
        # Evaluate
        predictions = model.predict(X_test)
        print("\n--- ÉVALUATION FINALE ---")
        print(f"Précision (Accuracy) : {accuracy_score(y_test, predictions):.2%}")
        print("\nTableau détaillé :")
        print(classification_report(y_test, predictions))
        
        # Save model
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
            
        print(f"\nModèle sauvegardé avec succès dans : {MODEL_PATH}")

if __name__ == "__main__":
    start_time = time.time()
    trainer = ModelTrainer()
    
    # Run pipeline
    samples = trainer.prepare_dataset()
    texts, labels = trainer.extract_features(samples)
    trainer.train(texts, labels)
    
    elapsed = time.time() - start_time
    print(f"\nPipeline terminé en {elapsed:.1f} secondes. ✨")
