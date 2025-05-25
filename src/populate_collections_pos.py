import datetime
import random
import uuid
from pymongo import MongoClient  # Removed unused import 'json'
from demo_constants import (YEAR_TO_GENERATE, MONGO_URI, DATABASE_NAME, LOCATIONS)

POS_APPLICATION_NAME = "RetailPOS"
POS_BUSINESS_UNIT = "Retail Operations"
POS_OWNER = "IT Retail Team"


POS_ANOMALIES = [
    {"date": "2024-01-01", "location": "Austin", "type": "Network Connectivity Loss", "start_hour": 10, "end_hour": 13},
    {"date": "2024-01-20", "location": "Corpus Christi", "type": "System Malfunction", "hour": 14},
    {"date": "2024-02-20", "location": "Austin", "type": "System Malfunction"},
    {"date": "2024-02-22", "location": "Houston", "type": "Hardware Failure", "hour": 12},
    {"date": "2024-02-22", "location": "Houston", "type": "Employee Inefficiency/Device Issue"},
    {"date": "2024-02-25", "location": "The Woodlands", "type": "Hardware Failure", "hour": 10},
    {"date": "2024-02-28", "location": "Austin", "type": "Network Connectivity Loss", "start_hour": 11, "end_hour": 12},
    {"date": "2024-03-01", "location": "Plano", "type": "System Malfunction"},
    {"date": "2024-03-04", "location": "Houston", "type": "Employee Inefficiency/Device Issue"},
    {"date": "2024-03-21", "location": "Austin", "type": "System Malfunction"},
    {"date": "2024-04-01", "location": "Houston", "type": "Employee Inefficiency/Device Issue"},
    {"date": "2024-04-11", "location": "Plano", "type": "Employee Inefficiency/Device Issue"},
    {"date": "2024-04-15", "location": "Austin", "type": "System Malfunction"},
    {"date": "2024-05-05", "location": "Plano", "type": "Unauthorized Shutdown"},
    {"date": "2024-05-15", "location": "Plano", "type": "Unauthorized Shutdown"},
    {"date": "2024-05-27", "location": "Dallas-Fort Worth", "type": "Peak Event Impact"}, # Memorial Day
    {"date": "2024-06-16", "location": "Dallas-Fort Worth", "type": "Peak Event Impact"}, # Father's Day
    {"date": "2024-07-15", "location": "Houston", "type": "Employee Inefficiency/Device Issue"},
    {"date": "2024-07-16", "location": "Houston", "type": "Employee Inefficiency/Device Issue"},
    {"date": "2024-07-17", "location": "Houston", "type": "Employee Inefficiency/Device Issue"},
    {"date": "2024-10-26", "location": "San Antonio", "type": "Significant Technical Problem"},
    {"date": "2024-11-28", "location": "Dallas-Fort Worth", "type": "Peak Event Impact", "hour": 10}, # Black Friday
    # System Malfunction (zero transactions) - few days, specific location
    {"date": "2025-01-26", "location": "Corpus Christi", "type": "System Malfunction", "hour": 10},
    # NEW: Network Connectivity Loss (impacts only some transactions, higher average time)
    {"date": "2025-03-01", "location": "Austin", "type": "Network Connectivity Loss", "start_hour": 13, "end_hour": 16},
    # Employee Inefficiency/Device Issue (gradual increase in transaction time) - period
    {"date": "2025-04-10", "location": "Plano", "type": "Employee Inefficiency/Device Issue"},
    {"date": "2025-04-12", "location": "Plano", "type": "Employee Inefficiency/Device Issue"},
    # NEW: Hardware Failure (Terminal non-responsive, zero transactions on one specific terminal)
    {"date": "2025-05-20", "location": "The Woodlands", "type": "Hardware Failure", "hour": 10},
    # Significant Technical Problem (high error count, low volume) - specific day, specific terminal
    {"date": "2025-07-10", "location": "McKinney", "type": "Significant Technical Problem", "hour": 15},
    # Unauthorized Shutdown (zero active hours) - specific day, specific location
    {"date": "2025-09-05", "location": "Denton", "type": "Unauthorized Shutdown", "hour": 11},
    # NEW: Software Update Issue (intermittent errors and slow transactions)
    {"date": "2025-10-01", "location": "San Antonio", "type": "Software Update Issue", "start_hour": 9, "end_hour": 13},
    # Peak Event Impact - on key shopping days
    {"date": "2025-11-27", "location": "Dallas-Fort Worth", "type": "Peak Event Impact", "hour": 10}, # Black Friday
    {"date": "2025-12-24", "location": "Houston", "type": "Peak Event Impact", "hour": 12}, # Christmas Eve
]

