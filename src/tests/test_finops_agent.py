
"""
Basic tests for FinOps Agent
"""
import pytest
from finops_agent import FinOpsContext, finops_agent

def test_context_creation():
    """Test FinOps context creation"""
    context = FinOpsContext()
    assert context.database_name == "finops_demo"

@pytest.mark.asyncio
async def test_agent_basic_query():
    """Test basic agent functionality"""  
    context = FinOpsContext()
    # Add more specific tests based on your requirements
    pass
