import os
import json
from dotenv import load_dotenv
from agents import ExcelAgent, SpreadsheetEncoderAgent, SheetSelectorAgent
from core.logger import setup_logger
from core.utils import remove_hidden_columns_all_sheets
from core.utils import get_sheet_names
from langfuse.openai import openai



logger = setup_logger(__name__)

def main():
    """Example usage of ExcelAgent and SpreadsheetEncoderAgent."""
    logger.info("Starting ExcelAgent application")
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    logger.info("Environment variables loaded")

    client_name = "client_1"
    excel_file = f"data/{client_name}/{client_name}.xlsx"
    encoded_sheets_dir = f"data/{client_name}/encoded_sheets"
    client_coa_mapping_file = f"data/{client_name}/{client_name}_coa.json"

    # Clean the spreadsheet by removing hidden columns
    # logger.info("=== Cleaning spreadsheet by removing hidden columns ===")
    # removed_columns_by_sheet = remove_hidden_columns_all_sheets(excel_file, output_path=excel_file)
    # for sheet_name, removed_columns in removed_columns_by_sheet.items():
    #     if removed_columns:
    #         logger.info("Removed %d hidden columns from %s", len(removed_columns), sheet_name)
    #     else:
    #         logger.info("No hidden columns found in %s", sheet_name)

    # Create encoded_sheets directory if it doesn't exist
    os.makedirs(encoded_sheets_dir, exist_ok=True)
    
    # Get sheet names
    logger.info("=== Getting sheet names ===")
    sheet_names = get_sheet_names(excel_file)
    logger.info("Found %d sheets: %s", len(sheet_names), sheet_names)
    
    # Load CoA items from the client's CoA mapping file
    logger.info("=== Loading CoA items ===")
    with open(client_coa_mapping_file, "r", encoding="utf-8") as f:
        coa_items = json.load(f)
    logger.info("Loaded %d CoA items", len(coa_items))
    
    # Use SheetSelectorAgent to identify which sheets contain CoA-related data
    logger.info("=== Using SheetSelectorAgent to identify relevant sheets ===")
    sheet_selector_agent = SheetSelectorAgent(api_key=api_key)
    sheet_selection_response = sheet_selector_agent.select_sheets(sheet_names, coa_items, excel_file_path=excel_file)
    
    # Get the selected sheet names
    selected_sheet_names = [sheet.sheet_name for sheet in sheet_selection_response.selected_sheets if sheet.include]
    logger.info("Selected %d sheets for encoding: %s", len(selected_sheet_names), selected_sheet_names)
    
    # Save the selected sheet names to a JSON file in the client folder
    selected_sheets_file = f"data/{client_name}/selected_sheets.json"
    with open(selected_sheets_file, "w", encoding="utf-8") as f:
        json.dump(selected_sheet_names, f, indent=2, ensure_ascii=False)
    logger.info("Saved selected sheet names to: %s", selected_sheets_file)
    
    # Encode only the selected sheets
    logger.info("=== Encoding selected sheets ===")
    encoder_agent = SpreadsheetEncoderAgent(api_key=api_key)
    all_sheet_encodings = []
    
    for sheet_name in selected_sheet_names:
        logger.info("Encoding sheet: %s", sheet_name)
        sheet_encoding = encoder_agent.encode(excel_file, sheet_name=sheet_name)
        
        # Save individual sheet encoding to separate JSON file
        sheet_filename = f"{sheet_name}.json"
        sheet_filepath = os.path.join(encoded_sheets_dir, sheet_filename)
        with open(sheet_filepath, "w", encoding="utf-8") as f:
            json.dump(sheet_encoding.model_dump(), f, indent=2, ensure_ascii=False)
        logger.info("Saved sheet encoding to: %s", sheet_filepath)
        
        all_sheet_encodings.append(sheet_encoding)
        logger.info("Successfully encoded sheet: %s", sheet_name)
    
    logger.info("Successfully encoded all selected sheets and saved individual files to %s", encoded_sheets_dir)
   
    
    # Example 2: Use ExcelAgent for task execution
    
    # logger.info("Reading CoA codes from file")
    # with open("data/coa_codes.txt", "r", encoding="utf-8") as f:
    #     coa_text = f.read()
    # logger.info("Read %d characters from coa_codes.txt", len(coa_text))
    
    # agent = ExcelAgent(api_key=api_key)
    # logger.info("Executing task on Excel file: %s", excel_file)
    # result = agent.execute(excel_file, coa_text=coa_text)
    
    # logger.info("Task execution completed successfully")
    # logger.info("Result length: %d characters", len(result))
    # print("\nTask Execution Result:")
    # print(result)

if __name__ == "__main__":
    main()