# --- Helper Functions ---
def is_weekend(date):
    return date.weekday() >= 5

def is_holiday(date):
    holidays = [
        datetime.date(2024, 1, 1), datetime.date(2024, 2, 14), datetime.date(2024, 5, 12),
        datetime.date(2024, 5, 27), datetime.date(2024, 6, 16),
        datetime.date(2024, 7, 4), datetime.date(2024, 9, 2), datetime.date(2024, 10, 31),
        datetime.date(2024, 11, 28), datetime.date(2024, 11, 29), datetime.date(2024, 12, 25),
        datetime.date(2025, 1, 1), datetime.date(2025, 2, 14), 
        datetime.date(2025, 2, 17), datetime.date(2025, 5, 11),
        datetime.date(2025, 5, 26), datetime.date(2025, 6, 15),
        datetime.date(2025, 7, 4), datetime.date(2025, 9, 1), datetime.date(2025, 10, 31),
        datetime.date(2025, 11, 27), datetime.date(2025, 11, 28), datetime.date(2025, 12, 25)
    ]
    return date in holidays

def get_weekly_pattern(date):
    weekday = date.weekday()
    if weekday < 4: return "Lower"
    elif weekday == 4: return "Normal"
    else: return "Peak"

def generate_resource_id(location):
    return f"{location.lower().replace(' ', '_')}-pos-terminal-{random.randint(100, 999)}"

## --- Data Generation Functions ---
def generate_application_data(year=2024):
    return {
        "app_id": f"{POS_APPLICATION_NAME.lower().replace(' ', '_')}-app-01",
        "name": POS_APPLICATION_NAME,
        "description": "Point of Sale application for Texas retail locations",
        "criticality": random.choice(["high", "medium"]),
        "business_unit": POS_BUSINESS_UNIT,
        "business_service": "Retail Transaction Processing",
        "owner": POS_OWNER,
        "creation_date": datetime.datetime(year, 1, 1),
        "last_modified": datetime.datetime.now()
    }

def generate_cloud_resource_data(location):
    resource_id = generate_resource_id(location)
    return {
        "resource_id": resource_id,
        "app_id": f"{POS_APPLICATION_NAME.lower().replace(' ', '_')}-app-01",
        "resource_type": "POS Terminal",
        "provider": "other",
        "region": "us-central-1", # Assuming a general region
        "environment": "prod",
        "specifications": {
            "os": random.choice(["Windows", "Linux"]),
            "cpu": "ARMv7",
            "memory_gb": 4,
            "storage_gb": 128
        },
        "creation_date": datetime.datetime(YEAR_TO_GENERATE, 1, 1),
        "last_modified": datetime.datetime.now()
    }

def generate_hourly_cost_data(date, hour, resource_id):
    timestamp = datetime.datetime.combine(date, datetime.time(hour, 0, 0))
    base_cost = 0.01
    if 10 <= hour < 20:
        base_cost *= 1.5
    if get_weekly_pattern(date) == "Peak":
        base_cost *= 1.2
    cost = round(random.uniform(base_cost * 0.8, base_cost * 1.2), 4)
    return {
        "resource_id": resource_id,  # FIXED: Use string, not dict
        "timestamp": timestamp,
        "cost": cost
    }

