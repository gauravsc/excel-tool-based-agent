import json
from agents.base_agent import BaseAgent
from tools.tools import (
    get_row_values_sample, get_column_values_sample, get_data_types_column_sample, get_sheet_dimensions,
    get_range_values, get_sheet_content_sample,
    get_max_rows, get_max_columns, get_nonempty_column_letters
)
from core.logger import setup_logger
from prompts.spreadsheet_encoder_agent import get_task_prompt
from pydantic_models.models import SingleSheetEncoding


logger = setup_logger(__name__)

class SpreadsheetEncoderAgent(BaseAgent):
    """Agent that generates compressed representation of spreadsheet structure and data types."""
    
    def __init__(self, api_key: str = None):
        """Initialize with OpenAI API key."""
        super().__init__(api_key)
        self.tools = [
            get_row_values_sample, get_column_values_sample,
            get_data_types_column_sample, get_sheet_dimensions,
            get_max_rows, get_max_columns, get_nonempty_column_letters
        ]
        logger.info("SpreadsheetEncoderAgent initialized")
        # INSERT_YOUR_CODE
        self.model = "o3"
        
    def get_tools(self):
        """Return the list of tools available to this agent."""
        return self.tools
    
    def encode(self, excel_file_path: str, sheet_name: str = None, **prompt_kwargs) -> SingleSheetEncoding:
        """Generate compressed representation of spreadsheet structure and data."""
        logger.info("Starting spreadsheet encoding for: %s", excel_file_path)
        
        # Get task prompt with any additional context including file path and sheet name
        task_prompt = get_task_prompt(excel_file_path=excel_file_path, sheet_name=sheet_name, **prompt_kwargs)
        logger.info("Task prompt: %s", task_prompt)
        
        messages = [
            {"role": "system", "content": "You are an expert financial analyst that understands spreadsheets."},
            {"role": "user", "content": task_prompt}
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
            # INSERT_YOUR_CODE
            print("=" * 80)
            logger.info("LLM iteration %d", iteration)
            
            # Reduce messages to prevent context from becoming too long
            # messages = self.reduce_messages(messages)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                # response_format={"type": "json_schema", "json_schema": SingleSheetEncoding.model_json_schema()}
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
        # Remove the last message (the LLM's final response) before parsing
        final_cost = self.compute_total_cost()
        logger.info("Encoding completed. Final cost: $%s (API calls: %s, tokens: %s)", final_cost['total_cost_usd'], final_cost['api_calls'], final_cost['total_tokens'])
        
        # Write the final response to a file called dump.txt
        if message.content:
            with open("dump.txt", "w", encoding="utf-8") as f:
                f.write(message.content)
            logger.info("Final encoding written to file: dump.txt")

        # Get structured response using chat.completions.create with response_format
        pydantic_schema = SingleSheetEncoding.model_json_schema()
        json_schema = {
            "name": pydantic_schema['title'],
            "schema": pydantic_schema
        }
        logger.info("JSON schema: %r", json_schema)
        final_response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_schema", "json_schema": json_schema},
        )

        logger.info("Final LLM response object: %r", final_response)
        
        # Update cost tracker with final response
        self.update_cost_tracker(final_response)

        # Parse the JSON response into SingleSheetEncoding
        response_content = final_response.choices[0].message.content
        parsed_data = json.loads(response_content)
        parsed_response = SingleSheetEncoding(**parsed_data)
        
        logger.info("Successfully parsed response into SingleSheetEncoding")
        return parsed_response
    