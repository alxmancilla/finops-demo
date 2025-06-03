from datetime import datetime, tzinfo, timezone
from pymongo import MongoClient

from demo_constants import MONGO_URI, DATABASE_NAME

# This script creates a MongoDB view to identify cost anomalies in cloud resources.

def create_cloud_waste_view(viewname='mv_cloud_waste'):
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db['resource_utilization']
    
    collection.aggregate([
        {
            '$match': {
                'timestamp': {
                    '$gte': datetime(2024, 12, 1, 0, 0, 0, tzinfo=timezone.utc), 
                    '$lte': datetime(2024, 12, 31, 0, 0, 0, tzinfo=timezone.utc)
                }
            }
        }, {
            '$group': {
                '_id': '$resource_id', 
                'avg_cpu_utilization': {
                    '$avg': '$cpu_utilization'
                }, 
                'avg_memory_utilization': {
                    '$avg': '$memory_utilization'
                }, 
                'app_id': {
                    '$first': '$resource_id'
                }
            }
        }, {
            '$addFields': {
                'average_utilization': {
                    '$avg': [
                        '$avg_cpu_utilization', '$avg_memory_utilization', '$avg_storage_utilization'
                    ]
                }, 
                'waste_percentage': {
                    '$multiply': [
                        {
                            '$subtract': [
                                1, {
                                    '$avg': [
                                        '$avg_cpu_utilization', '$avg_memory_utilization', '$avg_storage_utilization'
                                    ]
                                }
                            ]
                        }, 100
                    ]
                }
            }
        }, {
            '$lookup': {
                'from': 'cloud_resources', 
                'localField': '_id', 
                'foreignField': 'resource_id', 
                'as': 'resource_details'
            }
        }, {
            '$unwind': '$resource_details'
        }, {
            '$lookup': {
                'from': 'applications', 
                'localField': 'resource_details.app_id', 
                'foreignField': 'app_id', 
                'as': 'app_details'
            }
        }, {
            '$unwind': '$app_details'
        }, {
            '$lookup': {
                'from': 'cost_data', 
                'let': {
                    'resource_id': '$_id', 
                    'start_date': datetime(2024, 12, 1, 0, 0, 0, tzinfo=timezone.utc), 
                    'end_date': datetime(2024, 12, 31, 0, 0, 0, tzinfo=timezone.utc)
                }, 
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$and': [
                                    {
                                        '$eq': [
                                            '$resource_id', '$$resource_id'
                                        ]
                                    }, {
                                        '$gte': [
                                            '$timestamp', '$$start_date'
                                        ]
                                    }, {
                                        '$lte': [
                                            '$timestamp', '$$end_date'
                                        ]
                                    }
                                ]
                            }
                        }
                    }, {
                        '$group': {
                            '_id': None, 
                            'total_cost': {
                                '$sum': '$cost'
                            }
                        }
                    }
                ], 
                'as': 'cost_data'
            }
        }, {
            '$unwind': {
                'path': '$cost_data', 
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$project': {
                'app_id': '$app_details.app_id', 
                'app_name': '$app_details.name', 
                'business_unit': '$app_details.business_unit', 
                'resource_type': '$resource_details.resource_type', 
                'environment': '$resource_details.environment', 
                'average_utilization': {
                    '$multiply': [
                        '$average_utilization', 100
                    ]
                }, 
                'waste_percentage': 1, 
                'monthly_cost': {
                    '$ifNull': [
                        '$cost_data.total_cost', 0
                    ]
                }, 
                'estimated_waste_cost': {
                    '$multiply': [
                        {
                            '$ifNull': [
                                '$cost_data.total_cost', 0
                            ]
                        }, {
                            '$divide': [
                                '$waste_percentage', 100
                            ]
                        }
                    ]
                }
            }
        }, {
            '$sort': {
                'waste_percentage': -1
            }
        }, {
            '$limit': 10
        }, {
            '$merge': {
                'into': viewname, 
                'on': '_id', 
                'whenMatched': 'replace', 
                'whenNotMatched': 'insert'
            }
        }
    ])
    
if __name__ == "__main__":
    viewname = 'mv_cloud_waste'
    create_cloud_waste_view(viewname)
    print(f"View '{viewname}' created successfully.")
    
        