def generate_incident_description_pos(anomaly_type, location, affected_resource_id, timestamp):
    desc = f"Incident detected for {POS_APPLICATION_NAME} at {location} location, affecting terminal {affected_resource_id} at {timestamp.strftime('%Y-%m-%d %H:%M')}. "
    if anomaly_type == "System Malfunction":
        desc += f"The POS terminal {affected_resource_id} is reporting a complete system malfunction, rendering it inoperable. Transactions cannot be processed."
    elif anomaly_type == "Peak Event Impact":
        desc += f"During a peak retail event, the POS system at {location} experienced extreme load. This incident indicates potential performance degradation or temporary transaction failures due to high volume on terminal {affected_resource_id}."
    elif anomaly_type == "Employee Inefficiency/Device Issue":
        desc += f"Average transaction times on terminal {affected_resource_id} have significantly increased, indicating potential employee training needs or a subtle hardware/software issue impacting workflow."
    elif anomaly_type == "Significant Technical Problem":
        desc += f"Terminal {affected_resource_id} is logging a high volume of transaction and system errors, leading to low transaction success rates. This suggests a critical technical issue with the device or its network connection."
    elif anomaly_type == "Unauthorized Shutdown":
        desc += f"POS terminal {affected_resource_id} at {location} was unexpectedly shut down or logged out during normal operating hours, disrupting service."
    elif anomaly_type == "Network Connectivity Loss":
        desc += f"Intermittent or complete loss of network connectivity detected for POS terminal {affected_resource_id}. This is causing transaction delays and potential failures for payment processing."
    elif anomaly_type == "Hardware Failure":
        desc += f"POS terminal {affected_resource_id} has experienced a critical hardware failure (e.g., touchscreen unresponsive, card reader broken), rendering it unusable for transactions."
    elif anomaly_type == "Software Update Issue":
        desc += f"Post-software update, POS terminal {affected_resource_id} is exhibiting intermittent errors, slow response times, and occasional freezes during transaction processing."
    else:
        desc += "An unspecified anomaly has been detected causing unusual POS behavior."
    return desc

def generate_incident_data(date, hour, location, anomaly_type, resource_id):
 
    start_time = datetime.datetime.combine(date, datetime.time(hour, random.randint(0, 59), random.randint(0, 59)))
    
    # Define incident lifecycle timings
    # New -> In Progress (short delay)
    in_progress_time = start_time + datetime.timedelta(minutes=random.randint(5, 15))
    # In Progress -> On Hold (optional, random chance)
    on_hold_time = None
    on_hold_reason = None
    if random.random() < 0.2 and anomaly_type in ["Hardware Failure", "Network Connectivity Loss"]: # 20% chance for some types
        on_hold_time = in_progress_time + datetime.timedelta(minutes=random.randint(30, 90))
        on_hold_reason = random.choice(["Awaiting Vendor", "Awaiting Parts Delivery", "Awaiting Network Team"])
        
    # Resolution Time
    resolution_duration_minutes = random.randint(60, 360) # Total duration for resolution
    if on_hold_time:
        # If on hold, extend resolution by hold duration
        hold_duration = random.randint(60, 240)
        resolution_duration_minutes += hold_duration
        resolution_time = on_hold_time + datetime.timedelta(minutes=hold_duration + random.randint(30,60)) # Time after hold + work
    else:
        resolution_time = start_time + datetime.timedelta(minutes=resolution_duration_minutes)

    # Resolution needs to be after start and in progress. If it's in the future, set to current time
    if resolution_time > datetime.datetime.now():
        resolution_time = datetime.datetime.now()

    # Closed Time (after resolution, typically 1-3 days later)
    close_time = resolution_time + datetime.timedelta(days=random.randint(1, 3))
    # Or Canceled?
    is_canceled = False
    if random.random() < 0.05: # 5% chance of being cancelled
        is_canceled = True
        close_time = start_time + datetime.timedelta(minutes=random.randint(30, 120)) # Cancelled quickly
        resolution_time = None # Not resolved

    # Build state history
    state_history = []
    state_history.append({"state": "New", "timestamp": start_time})
    state_history.append({"state": "In Progress", "timestamp": in_progress_time})
    if on_hold_time:
        state_history.append({"state": "On Hold", "timestamp": on_hold_time, "reason": on_hold_reason})
        state_history.append({"state": "In Progress", "timestamp": on_hold_time + datetime.timedelta(minutes=random.randint(5,15))}) # Back to in progress after hold

    if not is_canceled:
        state_history.append({"state": "Resolved", "timestamp": resolution_time})
        state_history.append({"state": "Closed", "timestamp": close_time})
    else:
        state_history.append({"state": "Canceled", "timestamp": close_time}) # If canceled, it just goes to canceled

    # Calculate metrics
    time_to_resolve_minutes = (resolution_time - start_time).total_seconds() / 60 if resolution_time and not is_canceled else None
    time_to_close_minutes = (close_time - start_time).total_seconds() / 60 if close_time else None


    description = generate_incident_description_pos(anomaly_type, location, resource_id, start_time)
    
    return {
        "incident_id": f"INC-{start_time.strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
        "app_id": f"{POS_APPLICATION_NAME.lower().replace(' ', '_')}-app-01",
        "priority": random.choice([1, 2, 3]), # Can be linked to anomaly severity
        "impact": random.choice(["high", "medium", "low"]),
        "start_time": start_time,
        "resolution_time": resolution_time,
        "duration_minutes": resolution_duration_minutes,
        "affected_resources": [resource_id] if resource_id else [],
        "estimated_cost_impact": round(random.uniform(20, 200), 2),
        "anomaly_type": anomaly_type,
        "description": description,
        "state_history": state_history,
        "metrics": {
            "time_to_resolve_minutes": time_to_resolve_minutes,
            "time_to_close_minutes": time_to_close_minutes
        }
    }
   

