import datetime
import random
import uuid 
from pymongo import MongoClient
from demo_constants import (YEAR_TO_GENERATE, MONGO_URI, DATABASE_NAME, LOCATIONS)

# --- Configuration ---
ECOMM_APPLICATION_NAME = "ECommercePlatform"
ECOMM_BUSINESS_UNIT = "Online Sales"
ECOMM_OWNER = "Digital Commerce Team"


ECOMM_ANOMALIES = [
    {"date": "2024-01-20", "location": "Houston", "type": "DDoS Attack", "start_hour": 12, "end_hour": 20},
    {"date": "2024-02-08", "location": "San Antonio", "type": "Website Outage"},
    {"date": "2024-02-22", "location": "Houston", "type": "Website Outage"},
    {"date": "2024-03-10", "location": "Dallas-Fort Worth", "type": "DDoS Attack", "start_hour": 10, "end_hour": 14},
    {"date": "2024-03-25", "location": "San Antonio", "type": "Payment Processing Issues"},
    {"date": "2024-04-15", "location": "Austin", "type": "Website Outage"},
    {"date": "2024-04-16", "location": "Houston", "type": "Website Outage"},
    {"date": "2024-07-20", "location": "Dallas-Fort Worth", "type": "Unexpected Traffic Surge"},
    {"date": "2024-11-05", "location": "Houston", "type": "Payment Processing Issues"},
    {"date": "2024-11-06", "location": "Houston", "type": "Payment Processing Issues"},
    {"date": "2024-11-07", "location": "Austin", "type": "Payment Processing Issues"},
    # Website Outage - multiple days, specific location
    {"date": "2025-02-05", "location": "Houston", "type": "Website Outage"},
    {"date": "2025-02-07", "location": "Houston", "type": "Website Outage"},
    # Payment Processing Issues - period, noticeable drop
    {"date": "2025-03-20", "location": "San Antonio", "type": "Payment Processing Issues"},
    {"date": "2025-03-21", "location": "San Antonio", "type": "Payment Processing Issues"},
    {"date": "2025-03-22", "location": "San Antonio", "type": "Payment Processing Issues"},
    # New Anomaly: DDoS Attack (low volume, high errors/incidents for a short period)
    {"date": "2025-06-10", "location": "Dallas-Fort Worth", "type": "DDoS Attack", "start_hour": 10, "end_hour": 14},
    # Unexpected Traffic Surge - single random day, significant increase
    {"date": "2025-08-10", "location": "Frisco", "type": "Unexpected Traffic Surge"}, # Mid-summer random surge
    # New Anomaly: Third-Party API Failure (impacts specific functionality like search/recommendations, leading to moderate traffic drop)
    {"date": "2025-09-15", "location": "Plano", "type": "Third-Party API Failure"},
    {"date": "2025-09-16", "location": "Plano", "type": "Third-Party API Failure"},
    # New Anomaly: Flash Sale Gone Wrong (huge traffic surge, then rapid decline due to stock/site issues)
    {"date": "2025-10-20", "location": "Austin", "type": "Flash Sale Gone Wrong", "start_hour": 9, "end_hour": 11},
]

# --- Helper Functions ---
def is_weekend(date):
    return date.weekday() >= 5

def is_holiday_ecommerce(date):
    holidays = [
        datetime.date(2024, 1, 1),  # New Year's Day
        datetime.date(2024, 2, 14), # Valentine's Day
        datetime.date(2024, 5, 12), # Mother's Day
        datetime.date(2024, 5, 27), # Memorial Day
        datetime.date(2024, 6, 16), # Father's Day
        datetime.date(2024, 7, 4),  # Independence Day
        datetime.date(2024, 9, 2),  # Labor Day
        datetime.date(2024, 11, 28),# Thanksgiving
        datetime.date(2024, 11, 29),# Black Friday
        datetime.date(2024, 12, 2),  # Cyber Monday
        datetime.date(2024, 12, 25),# Christmas Day
        datetime.date(2025, 1, 1),   # New Year's Day
        datetime.date(2025, 2, 14),  # Valentine's Day
        datetime.date(2025, 2, 17),  # Presidents' Day
        datetime.date(2025, 5, 11),  # Mother's Day (2nd Sunday in May)
        datetime.date(2025, 5, 26),  # Memorial Day
        datetime.date(2025, 6, 15),  # Father's Day (3rd Sunday in June)
        datetime.date(2025, 7, 4),   # Independence Day
        datetime.date(2025, 9, 1),   # Labor Day
        datetime.date(2025, 11, 27), # Thanksgiving Day
        datetime.date(2025, 11, 28), # Black Friday (Day after Thanksgiving)
        datetime.date(2025, 12, 1),  # Cyber Monday (First Monday after Thanksgiving)
        datetime.date(2025, 12, 25), # Christmas Day
    ]
    return date in holidays

