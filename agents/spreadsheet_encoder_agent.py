import os
from openai import OpenAI
from tools.tools import (
    get_sheet_names, get_row_values_sample, get_column_values_sample, get_data_types_column_sample, get_sheet_dimensions,
    get_range_values, get_sheet_content,
    get_max_rows, get_max_columns
)
from core.logger import setup_logger
from prompts.spreadsheet_encoder_agent import get_system_prompt

logger = setup_logger(__name__)

class SpreadsheetEncoderAgent:
    """Agent that generates compressed representation of spreadsheet structure and data types."""
    
    def __init__(self, api_key: str = None):
        """Initialize with OpenAI API key."""
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.tools = [
            get_sheet_names, get_row_values_sample, get_column_values_sample,
            get_data_types_column_sample, get_sheet_dimensions,
            get_range_values, get_sheet_content,
            get_max_rows, get_max_columns
        ]
        logger.info("SpreadsheetEncoderAgent initialized")
    
    def encode(self, excel_file_path: str, **prompt_kwargs) -> str:
        """Generate compressed representation of spreadsheet structure and data."""
        logger.info(f"Starting spreadsheet encoding for: {excel_file_path}")
        
        # Get system prompt with any additional context
        system_prompt = get_system_prompt(**prompt_kwargs)
        
        messages = [
            {"role": "system", "content": "You are an expert financial analyst that understands spreadsheets."},
            {"role": "user", "content": system_prompt}
        ]
        iteration = 0
        max_iterations = 50
        
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
            # INSERT_YOUR_CODE
            print("=" * 80)
            logger.info(f"LLM iteration {iteration}")
            
            response = self.client.chat.completions.create(
                model="o3",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            messages.append(message)
            
            if not message.tool_calls:
                logger.info("No more tool calls, encoding completed")
                return message.content
            
            logger.info(f"LLM requested {len(message.tool_calls)} tool calls")
            
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = eval(tool_call.function.arguments)
                tool_args['file_path'] = excel_file_path
                
                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                
                tool_func = next(tool for tool in self.tools if tool.name == tool_name)
                logger.info(f"Calling tool function: {tool_name} with arguments: {tool_args}")
                result = tool_func.invoke(tool_args)
                
                logger.info(f"Tool {tool_name} returned result: {str(result)[:200]}...")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
        
        logger.warning(f"Reached maximum iterations ({max_iterations}), stopping encoding")
        return "Spreadsheet encoding stopped due to maximum iteration limit reached." 