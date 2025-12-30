from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import random
import os

class SyntheticDataGenerator:
    def __init__(self, output_dir="uploads/synthetic"):
        self.output_dir = output_dir
        self.faker = Faker()
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_invoice(self, filename):
        file_path = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        # Company Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, self.faker.company())
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 65, self.faker.address().replace('\n', ', '))
        
        # Invoice Title
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width / 2, height - 120, "FACTURE")
        
        # Invoice Details
        c.setFont("Helvetica", 12)
        invoice_id = f"INV-{random.randint(1000, 9999)}"
        c.drawString(50, height - 160, f"Numéro de facture : {invoice_id}")
        c.drawString(50, height - 175, f"Date : {self.faker.date()}")
        
        # Client Details
        c.drawString(400, height - 160, "Facturé à :")
        c.drawString(400, height - 175, self.faker.name())
        
        # Table Header
        c.line(50, height - 210, 550, height - 210)
        c.drawString(60, height - 230, "Description")
        c.drawString(450, height - 230, "Montant")
        c.line(50, height - 240, 550, height - 240)
        
        # Table Content
        total = 0
        y = height - 260
        for _ in range(random.randint(1, 5)):
            item = self.faker.word().capitalize()
            price = random.uniform(10, 500)
            c.drawString(60, y, item)
            c.drawString(450, y, f"{price:.2f} €")
            total += price
            y -= 20
            
        c.line(50, y - 10, 550, y - 10)
        
        # Summary
        c.setFont("Helvetica-Bold", 12)
        c.drawString(380, y - 30, f"Total TTC : {total:.2f} €")
        c.drawString(380, y - 50, f"TVA (20%) : {(total * 0.2):.2f} €")
        
        c.save()
        print(f"Generated: {file_path}")

    def generate_batch(self, count=10):
        for i in range(count):
            self.generate_invoice(f"synthetic_invoice_{i}.pdf")

if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    generator.generate_batch(5)
    print("Synthetic invoices generated in uploads/synthetic/")
