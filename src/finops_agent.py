"""
FinOps AI Agent with MongoDB Integration
Specialized agent for Financial Operations analysis and optimization
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pymongo import MongoClient
from pymongo.collection import Collection
import os
from enum import Enum
import demo_constants


# Pydantic Models for structured data
class Environment(str, Enum):
    PROD = "prod"
    TEST = "test"
    DEV = "dev"


class Criticality(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Provider(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class Application(BaseModel):
    app_id: str
    name: str
    description: str
    criticality: Criticality
    business_unit: str
    business_service: str
    owner: str
    creation_date: datetime
    last_modified: datetime


class CloudResource(BaseModel):
    resource_id: str
    app_id: str
    resource_type: str
    provider: Provider
    region: str
    environment: Environment
    specifications: Dict[str, Any]
    creation_date: datetime
    last_modified: datetime


class WasteAnalysis(BaseModel):
    resource_id: str
    app_id: str
    app_name: str
    business_unit: str
    resource_type: str
    environment: str
    waste_percentage: float
    average_utilization: float
    monthly_cost: float
    estimated_waste_cost: float


class CostTrend(BaseModel):
    app_id: str
    period_start: datetime
    period_end: datetime
    total_cost: float
    cost_change_percentage: Optional[float] = None


class Problem(BaseModel):
    problem_id: str
    app_id: str
    priority: int
    impact: str
    open_date: datetime
    resolution_date: Optional[datetime]
    related_incidents: List[str]
    estimated_cost_impact: float
    description: str


# Database Context for the agent
class FinOpsContext(BaseModel):
    connection_string : Optional[str] = None
    database_name: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    agent_name: str = Field(default="FinOps Assistant")
    debug_mode: bool = Field(default=False)
         
    def __init__(self):
        super().__init__()
        self._load_config()

    def _load_config(self):
        """Load configuration from environment variables"""
        self.connection_string = demo_constants.MONGO_URI
        self.database_name = demo_constants.DATABASE_NAME
        self.openai_api_key = demo_constants.OPENAI_API_KEY
        self.openai_model = demo_constants.OPENAI_LLM_MODEL
        self.agent_name = demo_constants.AGENT_NAME
        self.debug_mode = demo_constants.AGENT_DEBUG
        
    def get_client(self) -> MongoClient:
        return MongoClient(self.connection_string)
    
    def get_collection(self, collection_name: str) -> Collection:
        client = self.get_client()
        db = client[self.database_name]
        return db[collection_name]


# Tool Functions
def get_applications(ctx: RunContext[FinOpsContext], business_unit: Optional[str] = None) -> List[Application]:
    """
    Retrieve applications, optionally filtered by business unit.
    
    Args:
        business_unit: Optional filter by business unit
    
    Returns:
        List of applications
    """
    collection = ctx.deps.get_collection("applications")
    
    filter_query = {}
    if business_unit:
        filter_query["business_unit"] = {"$regex": business_unit, "$options": "i"}
    
    apps = list(collection.find(filter_query))
    return [Application(**app) for app in apps]


def get_cloud_resources(
    ctx: RunContext[FinOpsContext], 
    app_id: Optional[str] = None,
    environment: Optional[Environment] = None,
    provider: Optional[Provider] = None
) -> List[CloudResource]:
    """
    Retrieve cloud resources with optional filters.
    
    Args:
        app_id: Filter by application ID
        environment: Filter by environment (prod, test, dev)
        provider: Filter by cloud provider (aws, azure, gcp)
    
    Returns:
        List of cloud resources
    """
    collection = ctx.deps.get_collection("cloud_resources")
    
    filter_query = {}
    if app_id:
        filter_query["app_id"] = app_id
    if environment:
        filter_query["environment"] = environment.value
    if provider:
        filter_query["provider"] = provider.value
    
    resources = list(collection.find(filter_query))
    return [CloudResource(**resource) for resource in resources]


def analyze_waste(
    ctx: RunContext[FinOpsContext],
    app_id: Optional[str] = None,
    business_unit: Optional[str] = None,
    min_waste_percentage: float = 0.0
) -> List[WasteAnalysis]:
    """
    Analyze cloud waste and identify optimization opportunities.
    
    Args:
        app_id: Filter by application ID
        business_unit: Filter by business unit
        min_waste_percentage: Minimum waste percentage threshold
    
    Returns:
        List of waste analysis results
    """
    collection = ctx.deps.get_collection("cloud_waste")
    
    filter_query = {}
    if app_id:
        filter_query["app_id"] = app_id
    if business_unit:
        filter_query["business_unit"] = {"$regex": business_unit, "$options": "i"}
    if min_waste_percentage > 0:
        filter_query["waste_percentage"] = {"$gte": min_waste_percentage}
    
    # Sort by waste percentage descending to prioritize biggest opportunities
    waste_data = list(collection.find(filter_query).sort("waste_percentage", -1))
    
    return [WasteAnalysis(
        resource_id=item["_id"],
        app_id=item["app_id"],
        app_name=item["app_name"],
        business_unit=item["business_unit"],
        resource_type=item["resource_type"],
        environment=item["environment"],
        waste_percentage=item["waste_percentage"],
        average_utilization=item["average_utilization"],
        monthly_cost=item["monthly_cost"],
        estimated_waste_cost=item["estimated_waste_cost"]
    ) for item in waste_data]


def get_cost_trends(
    ctx: RunContext[FinOpsContext],
    app_id: Optional[str] = None,
    days_back: int = 30
) -> List[Dict[str, Any]]:
    """
    Get cost trends for applications over a specified period.
    
    Args:
        app_id: Filter by application ID
        days_back: Number of days to look back
    
    Returns:
        Cost trend data
    """
    collection = ctx.deps.get_collection("costs_trend_per_app")
    
    filter_query = {}
    if app_id:
        filter_query["app_id"] = app_id
    
    # Get cost trends sorted by date
    trends = list(collection.find(filter_query).sort("period_start", -1).limit(days_back))
    return trends


def get_problems_and_incidents(
    ctx: RunContext[FinOpsContext],
    app_id: Optional[str] = None,
    include_resolved: bool = False
) -> List[Problem]:
    """
    Get problems and incidents affecting applications.
    
    Args:
        app_id: Filter by application ID
        include_resolved: Whether to include resolved problems
    
    Returns:
        List of problems
    """
    collection = ctx.deps.get_collection("problems")
    
    filter_query = {}
    if app_id:
        filter_query["app_id"] = app_id
    if not include_resolved:
        filter_query["resolution_date"] = {"$exists": False}
    
    problems = list(collection.find(filter_query).sort("priority", 1))
    return [Problem(**problem) for problem in problems]


def calculate_potential_savings(
    ctx: RunContext[FinOpsContext],
    business_unit: Optional[str] = None
) -> Dict[str, float]:
    """
    Calculate potential cost savings from waste reduction.
    
    Args:
        business_unit: Filter by business unit
    
    Returns:
        Savings summary
    """
    waste_analysis = analyze_waste(ctx, business_unit=business_unit, min_waste_percentage=10.0)
    
    total_monthly_cost = sum(w.monthly_cost for w in waste_analysis)
    total_waste_cost = sum(w.estimated_waste_cost for w in waste_analysis)
    
    return {
        "total_monthly_cost": total_monthly_cost,
        "total_waste_cost": total_waste_cost,
        "potential_annual_savings": total_waste_cost * 12,
        "waste_percentage": (total_waste_cost / total_monthly_cost * 100) if total_monthly_cost > 0 else 0,
        "resources_analyzed": len(waste_analysis)
    }


def get_top_cost_drivers(
    ctx: RunContext[FinOpsContext],
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get top cost-driving applications and resources.
    
    Args:
        limit: Number of top items to return
    
    Returns:
        Top cost drivers
    """
    collection = ctx.deps.get_collection("costs_per_application")
    
    # Get applications sorted by total cost
    cost_drivers = list(collection.find().sort("total_cost", -1).limit(limit))
    return cost_drivers


