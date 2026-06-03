from flask import Flask, render_template_string, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "smart_rent_secret_key"  # Required for the popup flash notification system

# Base operational parameters
HOURLY_RATE = 50.0

# Core Data Structure: Dictionary tracking discrete slot allocations
inventory = {
    "APPLE":   {"Slot #1": None, "Slot #2": None, "Slot #3": None},
    "SAMSUNG": {"Slot #1": None, "Slot #2": None, "Slot #3": None},
    "GOOGLE":  {"Slot #1": None, "Slot #2": None},
    "ONEPLUS": {"Slot #1": None, "Slot #2": None}
}

# Stores native python datetime objects for active checkouts
time_logs = {} 

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
        <p class="lead mb-0 fs-6">Dynamic Time & Fee Tracking Allocation Matrix</p>
    </div>

    <div class="container">
        
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="alert alert-success alert-dismissible fade show text-center shadow fw-bold fs-5 mb-4" role="alert">
                🎉 {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}

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
                    Pricing Metric: ₹{{ rate }}/hour (Billed proportionally per minute)
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
                                            <span class="text-muted">Checked Out: {{ logs_data[brand + '_' + slot_id].strftime('%H:%M:%S') }}</span>
                                        {% else %}
                                            <span class="text-success">✔ Available</span>
                                        {% endif %}
                                    </div>
                                </div>
                                {% if occupant %}
                                    <a href="/return/{{ brand }}/{{ slot_id }}" class="btn btn-sm btn-outline-danger fw-bold">Withdraw & Free</a>
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

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, inventory_data=inventory, logs_data=time_logs, rate=HOURLY_RATE)

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
        # Core Concept: Store the exact object instantiation time
        time_logs[f"{brand}_{target_slot}"] = datetime.now()
    else:
        flash(f"Error: No free slots currently available inside the {brand} sector.")

    return redirect(url_for('home'))

@app.route('/return/<brand>/<slot_id>')
def free(brand, slot_id):
    if brand in inventory and slot_id in inventory[brand]:
        old_user = inventory[brand][slot_id]
        start_time = time_logs.get(f"{brand}_{slot_id}")
        
        # Reset slot immediately to prevent concurrency deadlocks
        inventory[brand][slot_id] = None
        time_logs.pop(f"{brand}_{slot_id}", None)
        
        if start_time:
            # Calculate the explicit delta between allocation sessions
            end_time = datetime.now()
            duration = end_time - start_time
            
            duration_seconds = duration.total_seconds()
            duration_minutes = duration_seconds / 60
            
            # Presentation scaling fallback logic
            if duration_minutes < 1.0:
                duration_minutes = 15.0  # Scales to 15 mins for presentation calculation variability
                
            duration_hours = duration_minutes / 60
            calculated_fee = round(duration_hours * HOURLY_RATE, 2)
            
            # Format tracking details into the popup text
            receipt_msg = f"Device Returned Safely! | Customer: {old_user} | Active Time: {round(duration_minutes, 1)} Mins | Calculated Fee: ₹{calculated_fee}"
            flash(receipt_msg)

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
  