def generate_problem_description_pos(anomaly_type, location, open_date):
    desc = f"Problem identified affecting {POS_APPLICATION_NAME} at {location} starting around {open_date.strftime('%Y-%m-%d %H:%M')}. Root cause analysis required. "
    if anomaly_type == "System Malfunction":
        desc += "Persistent system malfunctions across multiple POS terminals or recurring issues on a single terminal suggest a deeper software bug or a systemic configuration error requiring a formal problem investigation."
    elif anomaly_type == "Employee Inefficiency/Device Issue":
        desc += "A trend of increased transaction times indicates either a widespread device performance degradation, a need for revised employee training, or a flaw in the POS workflow itself. This problem will investigate the root cause."
    elif anomaly_type == "Significant Technical Problem":
        desc += "Frequent high error counts and low transaction volumes point to a critical underlying technical issue with the POS infrastructure, such as network instability, server problems, or database corruption, impacting multiple terminals."
    elif anomaly_type == "Unauthorized Shutdown":
        desc += "Repeated unauthorized shutdowns of POS terminals indicate potential security vulnerabilities, power management issues, or a lack of adherence to operational procedures. This problem will address the cause and prevention."
    elif anomaly_type == "Network Connectivity Loss":
        desc += "Ongoing or widespread network connectivity issues for POS terminals suggest a critical failure in the store's local network infrastructure (router, switch, cabling) or ISP service, impacting transaction processing."
    elif anomaly_type == "Hardware Failure":
        desc += "A pattern of hardware failures (e.g., card readers, touchscreens) across different POS terminals, potentially of the same model, indicates a manufacturing defect or a widespread environmental issue. This problem will address long-term hardware reliability."
    elif anomaly_type == "Software Update Issue":
        desc += "Widespread or recurring issues following a software update point to a critical defect in the update package, insufficient testing, or compatibility problems with existing hardware/peripherals. This problem will ensure stable software deployments."
    else:
        desc += "Ongoing or major incidents indicate a deeper systemic issue requiring a problem investigation."
    return desc

