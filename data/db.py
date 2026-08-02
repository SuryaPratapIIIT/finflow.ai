import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'finflow.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_overdue_invoices():
    """
    Returns all overdue invoices.
    days_overdue is computed dynamically using SQLite date functions.
    """
    query = '''
        SELECT 
            id, customer_id, amount, due_date, status,
            CAST(julianday('now') - julianday(due_date) AS INTEGER) AS days_overdue
        FROM invoices
        WHERE status = 'overdue'
        ORDER BY days_overdue DESC
    '''
    with get_connection() as conn:
        return [dict(row) for row in conn.execute(query).fetchall()]

def get_customer(customer_id: int):
    """
    Returns details for a specific customer.
    """
    query = 'SELECT * FROM customers WHERE id = ?'
    with get_connection() as conn:
        row = conn.execute(query, (customer_id,)).fetchone()
        return dict(row) if row else None

def get_payment_history(customer_id: int):
    """
    Returns the payment history for a specific customer.
    """
    query = '''
        SELECT * FROM payment_history
        WHERE customer_id = ?
        ORDER BY id DESC
    '''
    with get_connection() as conn:
        return [dict(row) for row in conn.execute(query, (customer_id,)).fetchall()]
