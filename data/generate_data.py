import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import os

faker = Faker("en_IN")

NUM_ORDERS = 1000

CATEGORIES = ["Electronics","Home", "Kitchen", "Apparel", "Jewelry","Health", "Beauty", "Entertainment","Lifestyle","Kids","Watches"]
REGIONS = ["North", "South", "East", "West", "Central"]
STATUS = ["Delivered", "Delayed", "In Transit", "Out for Delivery", "Stale"]
COURIERS = ["Shipped by Amazon", "Bluedart","Delhivery", "Shadowfax", "Indian Postal Service","Ecom Express"]

DELAY_BIAS = {
    "Electronics": 0.40,
    "Home": 0.30,
    "Kitchen" : 0.30,
    "Apparel" : 0.28,
    "Jewelry" : 0.25,
    "Health" : 0.25,
    "Beauty" : 0.25,
    "Entertainment" : 0.25,
    "Lifestyle" : 0.20,
    "Kids" : 0.20,
    "Watches" : 0.20
}

REGION_BIAS = {
    "South":   0.35,
    "East":    0.28,
    "Central": 0.20,
    "West":    0.15,
    "North":   0.10
}

def generate_order(order_id):
    category = random.choice(CATEGORIES)
    region = random.choice(REGIONS)
    courier = random.choice(COURIERS)

    order_date = datetime.now() - timedelta(days=random.randint(1, 60))
    expected_days = random.randint(3, 7)
    expected_delivery = order_date + timedelta(days=expected_days)

    delay_chance = (DELAY_BIAS[category] + REGION_BIAS[region]) / 2
    is_delayed = random.random() < delay_chance


    if is_delayed:
        extra_days = random.randint(1,15)
        actual_delivery = expected_delivery + timedelta(days = extra_days)

        if extra_days >= 7:
            status = "Delayed"
            severity = "Critical"
        elif extra_days >= 5:
            status = "Delayed"
            severity = "High"
        elif extra_days >= 3:
            status = "Delayed"
            severity = "Medium"
        else:
            status = "Delayed"
            severity = "Low"

        if random.random() < 0.15:
            status = "Stale"
            actual_delivery = None
            severity = "High"

    else:
        early_days = random.randint(0, 2)
        actual_delivery = expected_delivery - timedelta(days=early_days)
        status = "Delivered"
        severity = "None"

    if random.random() < 0.10 and not is_delayed:
        status = "In Transit"
        actual_delivery = None
        severity = "None"

    price_range = {
        "Electronics": (1000, 80000),
        "Home": (300,100000),
        "Kitchen" : (100, 20000),
        "Apparel" : (250, 15000),
        "Jewelry" : (200, 10000),
        "Health" : (300, 25000),
        "Beauty" : (250, 10000),
        "Entertainment" : (200, 3000),
        "Lifestyle" : (300, 25000),
        "Kids" : (200, 20000),
        "Watches" : (300, 50000)
    }

    min_price, max_price = price_range[category]
    price = round(random.uniform(min_price, max_price), 2)


    if actual_delivery and actual_delivery > expected_delivery:
        delay_days = (actual_delivery - expected_delivery).days
    else:
        delay_days = 0


    return {
        "order_id":          f"ORD-{order_id:04d}",
        "customer_name":     faker.name(),
        "product":           f"{category} Item {random.randint(1, 100)}",
        "category":          category,
        "region":            region,
        "courier":           courier,
        "price":             price,
        "order_date":        order_date.strftime("%Y-%m-%d"),
        "expected_delivery": expected_delivery.strftime("%Y-%m-%d"),
        "actual_delivery":   actual_delivery.strftime("%Y-%m-%d") if actual_delivery else None,
        "status":            status,
        "severity":          severity,
        "delay_days":        delay_days
    }


print("Generating 1000 orders...")
orders = [generate_order(i + 1) for i in range(NUM_ORDERS)]

df = pd.DataFrame(orders)

os.makedirs("data", exist_ok=True)
df.to_csv("data/orders.csv", index=False)

print(f"\nGenerated {len(df)} orders")
print(f"\n--- Status Breakdown ---")
print(df["status"].value_counts())
print(f"\n--- Severity Breakdown ---")
print(df["severity"].value_counts())
print(f"\n--- Delay Rate by Category ---")
delayed = df[df["delay_days"] > 0]
print(delayed.groupby("category")["order_id"].count().sort_values(ascending=False))
print(f"\n--- Delay Rate by Region ---")
print(delayed.groupby("region")["order_id"].count().sort_values(ascending=False))
print(f"\nData saved to data/orders.csv ")