def generate_problem_data(date, hour, location, anomaly_type):
    open_time = datetime.datetime.combine(date - datetime.timedelta(days=random.randint(1, 7)), datetime.time(random.randint(9, 17), random.randint(0, 59), 0))
    resolution_duration_days = random.randint(1, 5)
    resolution_time = datetime.datetime.now() + datetime.timedelta(days=resolution_duration_days)
    description = generate_problem_description_pos(anomaly_type, location, open_time)
    return {
        "problem_id": f"PRB-{uuid.uuid4()}",  # FIXED: Use uuid for uniqueness
        "app_id": f"{POS_APPLICATION_NAME.lower().replace(' ', '_')}-app-01",
        "priority": random.choice([1, 2]),
        "impact": random.choice(["high", "medium"]),
        "open_date": open_time,
        "resolution_date": resolution_time,
        "related_incidents": [f"INC-{uuid.uuid4()}"],
        "estimated_cost_impact": round(random.uniform(50, 500), 2),
        "description": description
    }

def generate_hourly_resource_utilization(date, hour, resource_id):
    timestamp = datetime.datetime.combine(date, datetime.time(hour, 0, 0))
    base_utilization = 0.2
    if 10 <= hour < 20:
        base_utilization += 0.3
    if get_weekly_pattern(date) == "Peak":
        base_utilization += 0.15
    cpu_utilization = round(random.uniform(max(0.05, base_utilization - 0.2), min(0.95, base_utilization + 0.2)), 2)
    memory_utilization = round(random.uniform(max(0.1, base_utilization - 0.15), min(0.9, base_utilization + 0.15)), 2)
    return {
        "resource_id": resource_id,  # FIXED: Use string, not dict
        "timestamp": timestamp,
        "cpu_utilization": cpu_utilization,
        "memory_utilization": memory_utilization
    }

def generate_hourly_pos_data(date, hour, location, anomaly_config=None):
    transactions_base = 5
    time_base = 30
    error_base = 0

    weekly_pattern = get_weekly_pattern(date)
    is_peak_time = 10 <= hour < 20

    if is_weekend(date) and is_peak_time:
        transactions_base *= 2
        time_base *= 1.1
    elif is_weekend(date):
        transactions_base *= 1.5
    elif is_peak_time and weekly_pattern == "Normal":
        transactions_base *= 1.3
    elif is_peak_time:
        transactions_base *= 1.1

    if is_holiday(date):
        transactions_base *= 2.5
        time_base *= 1.2

    month = date.month
    if month in [11, 12] and is_peak_time:
        transactions_base *= 1.4
    elif month in [6, 7, 8] and is_peak_time:
        transactions_base *= 0.8

    transactions = max(0, int(random.gauss(transactions_base, transactions_base * 0.3)))
    avg_transaction_time = max(10, int(random.gauss(time_base, time_base * 0.2)))
    error_count = max(0, int(random.expovariate(0.05))) # Higher rate for hourly

    anomaly_types = []
    if anomaly_config and date in anomaly_config and location in anomaly_config[date] and anomaly_config[date][location].get("hour") == hour:
        anomaly_types = anomaly_config[date][location].get("types", [])
        for anomaly_type in anomaly_types:
            if anomaly_type == "System Malfunction":
                transactions = 0
            elif anomaly_type == "Peak Event Impact":
                transactions *= 5
                avg_transaction_time *= 1.3
            elif anomaly_type == "Employee Inefficiency/Device Issue":
                avg_transaction_time *= (1 + random.uniform(0.3, 0.7))
            elif anomaly_type == "Significant Technical Problem":
                error_count = int(random.uniform(10, 30))
                transactions = max(0, int(transactions * 0.2))
            elif anomaly_type == "Unauthorized Shutdown":
                transactions = 0
                avg_transaction_time = 0
                error_count = 0

    return {
        "location": location,
        "timestamp": datetime.datetime.combine(date, datetime.time(hour, 0, 0)),
        "transactions_processed": transactions,
        "average_transaction_time": avg_transaction_time,
        "error_count": error_count,
        "anomaly_types": anomaly_types
    }

