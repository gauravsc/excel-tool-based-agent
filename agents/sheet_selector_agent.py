import json
from typing import List
from agents.base_agent import BaseAgent
from tools.tools import (
    get_row_values_sample, get_column_values_sample, get_data_types_column_sample, get_sheet_dimensions,
    get_range_values, get_sheet_content_sample,
    get_max_rows, get_max_columns, get_nonempty_column_letters
)
from core.logger import setup_logger
from prompts.sheet_selector_agent import get_task_prompt
from pydantic_models.models import SheetSelectionResponse

logger = setup_logger(__name__)

class SheetSelectorAgent(BaseAgent):
    """Agent that identifies which sheets are likely to contain CoA-related data."""
    
    def __init__(self, api_key: str = None):
        """Initialize with OpenAI API key."""
        super().__init__(api_key)
        self.tools = [
            get_row_values_sample, get_column_values_sample,
            get_data_types_column_sample, get_sheet_dimensions,
            get_max_rows, get_max_columns, get_nonempty_column_letters
        ]
        self.model = "o3"
        logger.info("SheetSelectorAgent initialized")
        
    def get_tools(self):
        """Return the list of tools available to this agent."""
        return self.tools
    
    def select_sheets(self, sheet_names: List[str], coa_items: List[str], excel_file_path: str = None) -> SheetSelectionResponse:
        """Analyze sheet names and determine which ones are likely to contain CoA-related data."""
        logger.info("Starting sheet selection analysis for %d sheets", len(sheet_names))
        
        # Get task prompt
        task_prompt = get_task_prompt(sheet_names=sheet_names, coa_items=coa_items, excel_file_path=excel_file_path)
        logger.info("Task prompt generated")
        logger.info("Task prompt: %s", task_prompt)
        
        messages = [
            {"role": "system", "content": "You are an expert financial analyst that understands Chart of Accounts and financial statements."},
            {"role": "user", "content": task_prompt}
        ]
        
        iteration = 0
        max_iterations = 10  # Lower than spreadsheet encoder since this is simpler
        
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
            print("=" * 80)
            logger.info("LLM iteration %d", iteration)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
            
            # Update cost tracker with response information
            self.update_cost_tracker(response)
            
            message = response.choices[0].message

            if not message.tool_calls:
                break
            
            messages.append(message)
        
            logger.info("LLM requested %d tool calls", len(message.tool_calls))
            
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = eval(tool_call.function.arguments)
                tool_args['file_path'] = excel_file_path
                
                logger.info("Executing tool: %s with args: %s", tool_name, tool_args)
                
                tool_func = next(tool for tool in self.tools if tool.name == tool_name)
                logger.info("Calling tool function: %s with arguments: %s", tool_name, tool_args)
                result = tool_func.invoke(tool_args)
                
                logger.info("Tool %s returned result: %s...", tool_name, str(result)[:200])
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

        logger.info("LLM response text: %s", message.content)
        
        # Get structured response using chat.completions.create with response_format
        pydantic_schema = SheetSelectionResponse.model_json_schema()
        json_schema = {
            "name": pydantic_schema['title'],
            "schema": pydantic_schema
        }
        
        logger.info("Requesting final structured response from LLM")
        final_response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_schema", "json_schema": json_schema},
        )

        # Update cost tracker with final response
        self.update_cost_tracker(final_response)

        # Parse the JSON response
        response_content = final_response.choices[0].message.content
        parsed_data = json.loads(response_content)
        parsed_response = SheetSelectionResponse(**parsed_data)
        
        # Log the results
        included_sheets = [sheet.sheet_name for sheet in parsed_response.selected_sheets if sheet.include]
        excluded_sheets = [sheet.sheet_name for sheet in parsed_response.selected_sheets if not sheet.include]
        
        logger.info("Sheet selection completed:")
        logger.info("Included sheets (%d): %s", len(included_sheets), included_sheets)
        logger.info("Excluded sheets (%d): %s", len(excluded_sheets), excluded_sheets)
        
        # Log final cost
        final_cost = self.compute_total_cost()
        logger.info("Sheet selection completed. Final cost: $%s (API calls: %s, tokens: %s)", 
                   final_cost['total_cost_usd'], final_cost['api_calls'], final_cost['total_tokens'])
        
        return parsed_response
    