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
            logger.info("Removed %d hidden columns from %s", len(removed_columns), sheet_name)
        else:
            logger.info("No hidden columns found in %s", sheet_name)

    # Example 1: Use SpreadsheetEncoderAgent to get structure
    # logger.info("=== Using SpreadsheetEncoderAgent ===")
    # encoder_agent = SpreadsheetEncoderAgent(api_key=api_key)
    
    # Get LLM-generated encoding
    # llm_encoding = encoder_agent.encode(excel_file)
    # logger.info("LLM encoding completed")
    # print("LLM-Generated Encoding:")
    # print(llm_encoding)
    
    # Load encoded spreadsheet from file
    logger.info("=== Loading encoded spreadsheet from file ===")
    with open("encoded_spreadsheet.txt", "r", encoding="utf-8") as f:
        encoded_spreadsheet_content = f.read()
    logger.info("Successfully loaded encoded spreadsheet from file")
   
    
    # Example 2: Use ExcelAgent for task execution with encoded spreadsheet
    
    logger.info("Reading CoA codes from file")
    with open("data/coa_codes.txt", "r", encoding="utf-8") as f:
        coa_text = f.read()
    logger.info("Read %d characters from coa_codes.txt", len(coa_text))
    
    
    
    agent = ExcelAgent(api_key=api_key)
    logger.info("Executing task on Excel file: %s with encoded spreadsheet", excel_file)
    result = agent.execute(excel_file, coa_text=coa_text, encoded_spreadsheet=encoded_spreadsheet_content)
    
    logger.info("Task execution completed successfully")
    logger.info("Result length: %d characters", len(result))
    print("\nTask Execution Result:")
    print(result)

if __name__ == "__main__":
    main()
