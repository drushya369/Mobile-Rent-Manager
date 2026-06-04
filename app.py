from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = "smart_rent_secret_key"

# Brand-Specific Pricing Configuration (Rupees per Hour)
BRAND_RATES = {
    "APPLE": 100.0,
    "SAMSUNG": 70.0,
    "GOOGLE": 50.0,
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
        .kiosk-header { background: #1e293b; color: white; padding: 1.5rem 0; }
        .brand-section { background: white; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }
        .menu-card { background: #fff; border-radius: 8px; border-left: 5px solid #3b82f6; }
    </style>
</head>
<body>

    <div class="kiosk-header text-center mb-4 shadow-sm">
        <h2 class="fw-bold">📱 Mobile Rent Manager</h2>
        <p class="lead mb-0 fs-6">Multi-Tariff Fixed-Slot Tracking Matrix
