import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Configuration for 100 records
NUM_RECORDS = 100
OUTPUT_FILE = "server_inventory.xlsx"

data = []

print(f"[*] Generating {NUM_RECORDS} records...")

for _ in range(NUM_RECORDS):
    # Logic to support the conditional masking test
    # We want some environments to be "Production" and others "Dev" or "Staging"
    environment = random.choice(['Production', 'Staging', 'Development'])
    
    # Generate realistic data
    record = {
        "Server_Name": f"{fake.hostname()}-{random.randint(100, 999)}",
        "IP_Address": fake.ipv4(),
        "Cost": round(random.uniform(50.00, 5000.00), 2),
        "Last_Patch_Date": fake.date_between(start_date='-1y', end_date='today'),
        "Admin_Password": fake.password(length=12),
        "Is_Active": random.choice([True, False]),
        "Owner_Email": fake.email(),
        "Environment": environment
    }
    data.append(record)

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
try:
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"[+] Successfully created '{OUTPUT_FILE}' with {len(df)} rows.")
    print("    Columns included:")
    for col in df.columns:
        print(f"    - {col}")
except Exception as e:
    print(f"[!] Error saving file: {e}")