# Fix for Issue 2 (Option B): Use generate_hourly_pos_data instead of missing generate_daily_pos_data
def generate_daily_pos_data(date, location, anomaly_config=None):
    # Aggregate hourly data for the day
    daily_summary = {
        "location": location,
        "date": date,
        "transactions_processed": 0,
        "average_transaction_time": 0,
        "error_count": 0,
        "anomaly_types": []
    }
    total_transaction_time = 0
    for hour in range(24):
        hourly = generate_hourly_pos_data(date, hour, location, anomaly_config)
        daily_summary["transactions_processed"] += hourly["transactions_processed"]
        total_transaction_time += hourly["average_transaction_time"]
        daily_summary["error_count"] += hourly["error_count"]
        daily_summary["anomaly_types"].extend(hourly["anomaly_types"])
    daily_summary["average_transaction_time"] = total_transaction_time // 24
    daily_summary["anomaly_types"] = list(set(daily_summary["anomaly_types"]))
    return daily_summary

def generate_pos_data_for_year(anomalies=None):
    year = YEAR_TO_GENERATE
    locations = LOCATIONS
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
            if anomaly['location'] not in anomaly_config[date_obj]:
                anomaly_config[date_obj][anomaly['location']] = {"types": [], "hour": anomaly.get("hour")}
            anomaly_config[date_obj][anomaly['location']]["types"].append(anomaly['type'])
            if "hour" in anomaly:
                anomaly_config[date_obj][anomaly['location']]["hour"] = anomaly["hour"]

    for location in locations:
        all_daily_data[location] = []
        current_date = start_date
        while current_date <= end_date:
            daily_data = generate_daily_pos_data(current_date, location, anomaly_config)
            all_daily_data[location].append(daily_data)
            current_date += delta
    return all_daily_data


def store_incidents_and_problems(db, resource_ids, anomalies, year):
    incident_collection = db["incidents"]
    problem_collection = db["problems"]
    anomaly_config = {}
    if anomalies:
        for anomaly in anomalies:
            date_obj = datetime.date.fromisoformat(anomaly['date'])
            if date_obj not in anomaly_config:
                anomaly_config[date_obj] = {}
            if anomaly['location'] not in anomaly_config[date_obj]:
                anomaly_config[date_obj][anomaly['location']] = {"types": [], "hour": anomaly.get("hour")}
            anomaly_config[date_obj][anomaly['location']]["types"].append(anomaly['type'])
            if "hour" in anomaly:
                anomaly_config[date_obj][anomaly['location']]["hour"] = anomaly["hour"]

    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)
    delta = datetime.timedelta(days=1)
    current_date = start_date

    while current_date <= end_date:
        for location, res_id in resource_ids.items():
            if current_date in anomaly_config and location in anomaly_config[current_date]:
                anomaly_types = anomaly_config[current_date][location]["types"]
                anomaly_hour = anomaly_config[current_date][location].get("hour")
                if anomaly_hour is None:
                    anomaly_hour = 12  # Default to noon if hour is missing
                for anomaly_type in anomaly_types:
                    if anomaly_type in ["System Malfunction", "Significant Technical Problem", "Unauthorized Shutdown"]:
                        incident_data = generate_incident_data(current_date, anomaly_hour, location, anomaly_type, res_id)
                        incident_collection.insert_one(incident_data)
                        print(f"Incident created for {location} on {current_date} due to {anomaly_type}.")
                    if anomaly_type in ["Significant Technical Problem"]:
                        problem_data = generate_problem_data(current_date, anomaly_hour, location, anomaly_type)
                        problem_collection.insert_one(problem_data)
                        print(f"Problem created for {location} on {current_date} due to {anomaly_type}.")
        current_date += delta
    print(f"Incident data stored in 'incidents' collection.")
    print(f"Problem data stored in 'problems' collection.")



def store_data_mongodb_hourly():
    anomalies=POS_ANOMALIES
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    year = YEAR_TO_GENERATE

    # Application Collection
    applications_collection = db["applications"]
    app_data = generate_application_data(year)
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

    # Cost Data Collection (hourly) - BULK INSERT
    cost_data_collection = db["cost_data"]
    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)
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

    # --- NEW: Incidents and Problems ---
    store_incidents_and_problems(db, resource_ids, anomalies, year)

    # Resource Utilization Collection - BULK INSERT
    resource_utilization_collection = db["resource_utilization"]
    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)
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
    daily_pos_data = generate_pos_data_for_year()
    store_data_mongodb_hourly()
    
    print("\nCMDB-like data generation and storage complete.")