# Create the FinOps AI Agent
finops_agent = Agent(
    'openai:gpt-4o',  # Agent model identifier
    deps_type=FinOpsContext,
    system_prompt="""
    You are a FinOps (Financial Operations) AI assistant specialized in cloud cost optimization 
    and financial analysis. You have access to a comprehensive database of cloud resources, 
    applications, cost data, waste analysis, and operational problems.

    Your primary responsibilities:
    1. **Cost Analysis**: Analyze cloud spending patterns and identify cost optimization opportunities
    2. **Waste Detection**: Identify underutilized resources and calculate potential savings
    3. **Trend Analysis**: Track cost trends and predict future spending
    4. **Problem Correlation**: Correlate operational issues with cost impacts
    5. **Recommendations**: Provide actionable recommendations for cost optimization

    Key capabilities:
    - Query application portfolios and their associated costs
    - Analyze cloud resource utilization and waste
    - Calculate potential savings from optimization efforts
    - Track cost trends across different time periods
    - Correlate problems/incidents with financial impact
    - Generate executive summaries and detailed reports

    Always provide:
    - Clear, actionable insights
    - Quantified financial impact where possible
    - Prioritized recommendations based on business value
    - Context-aware analysis considering business criticality

    Be concise but comprehensive in your analysis.
    """,
    tools=[
        get_applications,
        get_cloud_resources, 
        analyze_waste,
        get_cost_trends,
        get_problems_and_incidents,
        calculate_potential_savings,
        get_top_cost_drivers
    ]
)


