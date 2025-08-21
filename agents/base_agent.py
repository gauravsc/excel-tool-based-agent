from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langfuse.openai import openai
from core.logger import setup_logger

logger = setup_logger(__name__)

class BaseAgent(ABC):
    """Base agent class that provides common functionality for all agents."""
    
    def __init__(self, api_key: str = None):
        """Initialize base agent with OpenAI client and cost tracking."""
        # self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY")) # OpenAI client
        self.client = openai # Langfuse client
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
    
    def reduce_messages(self, messages: List[Dict[str, Any]], max_messages: int = 10) -> List[Dict[str, Any]]:
        """Reduce the message list to a maximum number of messages while preserving system and task prompts."""
        if len(messages) <= max_messages:
            return messages
        
        # Find system and user (task) prompts
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        
        # Keep all system messages and the first user message (task prompt)
        preserved_messages = system_messages + user_messages[:1]
        
        # Calculate how many recent messages we can keep
        remaining_slots = max_messages - len(preserved_messages)
        
        if remaining_slots <= 0:
            # If we can't fit even the preserved messages, just return them
            logger.warning("Message limit too low to preserve system and task prompts. Returning preserved messages only.")
            return preserved_messages
        
        # Get the most recent messages (excluding system and first user message)
        recent_messages = [msg for msg in messages if msg.get("role") not in ["system"] or 
                          (msg.get("role") == "user" and msg not in user_messages[:1])]
        
        # Take the most recent messages that fit in the remaining slots
        recent_messages_to_keep = recent_messages[-remaining_slots:]
        
        # Combine preserved messages with recent messages
        reduced_messages = preserved_messages + recent_messages_to_keep
        
        logger.info("Reduced messages from %d to %d (preserved %d system/task messages, kept %d recent messages)", 
                   len(messages), len(reduced_messages), len(preserved_messages), len(recent_messages_to_keep))
        
        return reduced_messages
    
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