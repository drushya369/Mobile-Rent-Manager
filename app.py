from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = "smart_rent_secret_key"

# Fixed rate per hour in Rupees
HOURLY_RATE = 50.0

inventory = {
    "APPLE":   {"Slot 1": None, "Slot 2": None, "Slot 3": None},
    "SAMSUNG": {"Slot 1": None, "Slot 2": None, "Slot 3": None},
    "GOOGLE":  {"Slot 1": None, "Slot 2": None},
    "ONEPLUS": {"Slot 1": None, "Slot 2": None}
}

# Stores the exact system timestamp when the rent starts
time_logs = {}
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
                    Pricing Metric: ₹{{ rate }}/hour <br>
                    <span class="text-success fw-bold">(Demo Mode: 1 Second = 1 Hour Billed)</span>
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
                                            <span class="text-muted">Status: Billed Active</span>
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
    current_popup = receipt_popup
    receipt_popup = None 
    return render_template_string(HTML_TEMPLATE, inventory_data=inventory, rate=HOURLY_RATE, popup_text=current_popup)

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
        # Track the exact epoch starting time in seconds
        time_logs[f"{brand}_{target_slot}"] = time.time()

    return redirect(url_for('home'))

@app.route('/withdraw_device', methods=['POST'])
def withdraw_device():
    global receipt_popup
    brand = request.form.get('brand')
    slot_id = request.form.get('slot_id')

    if brand in inventory and slot_id in inventory[brand]:
        old_user = inventory[brand][slot_id]
        start_time = time_logs.pop(f"{brand}_{slot_id}", None)
        
        # Free the slot instantly
        inventory[brand][slot_id] = None
        
        if start_time is not None:
            end_time = time.time()
            # Calculate the total seconds passed since checkout
            elapsed_seconds = end_time - start_time
            
            # SIMULATION LOGIC: We treat 1 real second as 1 hour of usage 
            # to show the dynamic pricing calculation scale instantly during your viva.
            simulated_hours = elapsed_seconds
            
            # Enforce a minimum scale so it never reads zero
            if simulated_hours < 0.1:
                simulated_hours = 0.5
                
            calculated_fee = round(simulated_hours * HOURLY_RATE, 2)
            
            # Display accurate simulated metrics dynamically
            receipt_popup = f"--- RENTAL RECEIPT ---\\nCustomer: {old_user}\\nDevice: {brand} ({slot_id})\\nSimulated Duration: {round(simulated_hours, 2)} Hours\\nTotal Charges: Rs. {calculated_fee}"

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
