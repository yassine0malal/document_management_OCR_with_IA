-- Création de la base de données
CREATE DATABASE IF NOT EXISTS gestion_documents;
USE gestion_documents;

-- Table Utilisateurs
CREATE TABLE IF NOT EXISTS Utilisateurs (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    role VARCHAR(50) DEFAULT 'utilisateur',
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table Categories
CREATE TABLE IF NOT EXISTS Categories (
    id_categorie INT AUTO_INCREMENT PRIMARY KEY,
    nom_categorie VARCHAR(100) NOT NULL UNIQUE
);

-- Insertion des catégories par défaut
INSERT IGNORE INTO Categories (nom_categorie) VALUES ('Facture'), ('Contrat'), ('CV'), ('Lettre'), ('Autre');

-- Table Documents
CREATE TABLE IF NOT EXISTS Documents (
    id_document INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT,
    nom_fichier VARCHAR(255) NOT NULL,
    chemin_fichier VARCHAR(255) NOT NULL,
    date_upload DATETIME DEFAULT CURRENT_TIMESTAMP,
    texte_extrait TEXT,
    categorie VARCHAR(100),
    score_confiance FLOAT,
    statut_document VARCHAR(50) DEFAULT 'actif',
    FOREIGN KEY (id_user) REFERENCES Utilisateurs(id_user)
);

-- Table Statistiques
CREATE TABLE IF NOT EXISTS Statistiques (
    id_stat INT AUTO_INCREMENT PRIMARY KEY,
    id_categorie INT,
    nb_documents INT DEFAULT 0,
    date_stat DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_categorie) REFERENCES Categories(id_categorie)
);
