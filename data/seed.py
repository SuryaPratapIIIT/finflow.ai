import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker()

DB_PATH = os.path.join(os.path.dirname(__file__), 'finflow.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def init_db(conn):
    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())
        
def seed_data():
    # Remove existing db to re-seed cleanly if needed
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    cursor = conn.cursor()
    
    # 1. Generate 15 Customers
    customers = []
    for _ in range(15):
        # Determine reliability to model realistic behavior
        reliability = random.choice(['reliable', 'moderate', 'chronically_late'])
        if reliability == 'reliable':
            score = random.randint(80, 100)
        elif reliability == 'moderate':
            score = random.randint(40, 79)
        else:
            score = random.randint(0, 39)
            
        name = fake.name()
        email = fake.email()
        phone = fake.phone_number()
        
        cursor.execute('''
            INSERT INTO customers (name, email, phone, payment_reliability_score)
            VALUES (?, ?, ?, ?)
        ''', (name, email, phone, score))
        customers.append({
            'id': cursor.lastrowid,
            'score': score
        })
        
    # 2. Generate 50 Invoices
    for _ in range(50):
        c = random.choice(customers)
        customer_id = c['id']
        score = c['score']
        
        amount = round(random.uniform(100.0, 5000.0), 2)
        
        # Decide invoice status based on customer reliability score
        if score > 80:
            status = random.choices(['paid', 'pending', 'overdue'], weights=[0.80, 0.15, 0.05])[0]
        elif score > 40:
            status = random.choices(['paid', 'pending', 'overdue'], weights=[0.50, 0.20, 0.30])[0]
        else:
            status = random.choices(['paid', 'pending', 'overdue'], weights=[0.20, 0.10, 0.70])[0]
            
        today = datetime.now()
        if status == 'overdue':
            # Due in the past
            days_ago = random.randint(1, 90)
            due_date = today - timedelta(days=days_ago)
        elif status == 'pending':
            # Due in the future
            days_ahead = random.randint(1, 30)
            due_date = today + timedelta(days=days_ahead)
        else: 
            # Paid - could be past or recent
            days_offset = random.randint(-60, 30)
            due_date = today - timedelta(days=days_offset)
            
        due_date_str = due_date.strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT INTO invoices (customer_id, amount, due_date, status)
            VALUES (?, ?, ?, ?)
        ''', (customer_id, amount, due_date_str, status))
        invoice_id = cursor.lastrowid
        
        # 3. Populate Payment History for paid invoices
        if status == 'paid':
            if score > 80:
                paid_on_time = random.choices([True, False], weights=[0.95, 0.05])[0]
            elif score > 40:
                paid_on_time = random.choices([True, False], weights=[0.60, 0.40])[0]
            else:
                paid_on_time = random.choices([True, False], weights=[0.20, 0.80])[0]
                
            days_late = 0 if paid_on_time else random.randint(1, 45)
            
            cursor.execute('''
                INSERT INTO payment_history (customer_id, invoice_id, paid_on_time, days_late)
                VALUES (?, ?, ?, ?)
            ''', (customer_id, invoice_id, paid_on_time, days_late))
            
    conn.commit()
    conn.close()
    print("Database seeded successfully with 15 customers and 50 invoices.")

if __name__ == '__main__':
    seed_data()
