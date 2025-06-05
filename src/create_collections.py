#!/usr/bin/env python3
"""
MongoDB Collections Creation Script

This script creates MongoDB collections with proper validation schemas and configurations:
- applications
- cloud_resources
- cost_data (time series)
- incidents
- problems
- resource_utilization (time series)
"""

from pymongo import MongoClient
from pymongo.operations import SearchIndexModel

from demo_constants import (YEAR_TO_GENERATE, MONGO_URI, DATABASE_NAME, LOCATIONS)

def create_collections():
        
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]

    # Drop existing collections if they exist
    collections = [
        "applications", 
        "cloud_resources", 
        "incidents", 
        "problems", 
        "cost_data", 
        "resource_utilization"
    ]

    for collection_name in collections:
        if collection_name in db.list_collection_names():
            db[collection_name].drop()
            print(f"Dropped existing collection: {collection_name}")

    # Create applications collection
    db.create_collection(
        "applications",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["app_id", "name", "criticality", "business_unit"],
                "properties": {
                    "app_id": {"bsonType": "string"},
                    "name": {"bsonType": "string"},
                    "description": {"bsonType": "string"},
                    "criticality": {
                        "bsonType": "string",
                        "enum": ["high", "medium", "low"]
                    },
                    "business_unit": {"bsonType": "string"},
                    "business_service": {"bsonType": "string"},
                    "owner": {"bsonType": "string"},
                    "creation_date": {"bsonType": "date"},
                    "last_modified": {"bsonType": "date"}
                }
            }
        }
    )
    print("Created applications collection")

    # Create cloud_resources collection
    db.create_collection(
        "cloud_resources",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["resource_id", "app_id", "resource_type", "provider", "environment"],
                "properties": {
                    "resource_id": {"bsonType": "string"},
                    "app_id": {"bsonType": "string"},
                    "resource_type": {"bsonType": "string"},
                    "provider": {
                        "bsonType": "string",
                        "enum": ["aws", "azure", "gcp", "other"]
                    },
                    "region": {"bsonType": "string"},
                    "environment": {
                        "bsonType": "string",
                        "enum": ["dev", "test", "prod"]
                    },
                    "specifications": {"bsonType": "object"},
                    "creation_date": {"bsonType": "date"},
                    "last_modified": {"bsonType": "date"}
                }
            }
        }
    )
    print("Created cloud_resources collection")

    # Create cost_data collection (time series)
    db.create_collection(
        "cost_data",
        timeseries={
            "timeField": "timestamp",
            "metaField": "resource_id",
            "granularity": "hours"
        }
    )
    print("Created cost_data collection (time series)")

    # Create incidents collection
    db.create_collection(
        "incidents",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["incident_id", "app_id", "priority", "start_time"],
                "properties": {
                    "incident_id": {"bsonType": "string"},
                    "description": {"bsonType": "string"},
                    "app_id": {"bsonType": "string"},
                    "priority": {"bsonType": "int"},
                    "impact": {
                        "bsonType": "string",
                        "enum": ["high", "medium", "low"]
                    },
                    "start_time": {"bsonType": "date"},
                    "resolution_time": {"bsonType": "date"},
                    "duration_minutes": {"bsonType": "int"},
                    "affected_resources": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    },
                    "estimated_cost_impact": {"bsonType": "double"}
                }
            }
        }
    )
    print("Created incidents collection")

    # Create problems collection
    db.create_collection(
        "problems",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["problem_id", "app_id", "priority", "open_date"],
                "properties": {
                    "problem_id": {"bsonType": "string"},
                    "description": {"bsonType": "string"},
                    "app_id": {"bsonType": "string"},
                    "priority": {"bsonType": "int"},
                    "impact": {
                        "bsonType": "string",
                        "enum": ["high", "medium", "low"]
                    },
                    "open_date": {"bsonType": "date"},
                    "resolution_date": {"bsonType": "date"},
                    "related_incidents": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    },
                    "estimated_cost_impact": {"bsonType": "double"}
                }
            }
        }
    )
    print("Created problems collection")

    # Create resource_utilization collection (time series)
    db.create_collection(
        "resource_utilization",
        timeseries={
            "timeField": "timestamp",
            "metaField": "resource_id",
            "granularity": "hours"
        }
    )
    print("Created resource_utilization collection (time series)")

    # Print final list of collections
    print("\nCreated collections:")
    for collection_name in db.list_collection_names():
        print(f"- {collection_name}")

    print("\nCollection creation completed successfully!")
    

def create_indexes():
    """
    Create indexes for the collections to improve query performance.
    """
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]

    # Create indexes for applications collection
    db.applications.create_index("app_id")
    db.applications.create_index("business_unit")
    print("Created indexes for applications collection")

    # Create indexes for incidents collection
    db.incidents.create_index("incident_id")
    db.incidents.create_index("app_id")
    print("Created indexes for incidents collection")

    # Create indexes for problems collection
    db.problems.create_index("problem_id")
    db.problems.create_index("app_id")
    print("Created indexes for problems collection")
    
    # Create your search index model, then create the search index
    search_index_model = SearchIndexModel(
    definition={
        "mappings": {
                "dynamic": False,
                "fields": {
                "description": {
                    "type": "string"
                }
                }
        }
    },
    name="search_index"
    )
    db.incidents.create_search_index(model=search_index_model)
        

if __name__ == "__main__":
    #create_collections()
    create_indexes()