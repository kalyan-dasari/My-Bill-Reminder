import sqlite3

def init_db():
    conn = sqlite3.connect('bills.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recharges (
            id INTEGER PRIMARY KEY,
            contact_name TEXT NOT NULL,
            recharge_date TEXT NOT NULL,
            valid_days INTEGER NOT NULL,
            plan_amount REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emis (
            id INTEGER PRIMARY KEY,
            emi_name TEXT NOT NULL,
            due_date TEXT NOT NULL,
            amount REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            event_name TEXT NOT NULL,
            event_date TEXT NOT NULL,
            notes TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monthly_bills (
            id INTEGER PRIMARY KEY,
            bill_name TEXT NOT NULL,
            amount REAL NOT NULL,
            due_date TEXT NOT NULL,
            is_paid INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_bills (
            id INTEGER PRIMARY KEY,
            bill_name TEXT NOT NULL,
            bill_type TEXT NOT NULL,
            due_date TEXT NOT NULL,
            amount REAL NOT NULL,
            is_paid INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('bills.db')
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")