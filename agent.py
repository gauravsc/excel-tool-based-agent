import os
from typing import List, Any
from openai import OpenAI
from tools.tools import (
    get_sheet_names, get_row_values, get_column_values, get_cell_value,
    get_detailed_data_types, get_data_types_column, get_sheet_dimensions,
    get_header_row, find_cells_with_value, get_range_values
)
from core.logger import logger

class ExcelAgent:
    """Agent that executes Excel tasks using OpenAI LLM and tool calls."""
    
    def __init__(self, api_key: str = None):
        """Initialize with OpenAI API key."""
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.tools = [
            get_sheet_names, get_row_values, get_column_values, get_cell_value,
            get_detailed_data_types, get_data_types_column, get_sheet_dimensions,
            get_header_row, find_cells_with_value, get_range_values
        ]
        logger.info("ExcelAgent initialized")
    
    def execute(self, task_description: str, excel_file_path: str) -> str:
        """Execute task on Excel file using LLM and tools."""
        logger.info(f"Starting task execution: {task_description[:100]}...")
        logger.info(f"Excel file: {excel_file_path}")
        
        messages = [{"role": "user", "content": f"Task: {task_description}\nExcel file: {excel_file_path}"}]
        iteration = 0
        
        while True:
            iteration += 1
            logger.info(f"LLM iteration {iteration}")
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=[{"type": "function", "function": tool.schema} for tool in self.tools],
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            messages.append(message)
            
            if not message.tool_calls:
                logger.info("No more tool calls, task completed")
                return message.content
            
            logger.info(f"LLM requested {len(message.tool_calls)} tool calls")
            
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = eval(tool_call.function.arguments)
                tool_args['file_path'] = excel_file_path
                
                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                
                tool_func = next(tool for tool in self.tools if tool.name == tool_name)
                result = tool_func(**tool_args)
                
                logger.info(f"Tool {tool_name} returned result: {str(result)[:200]}...")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
