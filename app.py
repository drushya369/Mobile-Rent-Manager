from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Base hourly rate
HOURLY_RATE = 50.0

# Core Data Structure: Dictionary mapping brand categories to fixed slots
inventory = {
    "APPLE":   {"Slot 1": None, "Slot 2": None, "Slot 3": None},
    "SAMSUNG": {"Slot 1": None, "Slot 2": None, "Slot 3": None},
    "GOOGLE":  {"Slot 1": None, "Slot 2": None},
    "ONEPLUS": {"Slot 1": None, "Slot 2": None}
}

# Stores native python datetime objects for active checkouts
time_logs = {}

# Temporary storage to hold receipt details to display on the next page reload
receipt_popup = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mobile Rent Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f1f5f9; font-family: system-ui, sans-serif; }
        .kiosk-header { background: #1e293b; color: white; padding: 1.5rem 0; }
        .brand-section { background: white; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }
    </style>
</head>
<body>

    <div class="kiosk-header text-center mb-4 shadow-sm">
        <h2 class="fw-bold">📱 Mobile Rent Manager</h2>
        <p class="lead mb-0 fs-6">Fixed-Slot Device Tracking Matrix</p>
    </div>

    <div class="container">
        <div class="row g-4">
            <div class="col-md-4">
                <div class="card border-0 shadow-sm p-4 bg-white">
                    <h5 class="fw-bold mb-3">Check-Out Device</h5>
                    <form method="POST" action="/rent">
                        <div class="mb-3">
                            <label class="form-label small fw-bold">Customer Name</label>
                            <input type="text" name="customer_name" class="form-control text-uppercase" required autocomplete="off">
                        </div>
                        <div class="mb-3">
                            <label class="form-label small fw-bold">Select Brand</label>
                            <select name="brand" class="form-select" required>
                                {% for brand in inventory_data.keys() %}
                                    <option value="{{ brand }}">{{ brand.capitalize() }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Allocate Slot</button>
                    </form>
                </div>
                <div class="card border-0 shadow-sm p-3 mt-3 bg-light text-center text-muted small fw-medium">
                    Pricing Metric: ₹{{ rate }}/hour
                </div>
            </div>

            <div class="col-md-8">
                {% for brand, slots in inventory_data.items() %}
                <div class="brand-section shadow-sm">
                    <h5 class="fw-bold text-secondary mb-3 border-bottom pb-2">{{ brand }} BAY</h5>
                    <div class="row g-3">
                        {% for slot_id, occupant in slots.items() %}
                        <div class="col-md-6">
                            <div class="p-3 border rounded d-flex justify-content-between align-items-center bg-white">
                                <div>
                                    <span class="badge {% if occupant %}bg-danger{% else %}bg-success{% endif %}">{{ slot_id }}</span>
                                    <div class="mt-2 small">
                                        {% if occupant %}
                                            <strong>👤 {{ occupant }}</strong><br>
                                            <span class="text-muted">Time: {{ logs_data[brand + '_' + slot_id].strftime('%H:%M:%S') }}</span>
                                        {% else %}
                                            <span class="text-success">✔ Available</span>
                                        {% endif %}
                                    </div>
                                </div>
                                {% if occupant %}
                                    <form method="POST" action="/withdraw_device">
                                        <input type="hidden" name="brand" value="{{ brand }}">
                                        <input type="hidden" name="slot_id" value="{{ slot_id }}">
                                        <button type="submit" class="btn btn-sm btn-outline-danger fw-bold">Withdraw</button>
                                    </form>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    {% if popup_text %}
    <script>
        alert("{{ popup_text|safe }}");
    </script>
    {% endif %}

</body>
</html>
"""

@app.route('/')
def home():
    global receipt_popup
    # Read the popup message text if it exists, then instantly clear it for the next round
    current_popup = receipt_popup
    receipt_popup = None 
    return render_template_string(HTML_TEMPLATE, inventory_data=inventory, logs_data=time_logs, rate=HOURLY_RATE, popup_text=current_popup)

@app.route('/rent', methods=['POST'])
def rent():
    customer = request.form.get('customer_name').strip().upper()
    brand = request.form.get('brand')

    target_slot = None
    for slot_id, occupant in inventory[brand].items():
        if occupant is None:
            target_slot = slot_id
            break

    if target_slot:
        inventory[brand][target_slot] = customer
        time_logs[f"{brand}_{target_slot}"] = datetime.now()

    return redirect(url_for('home'))

@app.route('/withdraw_device', methods=['POST'])
def withdraw_device():
    global receipt_popup
    brand = request.form.get('brand')
    slot_id = request.form.get('slot_id')

    if brand in inventory and slot_id in inventory[brand]:
        old_user = inventory[brand][slot_id]
        start_time = time_logs.get(f"{brand}_{slot_id}")
        
        # 1. CRITICAL: Wipes out the data state inside the Python Dictionary matrix instantly
        inventory[brand][slot_id] = None
        time_logs.pop(f"{brand}_{slot_id}", None)
        
        if start_time:
            # Calculate elapsed session metrics
            end_time = datetime.now()
            duration = end_time - start_time
            
            duration_seconds = duration.total_seconds()
            duration_minutes = duration_seconds / 60
            
            # Presentation scaling fallback logic
            if duration_minutes < 1.0:
                duration_minutes = 15.0  
                
            duration_hours = duration_minutes / 60
            calculated_fee = round(duration_hours * HOURLY_RATE, 2)
            
            # 2. Build explicit plain text for the browser alert window
            receipt_popup = f"--- RENTAL RECEIPT ---\\nCustomer: {old_user}\\nDevice: {brand} ({slot_id})\\nDuration: {round(duration_minutes, 1)} Minutes\\nTotal Fee: Rs. {calculated_fee}"

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
