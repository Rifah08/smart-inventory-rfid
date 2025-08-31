Purpose: Fetches data from the server and makes the page interactive.
  // script.js
// JavaScript for handling frontend logic
const API_URL = 'http://localhost:5000/api';

async function loadInventory() {
    try {
        const response = await fetch(API_URL + '/items');
        const items = await response.json();
        const table = document.querySelector('#inventory-table tbody');
        table.innerHTML = '';
        items.forEach(item => {
            const row = `<tr>
                <td>${item.name}</td><td>${item.rfid_tag}</td>
                <td class="${item.quantity < 5 ? 'low-stock' : ''}">${item.quantity}</td>
                <td>${item.quantity < 5 ? 'LOW STOCK' : 'OK'}</td>
            </tr>`;
            table.innerHTML += row;
        });
    } catch (error) {
        console.error("Error loading inventory:", error);
    }
}

async function simulateScan(action) {
    try {
        await fetch(API_URL + '/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tag_id: 'TAG003', action: action })
        });
        loadInventory();
        alert(`Simulated scan! Action: ${action}. Reloading inventory...`);
    } catch (error) {
        console.error("Error simulating scan:", error);
        alert("Error! Is the backend server running?");
    }
}

// Load data when page opens
loadInventory();


  const API_URL = 'http://localhost:5000/api';

async function loadInventory() {
    const response = await fetch(API_URL + '/items');
    const items = await response.json();
    const table = document.querySelector('#inventory-table tbody');
    table.innerHTML = '';
    items.forEach(item => {
        const row = `<tr>
            <td>${item.name}</td><td>${item.rfid_tag}</td>
            <td class="${item.quantity < 5 ? 'low-stock' : ''}">${item.quantity}</td>
            <td>${item.quantity < 5 ? 'LOW STOCK' : 'OK'}</td>
        </tr>`;
        table.innerHTML += row;
    });
}

async function simulateScan(action) {
    await fetch(API_URL + '/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tag_id: 'TAG003', action: action }) // Scans the stapler
    });
    loadInventory(); // Reload the table to show new quantity
}
// Load data when page opens
loadInventory();
