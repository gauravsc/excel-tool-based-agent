import os
from dotenv import load_dotenv
from agents import ExcelAgent, SpreadsheetEncoderAgent
from core.logger import setup_logger
from core.utils import remove_hidden_columns_all_sheets

logger = setup_logger(__name__)

def main():
    """Example usage of ExcelAgent and SpreadsheetEncoderAgent."""
    logger.info("Starting ExcelAgent application")
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    logger.info("Environment variables loaded")
    
    excel_file = "data/single_sheet.xlsx"

    # Clean the spreadsheet by removing hidden columns
    logger.info("=== Cleaning spreadsheet by removing hidden columns ===")
    removed_columns_by_sheet = remove_hidden_columns_all_sheets(excel_file, output_path=excel_file)
    for sheet_name, removed_columns in removed_columns_by_sheet.items():
        if removed_columns:
            logger.info(f"Removed {len(removed_columns)} hidden columns from {sheet_name}")
        else:
            logger.info(f"No hidden columns found in {sheet_name}")

    # Example 1: Use SpreadsheetEncoderAgent to get structure
    logger.info("=== Using SpreadsheetEncoderAgent ===")
    encoder_agent = SpreadsheetEncoderAgent(api_key=api_key)
    
    # Get LLM-generated encoding
    llm_encoding = encoder_agent.encode(excel_file)
    logger.info("LLM encoding completed")
    print("LLM-Generated Encoding:")
    print(llm_encoding)
    
    # Example 2: Use ExcelAgent for task execution
    logger.info("=== Using ExcelAgent ===")
    task_description = "Map values to the CoA codes based on the CoA codes in the below text"
    logger.info(f"Task description: {task_description}")
    
    logger.info("Reading CoA codes from file")
    with open("data/coa_codes.txt", "r", encoding="utf-8") as f:
        coa_text = f.read()
    logger.info(f"Read {len(coa_text)} characters from coa_codes.txt")
    
    task = f"{task_description}\n\n{coa_text}"
    
    agent = ExcelAgent(api_key=api_key)
    logger.info(f"Executing task on Excel file: {excel_file}")
    result = agent.execute(task, excel_file)
    
    logger.info("Task execution completed successfully")
    logger.info(f"Result length: {len(result)} characters")
    print("\nTask Execution Result:")
    print(result)

if __name__ == "__main__":
    main()
