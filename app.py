from flask import Flask, render_template_string, request, redirect, url_for
import time

app = Flask(__name__)
app.secret_key = "smart_rent_premium_key"

# Individual Pricing Profile Per Brand (Rupees per Hour)
BRAND_RATES = {
    "APPLE": 120.0,
    "SAMSUNG": 80.0,
    "GOOGLE": 60.0,
    "ONEPLUS": 40.0
}

inventory = {
    "APPLE":   {"Slot 1": None, "Slot 2": None, "Slot 3": None},
    "SAMSUNG": {"Slot 1": None, "Slot 2": None, "Slot 3": None},
    "GOOGLE":  {"Slot 1": None, "Slot 2": None},
    "ONEPLUS": {"Slot 1": None, "Slot 2": None}
}

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
        .kiosk-header { background: #0f172a; color: white; padding: 1.5rem 0; }
        .brand-section { background: white; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }
        .rate-badge { font-size: 0.8rem; font-weight: bold; padding: 4px 8px; border-radius: 4px; background: #e2e8f0; color: #334155; }
    </style>
</head>
<body>

    <div class="kiosk-header text-center mb-4 shadow-sm">
        <h2 class="fw-bold">📱 Mobile Rent Manager</h2>
        <p class="lead mb-0 fs-6">Dynamic Multi-Tariff Allocation Engine</p>
    </div>

    <div class="container">
        <div class="row g-4">
            
            <div class="col-md-4">
                
                <div class="card border-0 shadow-sm p-4 bg-white mb-4">
                    <h5 class="fw-bold mb-3">Check-Out Device</h5>
                    <form method="POST" action="/rent">
                        <div class="mb-3">
                            <label class="form-label small fw-bold">Customer Name</label>
                            <input type="text" name="customer_name" class="form-control text-uppercase" required autocomplete="off">
                        </div>
                        <div class="mb-3">
                            <label class="form-label small fw-bold">Select Target Brand</label>
                            <select name="brand" class="form-select" required>
                                {% for brand in inventory_data.keys() %}
                                    <option value="{{ brand }}">{{ brand.capitalize() }} (₹{{ rates[brand] }}/hr)</option>
                                {% endfor %}
                            </select>
                        </div>
                        <button type="submit" class="btn btn-primary w-100 fw-bold">Allocate Slot Array</button>
                    </form>
                </div>

                <div class="card border-0 shadow-sm p-3 bg-white">
                    <h6 class="fw-bold text-primary mb-2">📋 LIVE BRAND TARIFFS</h6>
                    <div class="small">
                        {% for b_name, b_rate in rates.items() %}
                        <div class="d-flex justify-content-between py-1 border-bottom">
                            <span class="fw-semibold text-secondary">{{ b_name }}</span>
                            <span class="fw-bold text-dark">₹{{ b_rate }}/hr</span>
                        </div>
                        {% endfor %}
                    </div>
                    <div class="text-center text-success fw-bold small mt-2" style="font-size: 0.75rem;">
                        ⏱️ LIVE TIMELINE: 5 REAL SECONDS = 1 MINUTE RENTED
                    </div>
                </div>
            </div>

            <div class="col-md-8">
                {% for brand, slots in inventory_data.items() %}
                <div class="brand-section shadow-sm">
                    <h5 class="fw-bold text-secondary mb-3 border-bottom pb-2 d-flex justify-content-between align-items-center">
                        <span>{{ brand }} BAY</span>
                        <span class="rate-badge">Rate: ₹{{ rates[brand] }}/hr</span>
                    </h5>
                    <div class="row g-3">
                        {% for slot_id, occupant in slots.items() %}
                        <div class="col-md-6">
                            <div class="p-3 border rounded d-flex justify-content-between align-items-center bg-white">
                                <div>
                                    <span class="badge {% if occupant %}bg-danger{% else %}bg-success{% endif %}">{{ slot_id }}</span>
                                    <div class="mt-2 small">
                                        {% if occupant %}
                                            <strong>👤 {{ occupant }}</strong><br>
                                            <span class="text-danger fw-bold">Status: Billing Active</span>
                                        {% else %}
                                            <span class="text-success">✔ Vacant</span>
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
    return render_template_string(HTML_TEMPLATE, inventory_data=inventory, rates=BRAND_RATES, popup_text=current_popup)

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
        
        # Free the slot array instantly
        inventory[brand][slot_id] = None
        
        if start_time is not None:
            real_seconds_elapsed = time.time() - start_time
            
            # FIXED MODIFIER: 1 Second = 0.2 Minutes (5 Seconds = 1 Minute)
            simulated_minutes_used = real_seconds_elapsed * 0.2
            
            # Safe minimum baseline so a super-fast click shows a real charge
            if simulated_minutes_used < 1.0:
                simulated_minutes_used = 1.5
                
            simulated_hours = simulated_minutes_used / 60.0
            
            # Brand-specific lookup matrix
            specific_hourly_rate = BRAND_RATES.get(brand, 40.0)
            calculated_fee = round(simulated_hours * specific_hourly_rate, 2)
            
            receipt_popup = (
                f"--- TRANSACT RENTAL RECEIPT ---\\n"
                f"Customer Name : {old_user}\\n"
                f"Assigned Asset: {brand} ({slot_id})\\n"
                f"Applied Tariff: Rs. {specific_hourly_rate}/hr\\n"
                f"Computed Time : {round(simulated_minutes_used, 1)} Minutes\\n"
                f"---------------------------------\\n"
                f"FINAL AMOUNT  : Rs. {calculated_fee}"
            )

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
