import frappe
from datetime import datetime, timedelta
import random

def create_pharmacy_sample_data():
    print("🚀 Starting pharmacy sample data generation...")

    # ------------------------------------------------------------------
    # 1. Create Medicine Categories
    # ------------------------------------------------------------------


    # ------------------------------------------------------------------
    # 2. Create Medicines with real data
    # ------------------------------------------------------------------
    medicines = [
        # Analgesics
        {"medicine_code": "PAR-001", "medicine_name": "Paracetamol 500mg", "generic_name": "Paracetamol", "category": "Analgesics", "manufacturer": "GSK", "unit": "Tablet", "purchase_price": 2.50, "selling_price": 5.00, "reorder_level": 100},
        {"medicine_code": "IBU-001", "medicine_name": "Ibuprofen 400mg", "generic_name": "Ibuprofen", "category": "Analgesics", "manufacturer": "Pfizer", "unit": "Tablet", "purchase_price": 3.00, "selling_price": 6.50, "reorder_level": 80},
        {"medicine_code": "DIC-001", "medicine_name": "Diclofenac 50mg", "generic_name": "Diclofenac Sodium", "category": "Analgesics", "manufacturer": "Novartis", "unit": "Tablet", "purchase_price": 4.00, "selling_price": 8.00, "reorder_level": 60},
        # Antibiotics
        {"medicine_code": "AMO-001", "medicine_name": "Amoxicillin 500mg", "generic_name": "Amoxicillin", "category": "Antibiotics", "manufacturer": "Sandoz", "unit": "Capsule", "purchase_price": 5.00, "selling_price": 12.00, "reorder_level": 50},
        {"medicine_code": "AZI-001", "medicine_name": "Azithromycin 250mg", "generic_name": "Azithromycin", "category": "Antibiotics", "manufacturer": "Teva", "unit": "Tablet", "purchase_price": 6.00, "selling_price": 15.00, "reorder_level": 40},
        {"medicine_code": "CEF-001", "medicine_name": "Cephalexin 500mg", "generic_name": "Cephalexin", "category": "Antibiotics", "manufacturer": "Mylan", "unit": "Capsule", "purchase_price": 7.00, "selling_price": 14.00, "reorder_level": 30},
        # Antihistamines
        {"medicine_code": "CET-001", "medicine_name": "Cetirizine 10mg", "generic_name": "Cetirizine HCl", "category": "Antihistamines", "manufacturer": "Johnson & Johnson", "unit": "Tablet", "purchase_price": 2.00, "selling_price": 4.50, "reorder_level": 100},
        {"medicine_code": "LOR-001", "medicine_name": "Loratadine 10mg", "generic_name": "Loratadine", "category": "Antihistamines", "manufacturer": "Bayer", "unit": "Tablet", "purchase_price": 2.50, "selling_price": 5.00, "reorder_level": 80},
        # Antacids
        {"medicine_code": "OME-001", "medicine_name": "Omeprazole 20mg", "generic_name": "Omeprazole", "category": "Antacids", "manufacturer": "AstraZeneca", "unit": "Capsule", "purchase_price": 3.00, "selling_price": 7.00, "reorder_level": 60},
        {"medicine_code": "RAN-001", "medicine_name": "Ranitidine 150mg", "generic_name": "Ranitidine", "category": "Antacids", "manufacturer": "GSK", "unit": "Tablet", "purchase_price": 2.00, "selling_price": 4.00, "reorder_level": 70},
        # Vitamins
        {"medicine_code": "VIT-C", "medicine_name": "Vitamin C 1000mg", "generic_name": "Ascorbic Acid", "category": "Vitamins", "manufacturer": "Nature's Bounty", "unit": "Tablet", "purchase_price": 1.50, "selling_price": 3.50, "reorder_level": 150},
        {"medicine_code": "VIT-D", "medicine_name": "Vitamin D3 2000IU", "generic_name": "Cholecalciferol", "category": "Vitamins", "manufacturer": "Solgar", "unit": "Capsule", "purchase_price": 2.00, "selling_price": 5.00, "reorder_level": 100},
        {"medicine_code": "VIT-B12", "medicine_name": "Vitamin B12 1000mcg", "generic_name": "Cyanocobalamin", "category": "Vitamins", "manufacturer": "Kirkland", "unit": "Tablet", "purchase_price": 1.80, "selling_price": 4.00, "reorder_level": 80},
        # Antipyretics
        {"medicine_code": "ASP-001", "medicine_name": "Aspirin 300mg", "generic_name": "Acetylsalicylic Acid", "category": "Antipyretics", "manufacturer": "Bayer", "unit": "Tablet", "purchase_price": 1.00, "selling_price": 2.50, "reorder_level": 120},
        # Antispasmodics
        {"medicine_code": "BUS-001", "medicine_name": "Buscopan 10mg", "generic_name": "Hyoscine Butylbromide", "category": "Antispasmodics", "manufacturer": "Boehringer Ingelheim", "unit": "Tablet", "purchase_price": 4.00, "selling_price": 8.50, "reorder_level": 50},
        # Cardiovascular
        {"medicine_code": "LIS-001", "medicine_name": "Lisinopril 10mg", "generic_name": "Lisinopril", "category": "Cardiovascular", "manufacturer": "Merck", "unit": "Tablet", "purchase_price": 3.50, "selling_price": 7.00, "reorder_level": 60},
        {"medicine_code": "AML-001", "medicine_name": "Amlodipine 5mg", "generic_name": "Amlodipine Besylate", "category": "Cardiovascular", "manufacturer": "Pfizer", "unit": "Tablet", "purchase_price": 4.00, "selling_price": 8.00, "reorder_level": 50},
        # Respiratory
        {"medicine_code": "SAL-001", "medicine_name": "Salbutamol 100mcg", "generic_name": "Salbutamol Sulfate", "category": "Respiratory", "manufacturer": "GSK", "unit": "Inhaler", "purchase_price": 8.00, "selling_price": 18.00, "reorder_level": 30},
        {"medicine_code": "BUD-001", "medicine_name": "Budesonide 200mcg", "generic_name": "Budesonide", "category": "Respiratory", "manufacturer": "AstraZeneca", "unit": "Inhaler", "purchase_price": 12.00, "selling_price": 25.00, "reorder_level": 20},
        # Dermatological
        {"medicine_code": "HYD-001", "medicine_name": "Hydrocortisone 1%", "generic_name": "Hydrocortisone", "category": "Dermatological", "manufacturer": "Pfizer", "unit": "Cream", "purchase_price": 3.00, "selling_price": 6.00, "reorder_level": 40},
        {"medicine_code": "CLO-001", "medicine_name": "Clotrimazole 1%", "generic_name": "Clotrimazole", "category": "Dermatological", "manufacturer": "Bayer", "unit": "Cream", "purchase_price": 4.00, "selling_price": 8.00, "reorder_level": 30},
        # More Antibiotics
        {"medicine_code": "CIP-001", "medicine_name": "Ciprofloxacin 500mg", "generic_name": "Ciprofloxacin", "category": "Antibiotics", "manufacturer": "Bayer", "unit": "Tablet", "purchase_price": 6.00, "selling_price": 14.00, "reorder_level": 40},
        # More Analgesics
        {"medicine_code": "MOR-001", "medicine_name": "Morphine 10mg", "generic_name": "Morphine Sulfate", "category": "Analgesics", "manufacturer": "Purdue", "unit": "Tablet", "purchase_price": 8.00, "selling_price": 20.00, "reorder_level": 20},
        # More Vitamins
        {"medicine_code": "MVM-001", "medicine_name": "Multivitamin", "generic_name": "Multivitamin Complex", "category": "Vitamins", "manufacturer": "Centrum", "unit": "Tablet", "purchase_price": 5.00, "selling_price": 10.00, "reorder_level": 100},
        # More Antihistamines
        {"medicine_code": "FEX-001", "medicine_name": "Fexofenadine 180mg", "generic_name": "Fexofenadine", "category": "Antihistamines", "manufacturer": "Sanofi", "unit": "Tablet", "purchase_price": 3.00, "selling_price": 6.50, "reorder_level": 60},
        # Cardiovascular
        {"medicine_code": "ATE-001", "medicine_name": "Atenolol 50mg", "generic_name": "Atenolol", "category": "Cardiovascular", "manufacturer": "AstraZeneca", "unit": "Tablet", "purchase_price": 2.50, "selling_price": 5.50, "reorder_level": 50},
        # Respiratory
        {"medicine_code": "MON-001", "medicine_name": "Montelukast 10mg", "generic_name": "Montelukast Sodium", "category": "Respiratory", "manufacturer": "Merck", "unit": "Tablet", "purchase_price": 4.00, "selling_price": 9.00, "reorder_level": 40},
        # Dermatological
        {"medicine_code": "TRE-001", "medicine_name": "Tretinoin 0.05%", "generic_name": "Tretinoin", "category": "Dermatological", "manufacturer": "Janssen", "unit": "Cream", "purchase_price": 10.00, "selling_price": 22.00, "reorder_level": 20},
        # Additional
        {"medicine_code": "MET-001", "medicine_name": "Metformin 500mg", "generic_name": "Metformin HCl", "category": "Antacids", "manufacturer": "Bristol-Myers Squibb", "unit": "Tablet", "purchase_price": 2.00, "selling_price": 4.50, "reorder_level": 100},
        {"medicine_code": "GAB-001", "medicine_name": "Gabapentin 300mg", "generic_name": "Gabapentin", "category": "Analgesics", "manufacturer": "Pfizer", "unit": "Capsule", "purchase_price": 7.00, "selling_price": 15.00, "reorder_level": 30},
    ]

    created_medicines = {}
    for med in medicines:
        if not frappe.db.exists("Medicine", med["medicine_code"]):
            doc = frappe.get_doc({"doctype": "Medicine", **med})
            doc.insert()
            created_medicines[med["medicine_code"]] = doc.name
            print(f"✅ Created medicine: {med['medicine_name']} ({med['medicine_code']})")
        else:
            doc = frappe.get_doc("Medicine", med["medicine_code"])
            created_medicines[med["medicine_code"]] = doc.name
            print(f"⏩ Medicine {med['medicine_code']} already exists, skipping.")

    # ------------------------------------------------------------------
    # 3. Create Batches for each medicine
    # ------------------------------------------------------------------
    # We'll generate 2-3 batches per medicine with realistic dates
    # Batch numbers: BATCH-{medicine_code}-{seq}
    # Manufacturing date: 6-12 months ago, Expiry: 12-24 months from manufacture

    for med_code, docname in created_medicines.items():
        # Number of batches: random 2-3
        num_batches = random.randint(2, 3)
        for i in range(num_batches):
            # Generate dates
            manuf_date = datetime.now() - timedelta(days=random.randint(180, 360))
            expiry_date = manuf_date + timedelta(days=random.randint(365, 730))  # 1-2 years
            batch_number = f"BATCH-{med_code}-{i+1:02d}"
            if not frappe.db.exists("Medicine Batch", batch_number):
                # Initial quantity: 200-500 units
                quantity = random.randint(200, 500)
                batch = frappe.get_doc({
                    "doctype": "Medicine Batch",
                    "medicine": docname,
                    "batch_number": batch_number,
                    "manufacturing_date": manuf_date.date(),
                    "expiry_date": expiry_date.date(),
                    "quantity": quantity,
                    "remaining_quantity": quantity,
                    "purchase_price": frappe.db.get_value("Medicine", docname, "purchase_price"),
                    "selling_price": frappe.db.get_value("Medicine", docname, "selling_price")
                })
                batch.insert()
                print(f"✅ Created batch {batch_number} for {med_code} (Qty: {quantity})")
            else:
                print(f"⏩ Batch {batch_number} already exists.")

    # ------------------------------------------------------------------
    # 6. Final commit
    # ------------------------------------------------------------------
    frappe.db.commit()
    print("\n🎉 Sample pharmacy data generation complete!")
    print("Your system now has realistic medicines, batches, stock-in, and sales.")
    print("Check the dashboard for low-stock and expiry alerts.")

# Run it
create_pharmacy_sample_data()