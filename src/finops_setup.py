import os
from pathlib import Path
from typing import Dict, Optional, Any
import json
import demo_constants


class FinOpsConfig:
    """Configuration management for FinOps Agent"""
    
    def __init__(self):
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables"""
        self.mongodb_connection = demo_constants.MONGO_URI
        self.database_name = demo_constants.FINOPS_DATABASE_NAME
        self.openai_api_key = demo_constants.OPENAI_API_KEY
        self.openai_model = demo_constants.OPENAI_MODEL
        self.agent_name = demo_constants.AGENT_NAME
        self.debug_mode = demo_constants.AGENT_DEBUG
        self.max_tools_per_call = demo_constants.MAX_TOOLS_PER_CALL
        self.log_level = demo_constants.LOG_LEVEL
        self.log_file = demo_constants.LOG_FILE
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        issues = []
        
        if not self.openai_api_key:
            issues.append("OpenAI API key not configured")
        
        if not self.mongodb_connection:
            issues.append("MongoDB connection string not configured")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": {
                "mongodb_connection": self.mongodb_connection,
                "database_name": self.database_name,
                "openai_model": self.openai_model,
                "agent_name": self.agent_name,
                "debug_mode": self.debug_mode
            }
        }
    

def setup_project():
    """Setup the FinOps agent project structure"""
    
    # Create project directories
    directories = [
        "config",
        "logs", 
        "data",
        "reports",
        "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    
    # Create .env template
    config = FinOpsConfig()
    
    # Create basic test file
    test_content = '''
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
'''
    
    with open("tests/test_finops_agent.py", "w") as f:
        f.write(test_content)
    print("✅ Created basic test file")
    
    print("\n🎉 Project setup complete!")
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Update .env file with your MongoDB and OpenAI credentials")
    print("3. Run the agent: python finops_agent.py")


# Enhanced FinOps Agent with configuration
from finops_agent import finops_agent, FinOpsContext
import logging


class ConfiguredFinOpsAgent:
    """FinOps Agent with configuration management"""
    
    def __init__(self, config_file: str = ".env"):
        self.config = FinOpsConfig(config_file)
        self.setup_logging()
        
        # Validate configuration
        validation = self.config.validate_config()
        if not validation["valid"]:
            raise ValueError(f"Configuration errors: {', '.join(validation['issues'])}")
        
        # Initialize context
        self.context = FinOpsContext(
            connection_string=self.config.mongodb_connection,
            database_name=self.config.database_name
        )
        
        # Set up OpenAI (if using OpenAI models)
        if self.config.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.config.openai_api_key
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("FinOpsAgent")
    
    async def query(self, question: str) -> str:
        """Query the FinOps agent with logging"""
        self.logger.info(f"Processing query: {question}")
        
        try:
            result = await finops_agent.run(question, deps=self.context)
            self.logger.info("Query processed successfully")
            return result.data
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            raise
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent and configuration information"""
        return {
            "agent_name": self.config.agent_name,
            "model": self.config.openai_model,
            "database": self.config.database_name,
            "debug_mode": self.config.debug_mode,
            "tools_available": len(finops_agent.tools),
            "status": "ready"
        }


# Web API using FastAPI (optional)
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    
    class QueryRequest(BaseModel):
        question: str
        context: Optional[Dict[str, Any]] = None
    
    class QueryResponse(BaseModel):
        answer: str
        processing_time: float
        agent_info: Dict[str, Any]
    
    def create_finops_api(config_file: str = ".env") -> FastAPI:
        """Create FastAPI application for FinOps agent"""
        app = FastAPI(title="FinOps AI Agent API", version="1.0.0")
        agent = ConfiguredFinOpsAgent(config_file)
        
        @app.get("/")
        async def root():
            return {"message": "FinOps AI Agent API", "status": "active"}
        
        @app.get("/agent/info")
        async def get_agent_info():
            return agent.get_agent_info()
        
        @app.post("/query", response_model=QueryResponse)
        async def query_agent(request: QueryRequest):
            import time
            start_time = time.time()
            
            try:
                answer = await agent.query(request.question)
                processing_time = time.time() - start_time
                
                return QueryResponse(
                    answer=answer,
                    processing_time=processing_time,
                    agent_info=agent.get_agent_info()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        return app

except ImportError:
    print("FastAPI not available. Install with: pip install fastapi uvicorn")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_project()
    else:
        # Run configured agent
        agent = ConfiguredFinOpsAgent()
        print("FinOps Agent configured and ready!")
        print(f"Agent info: {agent.get_agent_info()}")
