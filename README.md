# smart-inventory-rfid
A smart, RFID-based inventory management system designed for small businesses to automate stock tracking, reduce errors, and provide real-time insights.
smart-inventory-rfid/
├── src/
│   ├── backend/
│   │   ├── server.py
│   │   ├── requirements.txtfrom flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
from database import init_db, get_db_connection

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend')
CORS(app)  # Enable Cross-Origin Requests

# Initialize database
init_db()

# API Routes
@app.route('/')
def serve_frontend():
    """Serve the main dashboard page"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/items', methods=['GET'])
def get_all_items():
    """Get all inventory items"""
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    items_list = [dict(item) for item in items]
    return jsonify(items_list)

@app.route('/api/scan', methods=['POST'])
def handle_scan():
    """Handle RFID scan - add or remove item from inventory"""
    data = request.get_json()
    tag_id = data.get('tag_id')
    action = data.get('action', 'add')  # Default action is 'add'
    
    if not tag_id:
        return jsonify({'error': 'No tag_id provided'}), 400
    
    conn = get_db_connection()
    
    # Find item by RFID tag
    item = conn.execute(
        'SELECT * FROM items WHERE rfid_tag = ?', (tag_id,)
    ).fetchone()
    
    if not item:
        conn.close()
        return jsonify({'error': 'Item not found'}), 404
    
    # Update quantity based on action
    new_quantity = item['quantity']
    if action == 'add':
        new_quantity += 1
    elif action == 'remove':
        new_quantity = max(0, new_quantity - 1)
    
    # Update database
    conn.execute(
        'UPDATE items SET quantity = ? WHERE rfid_tag = ?',
        (new_quantity, tag_id)
    )
    conn.commit()
    
    # Get updated item
    updated_item = conn.execute(
        'SELECT * FROM items WHERE rfid_tag = ?', (tag_id,)
    ).fetchone()
    conn.close()
    
    return jsonify(dict(updated_item))

@app.route('/api/reports/low-stock', methods=['GET'])
def get_low_stock():
    """Get items that are low in stock (quantity < 5)"""
    conn = get_db_connection()
    low_stock_items = conn.execute(
        'SELECT * FROM items WHERE quantity < 5'
    ).fetchall()
    conn.close()
    
    low_stock_list = [dict(item) for item in low_stock_items]
    return jsonify(low_stock_list)

@app.route('/api/reports/inventory', methods=['GET'])
def get_inventory_report():
    """Generate inventory summary report"""
    conn = get_db_connection()
    
    # Get total items and value
    inventory_data = conn.execute('''
        SELECT 
            COUNT(*) as total_items,
            SUM(quantity * price) as total_value,
            SUM(CASE WHEN quantity < 5 THEN 1 ELSE 0 END) as low_stock_count
        FROM items
    ''').fetchone()
    
    conn.close()
    
    return jsonify(dict(inventory_data))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
│   │   └── database.py
│   ├── frontend/
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── script.js
│   └── prototype/
│       └── rfid_simulator.py
├── docs/
│   └── (your documents here)
├── README.md
└── .gitignore
import sqlite3
import os

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row  # This enables name-based access to columns
    return conn

def init_db():
    """Initialize the database with sample data"""
    conn = get_db_connection()
    
    # Create items table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rfid_tag TEXT UNIQUE NOT NULL,
            quantity INTEGER DEFAULT 0,
            price REAL DEFAULT 0.0,
            category TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample data if table is empty
    if conn.execute('SELECT COUNT(*) FROM items').fetchone()[0] == 0:
        sample_items = [
            ('Notebook', 'TAG001', 15, 2.50, 'Stationery'),
            ('Pen', 'TAG002', 8, 1.20, 'Stationery'),
            ('Stapler', 'TAG003', 3, 8.99, 'Office Supplies'),
            ('Paper Clips', 'TAG004', 150, 0.99, 'Office Supplies'),
            ('Coffee Mug', 'TAG005', 12, 5.75, 'Kitchen'),
            ('Mouse Pad', 'TAG006', 2, 4.50, 'Computer Accessories')
        ]
        
        conn.executemany(
            'INSERT INTO items (name, rfid_tag, quantity, price, category) VALUES (?, ?, ?, ?, ?)',
            sample_items
        )
        conn.commit()
    
    conn.close()
    Flask==2.3.3
Flask-CORS==4.0.0

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Inventory Management System</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Smart Inventory Management</h1>
            <p>Real-time tracking using RFID technology</p>
        </header>

        <div class="dashboard">
            <!-- Inventory Summary -->
            <div class="card summary-card">
                <h2>Inventory Summary</h2>
                <div id="summary-stats" class="stats">
                    <p>Loading inventory data...</p>
                </div>
            </div>

            <!-- Low Stock Alerts -->
            <div class="card alerts-card">
                <h2>⚠️ Low Stock Alerts</h2>
                <div id="alerts-list">
                    <p>Checking stock levels...</p>
                </div>
            </div>

            <!-- Inventory Table -->
            <div class="card inventory-card">
                <h2>Current Inventory</h2>
                <table id="inventory-table">
                    <thead>
                        <tr>
                            <th>Product Name</th>
                            <th>RFID Tag</th>
                            <th>Quantity</th>
                            <th>Price</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="inventory-body">
                        <!-- Data will be populated by JavaScript -->
                    </tbody>
                </table>
            </div>

            <!-- Reports Section -->
            <div class="card reports-card">
                <h2>Reports & Analytics</h2>
                <button onclick="generateReport()" class="btn-primary">
                    Generate Inventory Report
                </button>
                <div id="report-results"></div>
            </div>
        </div>

        <!-- Simulation Controls -->
        <div class="simulation-panel">
            <h3>RFID Scanner Simulation</h3>
            <div class="sim-controls">
                <button onclick="simulateScan('add')" class="btn-success">
                    Simulate Scan (Add Item)
                </button>
                <button onclick="simulateScan('remove')" class="btn-warning">
                    Simulate Scan (Remove Item)
                </button>
                <select id="product-select">
                    <option value="">Select a product to scan...</option>
                </select>
            </div>
        </div>
    </div>

    <script src="script.js"></script>
</body>
</html>

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f4f4f4;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

header {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
}

header h1 {
    margin-bottom: 10px;
}

.dashboard {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.card h2 {
    margin-bottom: 15px;
    color: #2c3e50;
    border-bottom: 2px solid #eee;
    padding-bottom: 10px;
}

.stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.stat-item {
    text-align: center;
    padding: 10px;
}

.stat-value {
    font-size: 1.5em;
    font-weight: bold;
    color: #667eea;
}

.stat-label {
    font-size: 0.9em;
    color: #666;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
}

th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

th {
    background-color: #f8f9fa;
    font-weight: 600;
}

.low-stock {
    color: #e74c3c;
    font-weight: bold;
}

.adequate-stock {
    color: #27ae60;
}

.btn-primary, .btn-success, .btn-warning {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1em;
    margin: 5px;
}

.btn-primary {
    background-color: #3498db;
    color: white;
}

.btn-success {
    background-color: #27ae60;
    color: white;
}

.btn-warning {
    background-color: #f39c12;
    color: white;
}

.btn-primary:hover { background-color: #2980b9; }
.btn-success:hover { background-color: #229954; }
.btn-warning:hover { background-color: #e67e22; }

.simulation-panel {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-top: 20px;
}

.sim-controls {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
}

#product-select {
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #ddd;
    min-width: 200px;
}

.alert-item {
    padding: 10px;
    margin: 5px 0;
    background-color: #ffeaa7;
    border-left: 4px solid #fdcb6e;
    border-radius: 3px;
}

@media (max-width: 768px) {
    .dashboard {
        grid-template-columns: 1fr;
    }
    
    .sim-controls {
        flex-direction: column;
        align-items: stretch;
    }
}

const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const inventoryBody = document.getElementById('inventory-body');
const alertsList = document.getElementById('alerts-list');
const summaryStats = document.getElementById('summary-stats');
const productSelect = document.getElementById('product-select');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadInventory();
    loadLowStockAlerts();
    loadSummaryStats();
    populateProductDropdown();
    
    // Refresh data every 30 seconds
    setInterval(() => {
        loadInventory();
        loadLowStockAlerts();
    }, 30000);
});

// Load all inventory items
async function loadInventory() {
    try {
        const response = await fetch(`${API_BASE_URL}/items`);
        const items = await response.json();
        
        inventoryBody.innerHTML = '';
        items.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.name}</td>
                <td>${item.rfid_tag}</td>
                <td class="${item.quantity < 5 ? 'low-stock' : 'adequate-stock'}">
                    ${item.quantity}
                </td>
                <td>$${item.price.toFixed(2)}</td>
                <td>${item.quantity < 5 ? 'Low Stock' : 'In Stock'}</td>
            `;
            inventoryBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading inventory:', error);
    }
}

// Load low stock alerts
async function loadLowStockAlerts() {
    try {
        const response = await fetch(`${API_BASE_URL}/reports/low-stock`);
        const lowStockItems = await response.json();
        
        if (lowStockItems.length === 0) {
            alertsList.innerHTML = '<p class="adequate-stock">No low stock items! 🎉</p>';
            return;
        }
        
        alertsList.innerHTML = '';
        lowStockItems.forEach(item => {
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert-item';
            alertDiv.innerHTML = `
                <strong>${item.name}</strong> is low on stock! 
                Only ${item.quantity} left. Consider reordering.
            `;
            alertsList.appendChild(alertDiv);
        });
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

// Load summary statistics
async function loadSummaryStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/reports/inventory`);
        const summary = await response.json();
        
        summaryStats.innerHTML = `
            <div class="stat-item">
                <div class="stat-value">${summary.total_items}</div>
                <div class="stat-label">Total Products</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">$${summary.total_value.toFixed(2)}</div>
                <div class="stat-label">Total Value</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${summary.low_stock_count}</div>
                <div class="stat-label">Low Stock Items</div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

// Populate product dropdown for simulation
async function populateProductDropdown() {
    try {
        const response = await fetch(`${API_BASE_URL}/items`);
        const items = await response.json();
        
        productSelect.innerHTML = '<option value="">Select a product to scan...</option>';
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item.rfid_tag;
            option.textContent = `${item.name} (${item.rfid_tag})`;
            productSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

// Simulate RFID scan
async function simulateScan(action) {
    const tagId = productSelect.value;
    if (!tagId) {
        alert('Please select a product first!');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/scan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tag_id: tagId,
                action: action
            })
        });
        
        if (response.ok) {
            const updatedItem = await response.json();
            alert(`Successfully ${action === 'add' ? 'added' : 'removed'} ${updatedItem.name}! New quantity: ${updatedItem.quantity}`);
            
            // Refresh all data
            loadInventory();
            loadLowStockAlerts();
            loadSummaryStats();
        } else {
            alert('Error processing scan. Please try again.');
        }
    } catch (error) {
        console.error('Error simulating scan:', error);
        alert('Network error. Make sure the backend server is running!');
    }
}

// Generate inventory report
async function generateReport() {
    try {
        const response = await fetch(`${API_BASE_URL}/reports/inventory`);
        const report = await response.json();
        
        const reportResults = document.getElementById('report-results');
        reportResults.innerHTML = `
            <div class="report-summary">
                <h3>Inventory Report</h3>
                <p><strong>Total Products:</strong> ${report.total_items}</p>
                <p><strong>Total Inventory Value:</strong> $${report.total_value.toFixed(2)}</p>
                <p><strong>Low Stock Items:</strong> ${report.low_stock_count}</p>
                <p><strong>Report Generated:</strong> ${new Date().toLocaleString()}</p>
            </div>
        `;
    } catch (error) {
        console.error('Error generating report:', error);
    }
}

import requests
import random
import time

API_URL = "http://localhost:5000/api"

def simulate_rfid_reader():
    """Simulate an RFID reader scanning tags"""
    print("🔷 RFID Scanner Simulator Started...")
    print("Press Ctrl+C to stop")
    
    # Sample RFID tags from our database
    sample_tags = ['TAG001', 'TAG002', 'TAG003', 'TAG004', 'TAG005', 'TAG006']
    
    try:
        while True:
            # Wait random time between scans (2-10 seconds)
            time.sleep(random.uniform(2, 10))
            
            # Randomly choose a tag and action
            tag_id = random.choice(sample_tags)
            action = random.choice(['add', 'remove'])
            
            print(f"📡 Scanning tag: {tag_id} - Action: {action}")
            
            try:
                response = requests.post(
                    f"{API_URL}/scan",
                    json={
                        "tag_id": tag_id,
                        "action": action
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    item = response.json()# Python
__pycache__/
*.pyc
*.pyo
*.pyd
venv/
env/

# Database
*.db
*.sqlite3

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
                    print(f"✅ Success: {item['name']} - New Qty: {item['quantity']}")
                else:
                    print(f"❌ Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Network error: {e}")
                
    except KeyboardInterrupt:
        print("\n🛑 Scanner stopped by user")

if __name__ == "__main__":
    simulate_rfid_reader()



  cd src/backend

  pip install -r requirements.txt

  python server.py

  cd src/prototype
python rfid_simulator.py