def get_weekly_pattern(date):
    weekday = date.weekday()  # Monday is 0, Sunday is 6
    if weekday < 4:  # Monday to Thursday
        return "Lower"
    elif weekday == 4:  # Friday
        return "Normal"
    else:  # Saturday and Sunday
        return "Peak"

def generate_resource_id(location):
    return f"{location.lower().replace(' ', '_')}-ecommerce-site"

# --- Data Generation Functions ---
def generate_application_data():
    return {
        "app_id": f"{ECOMM_APPLICATION_NAME.lower().replace(' ', '_')}-app-01",
        "name": ECOMM_APPLICATION_NAME,
        "description": "E-commerce platform for Texas retail businesses",
        "criticality": random.choice(["high", "medium"]),
        "business_unit": ECOMM_BUSINESS_UNIT,
        "business_service": "Online Sales Processing",
        "owner": ECOMM_OWNER,
        "creation_date": datetime.datetime(YEAR_TO_GENERATE, 1, 1),
        "last_modified": datetime.datetime.now()
    }

def generate_cloud_resource_data(location):
    resource_id = generate_resource_id(location)
    return {
        "resource_id": resource_id,
        "app_id": f"{ECOMM_APPLICATION_NAME.lower().replace(' ', '_')}-app-01",
        "resource_type": "E-commerce Website",
        "provider": random.choice(["aws", "azure", "gcp", "other"]),
        "region": random.choice(["reegion-1", "dc-2", "gcp", "other"]), # Assuming a general region
        "environment": "prod",
        "specifications": {
            "platform": "Custom",
            "language": "Python/JavaScript",
            "framework": "Django/React"
        },
        "creation_date": datetime.datetime(YEAR_TO_GENERATE, 1, 1),
        "last_modified": datetime.datetime.now()
    }

def generate_hourly_cost_data(date, hour, resource_id):
    timestamp = datetime.datetime.combine(date, datetime.time(hour, 0, 0))
    base_cost = 0.02
    if 10 <= hour < 22:  # Peak online shopping hours
        base_cost *= 1.3
    if is_weekend(date):
        base_cost *= 1.1
    if is_holiday_ecommerce(date):
        base_cost *= 1.5
    cost = round(random.uniform(base_cost * 0.9, base_cost * 1.1), 4)
    return {
        "resource_id": resource_id,  # Fix 1: Use string, not dict
        "timestamp": timestamp,
        "cost": cost
    }

def generate_incident_description(anomaly_type, location, affected_resource_id, timestamp):
    desc = f"Incident detected for {ECOMM_APPLICATION_NAME} at {location} at {timestamp.strftime('%Y-%m-%d %H:%M')}. "
    if anomaly_type == "Website Outage":
        desc += f"The e-commerce website for {location} is completely inaccessible. All online transactions are failing. Affected resource: {affected_resource_id}."
    elif anomaly_type == "Unexpected Traffic Surge":
        desc += f"Unanticipated and massive traffic surge detected on the e-commerce platform for {location}. System performance is degraded. Affected resource: {affected_resource_id}."
    elif anomaly_type == "Payment Processing Issues":
        desc += f"Significant decline in successful payment transactions observed for {location}. Customers are reporting payment failures. Investigation points to issues with the payment gateway. Affected resource: {affected_resource_id}."
    elif anomaly_type == "DDoS Attack":
        desc += f"Severe Distributed Denial of Service (DDoS) attack in progress impacting {location}'s e-commerce presence. High network load and service unavailability. Affected resource: {affected_resource_id}."
    elif anomaly_type == "Third-Party API Failure":
        desc += f"Critical third-party API (e.g., search, recommendations, shipping) failure impacting {location}'s online store. Customers may experience degraded functionality. Affected resource: {affected_resource_id}."
    elif anomaly_type == "Flash Sale Gone Wrong":
        desc += f"Flash sale initiated for {location} resulted in overwhelming traffic beyond system capacity, leading to rapid service degradation and transaction failures. Affected resource: {affected_resource_id}."
    else:
        desc += "An unspecified anomaly has been detected causing unexpected behavior."
    return desc

