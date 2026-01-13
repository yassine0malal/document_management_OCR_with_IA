from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import random
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import sys

# Ajouter le dossier courant au path pour les imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

class SyntheticDataGenerator:
    def __init__(self, output_dir=None):
        if output_dir is None:
            output_dir = os.path.join(PROJECT_ROOT, "uploads/synthetic")
        self.output_dir = output_dir
        self.faker = Faker('fr_FR')
        os.makedirs(self.output_dir, exist_ok=True)
        try:
            # Use a basic font if possible, otherwise default
            self.font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            self.font_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        except:
            self.font_bold = None
            self.font_regular = None

    def _get_path(self, category, index, ext="pdf"):
        cat_dir = os.path.join(self.output_dir, category)
        os.makedirs(cat_dir, exist_ok=True)
        return os.path.join(cat_dir, f"{category.lower()}_{index}.{ext}")

    def generate_invoice_img(self, index):
        file_path = self._get_path("FACTURE", index, "jpg")
        img = Image.new('RGB', (800, 1100), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        
        # Header
        d.text((50, 50), self.faker.company().upper(), fill=(0,0,0))
        d.text((50, 70), self.faker.address().replace('\n', ', '), fill=(50,50,50))
        
        # Title
        d.text((350, 150), "FACTURE", fill=(0,0,0))
        
        # Details
        d.text((50, 200), f"N° Facture : {self.faker.bothify(text='INV-####')}", fill=(0,0,0))
        d.text((50, 220), f"Date : {self.faker.date()}", fill=(0,0,0))
        
        # Items
        y = 300
        d.text((50, y), "Article / Description", fill=(0,0,0))
        d.text((650, y), "Prix", fill=(0,0,0))
        d.line((50, y+20, 750, y+20), fill=(0,0,0))
        
        y += 40
        total = 0
        for _ in range(random.randint(3, 8)):
            item = self.faker.catch_phrase()
            price = random.uniform(10, 500)
            d.text((50, y), item, fill=(50,50,50))
            d.text((650, y), f"{price:.2f} €", fill=(50,50,50))
            total += price
            y += 30
            
        d.line((500, y+10, 750, y+10), fill=(0,0,0))
        d.text((550, y+30), f"TOTAL TTC : {total:.2f} €", fill=(0,0,0))
        
        img.save(file_path)
        return file_path

    def generate_contract_img(self, index):
        file_path = self._get_path("CONTRAT", index, "jpg")
        img = Image.new('RGB', (800, 1100), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        
        d.text((250, 50), "CONTRAT DE SERVICES", fill=(0,0,0))
        
        y = 150
        lines = [
            f"Entre : {self.faker.company()}",
            f"Et : {self.faker.name()}",
            "",
            "ARTICLE 1 : OBJET",
            f"Le prestataire s'engage à fournir : {self.faker.job()}",
            "",
            "ARTICLE 2 : RENUMERATION",
            f"Le montant total de la mission est fixé à {random.randint(1000, 5000)} €.",
            "",
            "ARTICLE 3 : DUREE",
            "Le contrat prend effet dès signature.",
            "",
            f"Fait le {self.faker.date()} à {self.faker.city()}"
        ]
        
        for line in lines:
            d.text((70, y), line, fill=(0,0,0))
            y += 30
            
        img.save(file_path)
        return file_path

    def generate_id_img(self, index):
        file_path = self._get_path("ID", index, "jpg")
        img = Image.new('RGB', (600, 400), color=(240, 240, 255))
        d = ImageDraw.Draw(img)
        
        d.text((200, 20), "RÉPUBLIQUE FRANÇAISE", fill=(0,0,100))
        d.text((200, 40), "CARTE NATIONALE D'IDENTITÉ", fill=(0,0,100))
        
        d.rectangle((20, 80, 150, 250), outline=(0,0,0))
        d.text((50, 150), "PHOTO", fill=(100,100,100))
        
        d.text((180, 100), f"NOM : {self.faker.last_name().upper()}", fill=(0,0,0))
        d.text((180, 130), f"PRÉNOMS : {self.faker.first_name()}", fill=(0,0,0))
        d.text((180, 160), f"NÉ LE : {self.faker.date()}", fill=(0,0,0))
        d.text((180, 190), f"À : {self.faker.city().upper()}", fill=(0,0,0))
        
        d.text((20, 350), f"IDFRA{self.faker.bothify('##########')}<<<<<<<<<<<<", fill=(0,0,0))
        
        img.save(file_path)
        return file_path

    def generate_batch(self, count_per_cat=10):
        stats = {"FACTURE": 0, "CONTRAT": 0, "ID": 0}
        for i in range(count_per_cat):
            self.generate_invoice_img(i)
            self.generate_contract_img(i)
            self.generate_id_img(i)
            stats["FACTURE"] += 1
            stats["CONTRAT"] += 1
            stats["ID"] += 1
        return stats

if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    res = generator.generate_batch(5)
    print(f"Génération terminée : {res}")