# Example usage and testing
async def demo_finops_agent():
    """
    Demonstrate the FinOps agent capabilities
    """
    # Initialize context (update connection string as needed)
    context = FinOpsContext()
    # Example queries
    queries = [
        "What are the top 5 applications by cost and their waste percentage?",
        "Show me all high-waste resources (>50%) in the production environment",
        "Calculate potential annual savings for the Online Sales business unit",
        "What problems are currently open that have significant cost impact?",
        "Analyze cost trends for the RetailPOS application over the last 30 days",
        "Generate an executive summary of our current FinOps status"
    ]
    
    print("FinOps AI Agent Demo")
    print("=" * 50)
    
    for query in queries:
        print(f"\n🔍 Query: {query}")
        try:
            result = await finops_agent.run(query, deps=context)
            print(f"💡 Response: {result.data}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        print("-" * 30)


# CLI Interface for the agent
class FinOpsAgentCLI:
    def __init__(self):
        self.context = FinOpsContext()
    
    async def run_interactive(self):
        """
        Run an interactive CLI session with the FinOps agent
        """
        print("🏦 FinOps AI Agent - Interactive Mode")
        print("Type 'help' for available commands, 'quit' to exit")
        print("=" * 60)
        
        while True:
            try:
                query = input("\n💬 FinOps> ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif query.lower() == 'help':
                    self.show_help()
                elif query:
                    result = await finops_agent.run(query, deps=self.context)
                    print(f"\n📊 {result.data}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def show_help(self):
        print("""
🔧 Available Commands:
- Show applications in [business_unit]
- Analyze waste for [app_id/business_unit]  
- Calculate savings for [business_unit]
- Show cost trends for [app_id]
- List open problems with cost impact
- Show top cost drivers
- Generate executive summary
- help - Show this help
- quit - Exit the application
        """)


if __name__ == "__main__":
    import asyncio
    
    # You can either run the demo or the interactive CLI
    # asyncio.run(demo_finops_agent())
    
    # Or run interactive mode
    cli = FinOpsAgentCLI()
    asyncio.run(cli.run_interactive())