def generate_incident_data(date, hour, location, anomaly_type, resource_id):
    start_time = datetime.datetime.combine(date, datetime.time(hour, random.randint(0, 59), 0))
    resolution_duration = random.randint(60, 360)  # in minutes
    resolution_time = start_time + datetime.timedelta(minutes=resolution_duration)
    description = generate_incident_description(anomaly_type, location, resource_id, start_time)

    return {
        "incident_id": f"INC-{uuid.uuid4()}",  # Fix 5: Use uuid for uniqueness
        "app_id": f"{ECOMM_APPLICATION_NAME.lower().replace(' ', '_')}-app-01",
        "priority": random.choice([1, 2, 3]),
        "impact": random.choice(["high", "medium", "low"]),
        "start_time": start_time,
        "resolution_time": resolution_time,
        "duration_minutes": resolution_duration,
        "affected_resources": [resource_id],
        "estimated_cost_impact": round(random.uniform(50, 500), 2),
        "description": description
    }

def generate_problem_description(anomaly_type, location, open_date):
    desc = f"Problem identified affecting {ECOMM_APPLICATION_NAME} at {location} starting around {open_date.strftime('%Y-%m-%d %H:%M')}. Root cause analysis required. "
    if anomaly_type == "Website Outage":
        desc += "Recurring or prolonged website outages indicate a fundamental instability in the hosting infrastructure or core application. This problem ticket aims to identify and fix the underlying architectural flaw."
    elif anomaly_type == "DDoS Attack":
        desc += "Repeated or sustained DDoS attacks highlight a critical security vulnerability or inadequate network protection measures. This problem seeks to implement robust long-term DDoS mitigation strategies."
    elif anomaly_type == "Payment Processing Issues":
        desc += "Persistent payment processing failures suggest a systemic issue with the payment gateway integration, third-party vendor reliability, or internal transaction processing logic. This problem aims to ensure transaction integrity and reliability."
    elif anomaly_type == "Third-Party API Failure":
        desc += "Continuous failures of external APIs point to either an unstable third-party service or insufficient error handling and fallback mechanisms within our application. This problem will address external dependency resilience."
    elif anomaly_type == "Flash Sale Gone Wrong":
        desc += "The severe impact of a 'flash sale gone wrong' indicates a lack of scalability and load testing for high-demand events. This problem focuses on improving system elasticity and capacity planning for future promotions."
    else:
        desc += "Ongoing or major incidents indicate a deeper systemic issue requiring a problem investigation."
    return desc

def generate_problem_data(date, hour, location, anomaly_type):
    open_time = datetime.datetime.combine(date - datetime.timedelta(days=random.randint(1, 7)), datetime.time(random.randint(9, 17), random.randint(0, 59), 0))
    resolution_duration_days = random.randint(1, 5)
    resolution_time = datetime.datetime.now() + datetime.timedelta(days=resolution_duration_days)
    description = generate_problem_description(anomaly_type, location, open_time)
    return {
        "problem_id": f"PRB-{uuid.uuid4()}",  # Fix 5: Use uuid for uniqueness
        "app_id": f"{ECOMM_APPLICATION_NAME.lower().replace(' ', '_')}-app-01",
        "priority": random.choice([1, 2]),
        "impact": random.choice(["high", "medium"]),
        "open_date": open_time,
        "resolution_date": resolution_time,
        "related_incidents": [f"INC-{uuid.uuid4()}"],
        "estimated_cost_impact": round(random.uniform(100, 1000), 2),
        "description": description
    }

