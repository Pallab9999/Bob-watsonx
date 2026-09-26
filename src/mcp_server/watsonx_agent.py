"""
watsonx Orchestrate Agent Implementation

This module provides an agent that uses MCP tools for watsonx Orchestrate.
"""

import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum


class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class ToolCall:
    """Represents a tool call in an agent execution"""
    
    def __init__(self, tool_name: str, parameters: Dict[str, Any]):
        """
        Initialize a tool call
        
        Args:
            tool_name: Name of the tool to call
            parameters: Tool parameters
        """
        self.tool_name = tool_name
        self.parameters = parameters
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp
        }


class AgentExecution:
    """Represents an agent execution"""
    
    def __init__(self, execution_id: str, agent_name: str, user_input: str):
        """
        Initialize an agent execution
        
        Args:
            execution_id: Unique execution ID
            agent_name: Name of the agent
            user_input: User input/request
        """
        self.execution_id = execution_id
        self.agent_name = agent_name
        self.user_input = user_input
        self.state = AgentState.IDLE
        self.tool_calls: List[ToolCall] = []
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.start_time = datetime.utcnow().isoformat()
        self.end_time: Optional[str] = None
    
    def add_tool_call(self, tool_call: ToolCall) -> None:
        """Add a tool call to the execution"""
        self.tool_calls.append(tool_call)
    
    def set_result(self, result: Dict[str, Any]) -> None:
        """Set the execution result"""
        self.result = result
        self.state = AgentState.COMPLETED
        self.end_time = datetime.utcnow().isoformat()
    
    def set_error(self, error: str) -> None:
        """Set an error"""
        self.error = error
        self.state = AgentState.FAILED
        self.end_time = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "execution_id": self.execution_id,
            "agent_name": self.agent_name,
            "user_input": self.user_input,
            "state": self.state.value,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls],
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time,
            "end_time": self.end_time
        }


