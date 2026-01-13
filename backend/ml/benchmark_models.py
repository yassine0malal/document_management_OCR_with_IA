import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import os

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "dataset.csv")
OUTPUT_IMG = os.path.join(BASE_DIR, "comparison_results.png")

def run_benchmark():
    print(f"--- Chargement du dataset : {CSV_PATH} ---")
    if not os.path.exists(CSV_PATH):
        print(f"Erreur : Le fichier {CSV_PATH} n'existe pas.")
        return

    df = pd.read_csv(CSV_PATH)
    print(f"Nombre de documents chargés : {len(df)}")
    
    # Nettoyage : Garder uniquement les classes avec au moins 2 membres pour le découpage train/test
    class_counts = df['categorie'].value_counts()
    classes_to_keep = class_counts[class_counts >= 2].index
    df = df[df['categorie'].isin(classes_to_keep)]
    print(f"Nombre de documents après filtrage des classes trop petites : {len(df)}")
    
    X = df['texte'].fillna('')
    y = df['categorie']

    # Division Train/Test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Définition des modèles
    models = {
        "Naive Bayes": MultinomialNB(),
        "SVM (Linear)": CalibratedClassifierCV(SGDClassifier(loss='hinge', random_state=42)),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42)
    }

    results = []

    print("\n--- Phase d'entraînement et évaluation ---")
    for name, clf in models.items():
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=2000, stop_words='english')),
            ('clf', clf)
        ])
        
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        results.append({"Modèle": name, "Précision": acc})
        
        print(f"\n[ {name} ]")
        print(f"Accuracy: {acc:.2%}")
        # print(classification_report(y_test, y_pred))

    # Visualisation
    res_df = pd.DataFrame(results)
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(res_df["Modèle"], res_df["Précision"], color=['#4e79a7', '#f28e2b', '#e15759'])
    
    # Ajouter les labels sur les barres
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{height:.2%}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    plt.title("Comparaison des Algorithmes de Classification", fontsize=16)
    plt.ylim(0, 1.1)
    plt.ylabel("Score de Précision (Accuracy)", fontsize=12)
    plt.xlabel("Algorithme", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_IMG)
    print(f"\nGraphique de comparaison sauvegardé dans : {OUTPUT_IMG}")
    
    return res_df

if __name__ == "__main__":
    run_benchmark()
