Purpose: The main server code that handles API requests (e.g., scanning an item, getting inventory).

from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_db, init_db

app = Flask(__name__)
CORS(app)
init_db()

@app.route('/api/items')
def get_items():
    conn = get_db()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return jsonify([dict(item) for item in items])

@app.route('/api/scan', methods=['POST'])
def scan_item():
    data = request.get_json()
    tag_id = data['tag_id']
    action = data.get('action', 'add') # add or remove

    conn = get_db()
    item = conn.execute('SELECT * FROM items WHERE rfid_tag = ?', (tag_id,)).fetchone()
    new_qty = item['quantity'] + 1 if action == 'add' else max(0, item['quantity'] - 1)
    
    conn.execute('UPDATE items SET quantity = ? WHERE rfid_tag = ?', (new_qty, tag_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Updated', 'new_quantity': new_qty})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