def generate_hourly_resource_utilization(date, hour, resource_id):
    timestamp = datetime.datetime.combine(date, datetime.time(hour, 0, 0))
    base_utilization = 0.1
    if 10 <= hour < 22:
        base_utilization += 0.2
    if is_weekend(date):
        base_utilization += 0.1
    if is_holiday_ecommerce(date):
        base_utilization += 0.3
    cpu_utilization = round(random.uniform(max(0.05, base_utilization - 0.15), min(0.95, base_utilization + 0.15)), 2)
    memory_utilization = round(random.uniform(max(0.1, base_utilization - 0.1), min(0.9, base_utilization + 0.1)), 2)
    return {
        "resource_id": resource_id,  # Fix 1: Use string, not dict
        "timestamp": timestamp,
        "cpu_utilization": cpu_utilization,
        "memory_utilization": memory_utilization
    }

def generate_ecommerce_data_for_year():
    year = YEAR_TO_GENERATE
    locations = LOCATIONS
    anomalies = ECOMM_ANOMALIES
    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)
    delta = datetime.timedelta(days=1)
    all_daily_data = {}
    anomaly_config = {}
    if anomalies:
        for anomaly in anomalies:
            date_obj = datetime.date.fromisoformat(anomaly['date'])
            if date_obj not in anomaly_config:
                anomaly_config[date_obj] = {}
            # Fix 9: Use dict with "types" and "hour" keys for anomaly_config
            if anomaly['location'] not in anomaly_config[date_obj]:
                anomaly_config[date_obj][anomaly['location']] = {"types": [], "hour": anomaly.get("hour")}
            anomaly_config[date_obj][anomaly['location']]["types"].append(anomaly['type'])
            if "hour" in anomaly:
                anomaly_config[date_obj][anomaly['location']]["hour"] = anomaly["hour"]

    for location in locations:
        all_daily_data[location] = []
        current_date = start_date
        while current_date <= end_date:
            daily_data = generate_daily_ecommerce_data(current_date, location, anomaly_config)
            all_daily_data[location].append(daily_data)
            current_date += delta
    return all_daily_data

def generate_daily_ecommerce_data(date, location, anomaly_config=None):
    transactions_base = 100
    weekly_pattern = get_weekly_pattern(date)

    if is_weekend(date):
        transactions_base *= 1.8
    elif weekly_pattern == "Normal":
        transactions_base *= 1.2

    if is_holiday_ecommerce(date):
        transactions_base *= 2.5
    elif date.month == 11 and date.day > 15:  # Pre-holiday shopping
        transactions_base *= 1.5
    elif date.month == 12 and date.day < 26:  # Christmas shopping
        transactions_base *= 1.7
    elif date.month == 1:  # Post-holiday sales
        transactions_base *= 1.3

    transactions = max(0, int(random.gauss(transactions_base, transactions_base * 0.25)))

    anomaly_types = []
    # Fix 9: Use new anomaly_config structure
    if anomaly_config and date in anomaly_config and location in anomaly_config[date]:
        anomaly_types = anomaly_config[date][location].get("types", [])
        for anomaly_type in anomaly_types:
            if anomaly_type == "Website Outage":
                transactions = 0
            elif anomaly_type == "Unexpected Traffic Surge":
                transactions *= 4
            elif anomaly_type == "Payment Processing Issues":
                transactions = max(0, int(transactions * 0.4))

    return {
        "location": location,
        "date": date.strftime("%Y-%m-%d"),
        "transaction_volume": transactions,
        "anomaly_types": anomaly_types
    }

