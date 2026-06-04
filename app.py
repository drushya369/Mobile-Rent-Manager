from flask import Flask, render_template_string, request, redirect, url_for
import time

app = Flask(__name__)
app.secret_key = "smart_rent_premium_key"

# 1. Distinct Pricing Profiles (Rupees per Hour)
BRAND_RATES = {
    "APPLE": 120.0,
    "SAMSUNG": 80.0,
    "GOOGLE": 60.0,
    "ONEPLUS": 40.0
}

# 2. Strict Inventory Slot Matrices
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
        .rate-card { border-left: 4px solid #2563eb; background: #fff; }
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
                
                <div class="card rate-card border-0 shadow-sm p-3 mb-4">
                    <h6 class="fw-bold text-primary mb-2">📋 LIVE BRAND TARIFFS</h6>
                    <div class="small">
                        {% for b_name, b_rate in rates.items() %}
                        <div class="d-flex justify-content-between py-1 border-bottom">
                            <span class="fw-semibold text-secondary">{{ b_name }}</span>
                            <span class="fw-bold text-dark">₹{{ b_rate }}/hr</span>
                        </div>
                        {% endfor %}
                    </div>
                    <div class="text-center text-danger fw-bold small mt-2" style="font-size: 0.72rem;">
                        ⚡ SIMULATION NODE: 1 REAL SECOND = 2.6 MINUTES RENTED
                    </div>
                </div>

                <div class="card border-0 shadow-sm p-4 bg-white">
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
            </div>

            <div class="col-md-8">
                {% for brand, slots in inventory_data.items() %}
                <div class="brand-section shadow-sm">
                    <h5 class="fw-bold text-secondary mb-3 border-bottom pb-2">
                        {{ brand }} BAY 
                        <span class="badge bg-dark float-end fs-6">Base: ₹{{ rates[brand] }}/hr</span>
                    </h5>
                    <div class="row g-3">
                        {% for slot_id, occupant in slots.items() %}
                        <div class="col-md-6">
                            <div class="p-3 border rounded d-flex justify-content-between align-
