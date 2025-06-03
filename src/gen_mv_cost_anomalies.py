from datetime import datetime, tzinfo, timezone
from pymongo import MongoClient

from demo_constants import MONGO_URI, DATABASE_NAME

# This script creates a MongoDB view to identify cost anomalies in cloud resources.

def create_cost_anomaly_view(viewname='mv_cost_anomalies'):
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db['cost_data']
    
    collection.aggregate([
        {
            '$match': {
                'timestamp': {
                    '$gte': datetime(2024, 9, 1, 0, 0, 0, tzinfo=timezone.utc)
                }
            }
        }, {
            '$lookup': {
                'from': 'cloud_resources', 
                'localField': 'resource_id', 
                'foreignField': 'resource_id', 
                'as': 'resource'
            }
        }, {
            '$unwind': '$resource'
        }, {
            '$addFields': {
                'month': {
                    '$dateToString': {
                        'format': '%Y-%m', 
                        'date': '$timestamp'
                    }
                }, 
                'is_current_month': {
                    '$gte': [
                        '$timestamp', datetime(2024, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
                    ]
                }
            }
        }, {
            '$group': {
                '_id': {
                    'app_id': '$resource.app_id', 
                    'resource_id': '$resource_id', 
                    'is_current_month': '$is_current_month'
                }, 
                'cost': {
                    '$sum': '$cost'
                }, 
                'days_count': {
                    '$addToSet': {
                        '$dayOfMonth': '$timestamp'
                    }
                }
            }
        }, {
            '$addFields': {
                'days': {
                    '$size': '$days_count'
                }
            }
        }, {
            '$addFields': {
                'daily_avg_cost': {
                    '$divide': [
                        '$cost', '$days'
                    ]
                }
            }
        }, {
            '$group': {
                '_id': {
                    'app_id': '$_id.app_id', 
                    'resource_id': '$_id.resource_id'
                }, 
                'current_month_daily_avg': {
                    '$max': {
                        '$cond': [
                            '$_id.is_current_month', '$daily_avg_cost', 0
                        ]
                    }
                }, 
                'previous_month_daily_avg': {
                    '$max': {
                        '$cond': [
                            {
                                '$not': '$_id.is_current_month'
                            }, '$daily_avg_cost', 0
                        ]
                    }
                }, 
                'current_month_total': {
                    '$max': {
                        '$cond': [
                            '$_id.is_current_month', '$cost', 0
                        ]
                    }
                }, 
                'previous_month_total': {
                    '$max': {
                        '$cond': [
                            {
                                '$not': '$_id.is_current_month'
                            }, '$cost', 0
                        ]
                    }
                }
            }
        }, {
            '$addFields': {
                'percentage_increase': {
                    '$cond': [
                        {
                            '$eq': [
                                '$previous_month_daily_avg', 0
                            ]
                        }, None, {
                            '$multiply': [
                                {
                                    '$divide': [
                                        {
                                            '$subtract': [
                                                '$current_month_daily_avg', '$previous_month_daily_avg'
                                            ]
                                        }, '$previous_month_daily_avg'
                                    ]
                                }, 100
                            ]
                        }
                    ]
                }
            }
        }, {
            '$match': {
                'percentage_increase': {
                    '$gte': 20
                }
            }
        }, {
            '$lookup': {
                'from': 'applications', 
                'localField': '_id.app_id', 
                'foreignField': 'app_id', 
                'as': 'app_details'
            }
        }, {
            '$unwind': '$app_details'
        }, {
            '$lookup': {
                'from': 'cloud_resources', 
                'localField': '_id.resource_id', 
                'foreignField': 'resource_id', 
                'as': 'resource_details'
            }
        }, {
            '$unwind': '$resource_details'
        }, {
            '$project': {
                'app_id': '$_id.app_id', 
                'app_name': '$app_details.name', 
                '_id': '$_id.resource_id', 
                'resource_type': '$resource_details.resource_type', 
                'environment': '$resource_details.environment', 
                'previous_month_daily_avg': 1, 
                'current_month_daily_avg': 1, 
                'percentage_increase': 1, 
                'previous_month_total': 1, 
                'current_month_total': 1
            }
        }, {
            '$sort': {
                'percentage_increase': -1
            }
        }, {
            '$merge':{
                'into': viewname, 
                'on': '_id',
                'whenMatched': 'replace', 
                'whenNotMatched': 'insert'
            }
        }
    ])
    
if __name__ == "__main__":
    viewname = 'mv_cost_anomalies'
    create_cost_anomaly_view(viewname)
    print(f"View '{viewname}' created successfully.")
    
        
