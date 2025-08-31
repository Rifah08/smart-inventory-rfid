import sqlite3

def get_db():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            rfid_tag TEXT UNIQUE,
            quantity INTEGER,
            price REAL
        )
    ''')
    # Add sample items if table is empty
    if conn.execute('SELECT count(*) FROM items').fetchone()[0] == 0:
        sample_items = [
            ('Notebook', 'TAG001', 15, 2.5),
            ('Pen', 'TAG002', 8, 1.2),
            ('Stapler', 'TAG003', 3, 8.99)
        ]
        conn.executemany('INSERT INTO items (name, rfid_tag, quantity, price) VALUES (?,?,?,?)', sample_items)
        conn.commit()
    conn.close()
