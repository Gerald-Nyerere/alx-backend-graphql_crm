#!/usr/bin/env python3
"""
Script: send_order_reminders.py
Purpose: Query recent orders (last 7 days) via GraphQL and log them.
"""

import requests
from datetime import datetime, timedelta

GRAPHQL_URL = "http://localhost:8000/graphql"

LOG_FILE = "/tmp/order_reminders_log.txt"

seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

query = """
query {
  orders(orderDate_Gte: "%s") {
    id
    customer {
      email
    }
  }
}
""" % seven_days_ago

response = requests.post(GRAPHQL_URL, json={"query": query})
data = response.json()

with open(LOG_FILE, "a") as log_file:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    orders = data.get("data", {}).get("orders", [])
    for order in orders:
        order_id = order.get("id")
        email = order.get("customer", {}).get("email")
        log_file.write(f"[{timestamp}] Order ID: {order_id}, Customer Email: {email}\n")

print("Order reminders processed!")
