from agents.base_agent import BaseAgent
from tools.tools import (
    get_sheet_names, get_row_values, get_column_values, get_cell_value,
    get_data_types_column, get_sheet_dimensions,
    find_cells_with_value, get_range_values, get_sheet_content,
    get_max_rows, get_max_columns
)
from core.logger import setup_logger
from prompts.excel_agent import get_system_prompt

logger = setup_logger(__name__)

class ExcelAgent(BaseAgent):
    """Agent that executes Excel tasks using OpenAI LLM and tool calls."""
    
    def __init__(self, api_key: str = None):
        """Initialize with OpenAI API key."""
        super().__init__(api_key)
        self.tools = [
            get_sheet_names, get_row_values, get_column_values, get_cell_value,
            get_data_types_column, get_sheet_dimensions,
            find_cells_with_value, get_range_values, get_sheet_content,
            get_max_rows, get_max_columns
        ]
        logger.info("ExcelAgent initialized")
        self.model = "o3"
    
    def get_tools(self):
        """Return the list of tools available to this agent."""
        return self.tools
    
    def execute(self, task_description: str, excel_file_path: str, **prompt_kwargs) -> str:
        """Execute task on Excel file using LLM and tools."""
        logger.info(f"Starting task execution: {task_description[:100]}...")
        logger.info(f"Excel file: {excel_file_path}")
        
        # Get system prompt with any additional context including file path
        system_prompt = get_system_prompt(excel_file_path=excel_file_path, **prompt_kwargs)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Task: {task_description}\nExcel file: {excel_file_path}"}
        ]
        iteration = 0
        max_iterations = 20
        
        # Format tools for OpenAI API
        tools = []
        for tool in self.tools:
            tool_schema = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.args_schema.schema() if hasattr(tool, 'args_schema') else {}
                }
            }
            tools.append(tool_schema)
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"LLM iteration {iteration}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            # Update cost tracker with response information
            self.update_cost_tracker(response)
            
            message = response.choices[0].message
            messages.append(message)
            
            if not message.tool_calls:
                logger.info("No more tool calls, task completed")
                final_cost = self.compute_total_cost()
                logger.info(f"Task completed. Final cost: ${final_cost['total_cost_usd']} (API calls: {final_cost['api_calls']}, tokens: {final_cost['total_tokens']})")
                return message.content
            
            logger.info(f"LLM requested {len(message.tool_calls)} tool calls")
            
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = eval(tool_call.function.arguments)
                tool_args['file_path'] = excel_file_path
                
                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                
                tool_func = next(tool for tool in self.tools if tool.name == tool_name)
                result = tool_func.invoke(tool_args)
                
                logger.info(f"Tool {tool_name} returned result: {str(result)[:200]}...")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
        
        logger.warning(f"Reached maximum iterations ({max_iterations}), stopping execution")
        final_cost = self.compute_total_cost()
        logger.info(f"Task stopped due to max iterations. Final cost: ${final_cost['total_cost_usd']} (API calls: {final_cost['api_calls']}, tokens: {final_cost['total_tokens']})")
        return "Task execution stopped due to maximum iteration limit reached."