class WatsonxAgent:
    """Base class for watsonx Orchestrate agents"""
    
    def __init__(
        self,
        name: str,
        description: str,
        tools: List[Dict[str, Any]],
        tool_executor: Optional[Callable] = None
    ):
        """
        Initialize the agent
        
        Args:
            name: Agent name
            description: Agent description
            tools: List of available tools
            tool_executor: Function to execute tools
        """
        self.name = name
        self.description = description
        self.tools = tools
        self.tool_executor = tool_executor
        self.executions: Dict[str, AgentExecution] = {}
        self.created_at = datetime.utcnow().isoformat()
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": self.name,
            "description": self.description,
            "tools": self.tools,
            "created_at": self.created_at,
            "execution_count": len(self.executions)
        }
    
    async def execute(
        self,
        execution_id: str,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentExecution:
        """
        Execute the agent
        
        Args:
            execution_id: Unique execution ID
            user_input: User input/request
            context: Optional execution context
            
        Returns:
            Agent execution result
        """
        execution = AgentExecution(execution_id, self.name, user_input)
        execution.state = AgentState.RUNNING
        
        try:
            # Parse user input to determine which tools to use
            tool_calls = self._parse_user_input(user_input, context)
            
            # Execute tool calls
            for tool_call in tool_calls:
                execution.add_tool_call(tool_call)
                
                if self.tool_executor:
                    try:
                        result = await self.tool_executor(
                            tool_call.tool_name,
                            **tool_call.parameters
                        )
                        tool_call.result = result
                    except Exception as e:
                        tool_call.error = str(e)
            
            # Generate final result
            result = self._generate_result(execution)
            execution.set_result(result)
            
        except Exception as e:
            execution.set_error(str(e))
        
        self.executions[execution_id] = execution
        return execution
    
    def _parse_user_input(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ToolCall]:
        """
        Parse user input to determine tool calls
        
        Args:
            user_input: User input
            context: Execution context
            
        Returns:
            List of tool calls
        """
        # This is a simple implementation - can be enhanced with NLP
        tool_calls = []
        
        # Example: Check for weather-related keywords
        if any(word in user_input.lower() for word in ["weather", "temperature", "forecast"]):
            # Extract location if present
            location = self._extract_location(user_input)
            if location:
                tool_calls.append(ToolCall("get_weather", {"location": location}))
        
        # Example: Check for statistics-related keywords
        if any(word in user_input.lower() for word in ["statistics", "calculate", "average", "mean"]):
            # Extract numbers if present
            numbers = self._extract_numbers(user_input)
            if numbers:
                tool_calls.append(ToolCall("calculate_statistics", {"numbers": numbers}))
        
        return tool_calls
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text"""
        # Simple extraction - can be enhanced with NER
        keywords = ["in ", "for ", "at "]
        for keyword in keywords:
            if keyword in text.lower():
                idx = text.lower().find(keyword)
                location = text[idx + len(keyword):].split()[0:2]
                return " ".join(location)
        return None
    
    def _extract_numbers(self, text: str) -> Optional[List[float]]:
        """Extract numbers from text"""
        import re
        numbers = re.findall(r'\d+\.?\d*', text)
        return [float(n) for n in numbers] if numbers else None
    
    def _generate_result(self, execution: AgentExecution) -> Dict[str, Any]:
        """Generate final result from execution"""
        results = []
        
        for tool_call in execution.tool_calls:
            if tool_call.result:
                results.append({
                    "tool": tool_call.tool_name,
                    "result": tool_call.result
                })
        
        return {
            "summary": f"Executed {len(execution.tool_calls)} tool(s)",
            "tool_results": results,
            "execution_time": self._calculate_execution_time(execution)
        }
    
    def _calculate_execution_time(self, execution: AgentExecution) -> str:
        """Calculate execution time"""
        if execution.end_time:
            start = datetime.fromisoformat(execution.start_time)
            end = datetime.fromisoformat(execution.end_time)
            duration = (end - start).total_seconds()
            return f"{duration:.2f}s"
        return "N/A"
    
    def get_execution(self, execution_id: str) -> Optional[AgentExecution]:
        """Get an execution by ID"""
        return self.executions.get(execution_id)
    
    def get_all_executions(self) -> List[AgentExecution]:
        """Get all executions"""
        return list(self.executions.values())


class WeatherAgent(WatsonxAgent):
    """Agent specialized for weather-related tasks"""
    
    def __init__(self, tool_executor: Optional[Callable] = None):
        """Initialize weather agent"""
        tools = [
            {
                "name": "get_weather",
                "description": "Get weather information for a location"
            }
        ]
        super().__init__(
            name="Weather Agent",
            description="Agent for retrieving weather information",
            tools=tools,
            tool_executor=tool_executor
        )
    
    def _parse_user_input(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ToolCall]:
        """Parse user input for weather queries"""
        tool_calls = []
        
        # Extract location
        location = self._extract_location(user_input)
        if location:
            # Extract units if specified
            units = "celsius"
            if "fahrenheit" in user_input.lower() or "°f" in user_input.lower():
                units = "fahrenheit"
            
            tool_calls.append(ToolCall("get_weather", {
                "location": location,
                "units": units
            }))
        
        return tool_calls


class AnalyticsAgent(WatsonxAgent):
    """Agent specialized for data analytics tasks"""
    
    def __init__(self, tool_executor: Optional[Callable] = None):
        """Initialize analytics agent"""
        tools = [
            {
                "name": "calculate_statistics",
                "description": "Calculate statistical measures from data"
            }
        ]
        super().__init__(
            name="Analytics Agent",
            description="Agent for data analysis and statistics",
            tools=tools,
            tool_executor=tool_executor
        )
    
    def _parse_user_input(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ToolCall]:
        """Parse user input for analytics queries"""
        tool_calls = []
        
        # Extract numbers
        numbers = self._extract_numbers(user_input)
        if numbers:
            tool_calls.append(ToolCall("calculate_statistics", {
                "numbers": numbers,
                "measures": ["all"]
            }))
        
        return tool_calls


class AgentFactory:
    """Factory for creating agents"""
    
    @staticmethod
    def create_agent(
        agent_type: str,
        tool_executor: Optional[Callable] = None
    ) -> Optional[WatsonxAgent]:
        """
        Create an agent of the specified type
        
        Args:
            agent_type: Type of agent to create
            tool_executor: Function to execute tools
            
        Returns:
            Agent instance or None if type is unknown
        """
        agents = {
            "weather": WeatherAgent,
            "analytics": AnalyticsAgent,
        }
        
        agent_class = agents.get(agent_type.lower())
        if agent_class:
            return agent_class(tool_executor)
        
        return None
    
    @staticmethod
    def get_available_agents() -> List[str]:
        """Get list of available agent types"""
        return ["weather", "analytics"]

# Made with Bob
