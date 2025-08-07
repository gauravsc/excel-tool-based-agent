import os
from abc import ABC, abstractmethod
from openai import OpenAI
from typing import List, Dict, Any
from core.logger import setup_logger

logger = setup_logger(__name__)

class BaseAgent(ABC):
    """Base agent class that provides common functionality for all agents."""
    
    def __init__(self, api_key: str = None):
        """Initialize base agent with OpenAI client and cost tracking."""
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.cost_tracker = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "api_calls": 0,
            "model_used": None
        }
        logger.info("%s initialized", self.__class__.__name__)
        self.model = None
    
    @abstractmethod
    def get_tools(self) -> List[Any]:
        """Return the list of tools available to this agent."""
        pass
    
    def compute_total_cost(self) -> Dict[str, Any]:
        """Compute and return the total cost incurred by the agent."""
        pricing = {
            "o3": {"input": 0.002, "output": 0.008},
        }
        
        model = self.model
        model_pricing = pricing[self.model]
        
        input_cost = (self.cost_tracker["prompt_tokens"] / 1000) * model_pricing["input"]
        output_cost = (self.cost_tracker["completion_tokens"] / 1000) * model_pricing["output"]
        total_cost = input_cost + output_cost
        
        return {
            "model_used": model,
            "api_calls": self.cost_tracker["api_calls"],
            "total_tokens": self.cost_tracker["total_tokens"],
            "prompt_tokens": self.cost_tracker["prompt_tokens"],
            "completion_tokens": self.cost_tracker["completion_tokens"],
            "total_cost_usd": round(total_cost, 6)
        }
    
    def update_cost_tracker(self, response: Any) -> None:
        """Update the cost tracker with information from an API response."""
        if hasattr(response, 'usage'):
            usage = response.usage
            self.cost_tracker["total_tokens"] += usage.total_tokens
            self.cost_tracker["prompt_tokens"] += usage.prompt_tokens
            self.cost_tracker["completion_tokens"] += usage.completion_tokens
        
        if hasattr(response, 'model'):
            self.cost_tracker["model_used"] = response.model
        
        self.cost_tracker["api_calls"] += 1
        
        # Log current cost after each API call
        current_cost = self.compute_total_cost()
        logger.info("Current cost for %s: $%s (API calls: %s, tokens: %s)", self.__class__.__name__, current_cost['total_cost_usd'], current_cost['api_calls'], current_cost['total_tokens']) 