def store_ecommerce_data_mongodb(daily_data):
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]

    # Application Collection
    applications_collection = db["applications"]
    app_data = generate_application_data()
    applications_collection.insert_one(app_data)
    print(f"Application data stored in 'applications' collection.")
    app_id = app_data['app_id']

    # Cloud Resources Collection
    cloud_resources_collection = db["cloud_resources"]
    resource_ids = {}
    for location in LOCATIONS:
        resource_data = generate_cloud_resource_data(location)
        cloud_resources_collection.insert_one(resource_data)
        resource_ids[location] = resource_data['resource_id']
    print(f"Cloud resource data stored in 'cloud_resources' collection.")

    # Cost Data Collection (hourly) - Fix 2: Use bulk insert
    cost_data_collection = db["cost_data"]
    start_date = datetime.date(YEAR_TO_GENERATE, 1, 1)
    end_date = datetime.date(YEAR_TO_GENERATE, 12, 31)
    delta = datetime.timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
        cost_docs = []
        for location, res_id in resource_ids.items():
            for hour in range(24):
                cost_data = generate_hourly_cost_data(current_date, hour, res_id)
                cost_docs.append(cost_data)
        if cost_docs:
            cost_data_collection.insert_many(cost_docs)
        current_date += delta
    print(f"Hourly cost data stored in 'cost_data' collection.")

    # Incident and Problem Collections
    incident_collection = db["incidents"]
    problem_collection = db["problems"]
    anomaly_config = {}
    if ECOMM_ANOMALIES:
        for anomaly in ECOMM_ANOMALIES:
            date_obj = datetime.date.fromisoformat(anomaly['date'])
            if date_obj not in anomaly_config:
                anomaly_config[date_obj] = {}
            # Fix 9: Use dict with "types" and "hour" keys for anomaly_config
            if anomaly['location'] not in anomaly_config[date_obj]:
                anomaly_config[date_obj][anomaly['location']] = {"types": [], "hour": anomaly.get("hour")}
            anomaly_config[date_obj][anomaly['location']]["types"].append(anomaly['type'])
            if "hour" in anomaly:
                anomaly_config[date_obj][anomaly['location']]["hour"] = anomaly["hour"]

    start_date = datetime.date(YEAR_TO_GENERATE, 1, 1)
    end_date = datetime.date(YEAR_TO_GENERATE, 12, 31)
    delta = datetime.timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
        for location, res_id in resource_ids.items():
            if current_date in anomaly_config and location in anomaly_config[current_date]:
                anomaly_types = anomaly_config[current_date][location].get("types", [])
                anomaly_hour = anomaly_config[current_date][location].get("hour")
                if anomaly_hour is None:
                    anomaly_hour = 12  # Default to noon if hour is missing or None
                for anomaly_type in anomaly_types:
                    if anomaly_type == "Website Outage":
                        for hour in range(24):
                            incident_data = generate_incident_data(current_date, hour, location, anomaly_type, res_id)
                            incident_collection.insert_one(incident_data)
                        problem_data = generate_problem_data(current_date, 12, location, anomaly_type)
                        problem_collection.insert_one(problem_data)
                        print(f"Incident and Problem created for {location} on {current_date} due to {anomaly_type}.")
                    elif anomaly_type == "Payment Processing Issues":
                        for hour in range(8, 22):
                            incident_data = generate_incident_data(current_date, hour, location, anomaly_type, res_id)
                            incident_collection.insert_one(incident_data)
                        print(f"Incident(s) created for {location} on {current_date} due to {anomaly_type}.")
                    elif anomaly_type == "Unexpected Traffic Surge":
                        incident_data = generate_incident_data(current_date, anomaly_hour, location, anomaly_type, res_id)
                        incident_collection.insert_one(incident_data)
                        print(f"Incident created for {location} on {current_date} due to {anomaly_type}.")
        current_date += delta
    print(f"Incident data stored in 'incidents' collection.")
    print(f"Problem data stored in 'problems' collection.")

    # Resource Utilization Collection (hourly) - Fix 2: Use bulk insert
    resource_utilization_collection = db["resource_utilization"]
    start_date = datetime.date(YEAR_TO_GENERATE, 1, 1)
    end_date = datetime.date(YEAR_TO_GENERATE, 12, 31)
    delta = datetime.timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
        util_docs = []
        for location, res_id in resource_ids.items():
            for hour in range(24):
                utilization_data = generate_hourly_resource_utilization(current_date, hour, res_id)
                util_docs.append(utilization_data)
        if util_docs:
            resource_utilization_collection.insert_many(util_docs)
        current_date += delta
    print(f"Resource utilization data stored in 'resource_utilization' collection.")

    client.close()

# Fix for Issue 1 (Option A): Call the correct function name
if __name__ == "__main__":
    daily_pos_data_2024 = generate_ecommerce_data_for_year()
    store_ecommerce_data_mongodb(daily_pos_data_2024)
    print("\nCMDB-like data generation and storage complete.")