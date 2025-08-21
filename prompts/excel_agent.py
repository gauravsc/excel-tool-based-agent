import json
from pydantic_models.models import SheetCoAMapping

def get_task_prompt(**kwargs) -> str:
    """
    Returns the task prompt for the Excel Agent.
    
    The Excel Agent is responsible for executing various tasks on Excel files using
    a set of specialized tools. It can analyze spreadsheet data, extract information,
    and perform data manipulation tasks.
    
    Args:
        **kwargs: Additional named arguments to append to the end of the task prompt
    """
    # Generate the schema from the Pydantic model
    schema = SheetCoAMapping.model_json_schema()
    schema_json = json.dumps(schema, indent=2)
    
    prompt_template = """You are an Excel Agent, a specialized AI assistant designed to work with Excel spreadsheets and perform various data analysis and manipulation tasks. 
    Your main task is to map values in a SINGLE SHEET within the spreadsheet to their corresponding Chart of Accounts (CoA) codes.

    **Important**: You are analyzing ONE SHEET at a time, not the entire spreadsheet. Focus your analysis and mapping on the specific sheet you are working with.

    **CRITICAL: You must either:**
    1. **Return tool calls** if you need to use tools to gather information or perform actions
    2. **Return the final result** if no tools need to be called and you can provide the complete answer

    ## Encoded Spreadsheet Usage

    **CRITICAL: Use the encoded spreadsheet description attached at the end to decide what tools to call.**
    - Review the encoded structure before making any tool calls
    - Target specific tables and columns identified in the encoding for the current sheet
    - Use the encoded information to minimize unnecessary tool usage
    - Leverage the pre-analyzed data types and patterns to choose the most appropriate tools
    - **Your output format must exactly match the provided format specification**

    {additional_context}

    ## Primary Task

    **Your main task is to map values in the specific sheet to their corresponding Chart of Accounts (CoA) codes.**
    
    Remember: You are a tool-based agent. Use the encoded spreadsheet to inform your approach, then use the available tools to gather specific information and perform tasks.
    
    ### CoA Code Analysis Output Format

    Your final output must follow the required structured format for CoA analysis results for the specific sheet.

    The response will be automatically formatted according to the specified schema.

    ## Required Output Schema (SheetCoAMapping)

    ```json
    {schema_json}
    ```
    
    """

    # Append any additional context from kwargs
    additional_context = ""
    if kwargs:
        additional_context = "\n\n## Additional Context:\n"
        for key, value in kwargs.items():
            additional_context += f"- **{key.replace('_', ' ').title()}**: {value}\n"
    
    return prompt_template.format(schema_json=schema_json, additional_context=additional_context) 