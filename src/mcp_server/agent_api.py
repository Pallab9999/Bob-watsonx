"""
Agent API endpoints for watsonx Orchestrate integration
"""

import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel

from .watsonx_agent import (
    WatsonxAgent,
    AgentFactory,
    AgentExecution,
    execute_tool
)


# Request/Response models
class AgentExecutionRequest(BaseModel):
    """Request model for agent execution"""
    agent_type: str
    user_input: str
    context: Optional[Dict[str, Any]] = None


class AgentExecutionResponse(BaseModel):
    """Response model for agent execution"""
    execution_id: str
    agent_name: str
    state: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentInfoResponse(BaseModel):
    """Response model for agent information"""
    name: str
    description: str
    tools: list
    created_at: str
    execution_count: int


class ExecutionHistoryResponse(BaseModel):
    """Response model for execution history"""
    execution_id: str
    agent_name: str
    user_input: str
    state: str
    tool_calls: list
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: str
    end_time: Optional[str] = None


class AgentAPIManager:
    """Manager for agent API operations"""
    
    def __init__(self):
        """Initialize the agent API manager"""
        self.agents: Dict[str, WatsonxAgent] = {}
        self.executions: Dict[str, AgentExecution] = {}
    
    def create_agent(
        self,
        agent_type: str,
        tool_executor=None
    ) -> Optional[WatsonxAgent]:
        """
        Create an agent
        
        Args:
            agent_type: Type of agent to create
            tool_executor: Function to execute tools
            
        Returns:
            Agent instance or None
        """
        agent = AgentFactory.create_agent(agent_type, tool_executor)
        if agent:
            self.agents[agent_type] = agent
        return agent
    
    def get_agent(self, agent_type: str) -> Optional[WatsonxAgent]:
        """Get an agent by type"""
        return self.agents.get(agent_type)
    
    def get_available_agents(self) -> list:
        """Get list of available agent types"""
        return AgentFactory.get_available_agents()
    
    async def execute_agent(
        self,
        agent_type: str,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute an agent
        
        Args:
            agent_type: Type of agent to execute
            user_input: User input
            context: Optional execution context
            
        Returns:
            Execution result
        """
        # Get or create agent
        agent = self.get_agent(agent_type)
        if not agent:
            agent = self.create_agent(agent_type, execute_tool)
        
        if not agent:
            return {
                "success": False,
                "error": f"Unknown agent type: {agent_type}"
            }
        
        # Generate execution ID
        execution_id = str(uuid.uuid4())
        
        # Execute agent
        execution = await agent.execute(execution_id, user_input, context)
        
        # Store execution
        self.executions[execution_id] = execution
        
        return {
            "success": True,
            "execution_id": execution_id,
            "agent_name": agent.name,
            "state": execution.state.value,
            "result": execution.result,
            "error": execution.error
        }
    
    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get an execution by ID"""
        execution = self.executions.get(execution_id)
        if execution:
            return execution.to_dict()
        return None
    
    def get_execution_history(
        self,
        agent_type: Optional[str] = None,
        limit: int = 10
    ) -> list:
        """Get execution history"""
        executions = list(self.executions.values())
        
        if agent_type:
            executions = [e for e in executions if e.agent_name == agent_type]
        
        # Sort by start time (newest first)
        executions.sort(key=lambda e: e.start_time, reverse=True)
        
        return [e.to_dict() for e in executions[:limit]]
    
    def get_agent_info(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """Get agent information"""
        agent = self.get_agent(agent_type)
        if agent:
            return agent.get_agent_info()
        return None


# Global agent manager instance
agent_manager = AgentAPIManager()


# API endpoint functions
async def list_agents() -> Dict[str, Any]:
    """List available agents"""
    agents = agent_manager.get_available_agents()
    return {
        "agents": agents,
        "count": len(agents)
    }


async def get_agent_info(agent_type: str) -> Dict[str, Any]:
    """Get information about an agent"""
    info = agent_manager.get_agent_info(agent_type)
    if info:
        return {
            "success": True,
            "agent": info
        }
    return {
        "success": False,
        "error": f"Agent type '{agent_type}' not found"
    }


async def execute_agent(request: AgentExecutionRequest) -> Dict[str, Any]:
    """Execute an agent"""
    result = await agent_manager.execute_agent(
        request.agent_type,
        request.user_input,
        request.context
    )
    return result


async def get_execution(execution_id: str) -> Dict[str, Any]:
    """Get an execution by ID"""
    execution = agent_manager.get_execution(execution_id)
    if execution:
        return {
            "success": True,
            "execution": execution
        }
    return {
        "success": False,
        "error": f"Execution '{execution_id}' not found"
    }


async def get_execution_history(
    agent_type: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """Get execution history"""
    history = agent_manager.get_execution_history(agent_type, limit)
    return {
        "success": True,
        "count": len(history),
        "executions": history
    }


# Initialize default agents
def initialize_agents():
    """Initialize default agents"""
    for agent_type in agent_manager.get_available_agents():
        agent_manager.create_agent(agent_type, execute_tool)

# Made with Bob
