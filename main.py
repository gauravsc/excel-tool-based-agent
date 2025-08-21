import os
import json
from dotenv import load_dotenv
from agents import SpreadsheetEncoderAgent, SheetSelectorAgent, ExcelAgent
from core.logger import setup_logger
from core.utils import get_sheet_names


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
    
    # Check if selected sheets file exists
    selected_sheets_file = f"data/{client_name}/selected_sheets.json"
    
    if os.path.exists(selected_sheets_file):
        # Load existing selected sheet names
        logger.info("=== Loading existing selected sheets from file ===")
        with open(selected_sheets_file, "r", encoding="utf-8") as f:
            selected_sheet_names = json.load(f)
        logger.info("Loaded %d selected sheets from file: %s", len(selected_sheet_names), selected_sheet_names)
    else:
        # Use SheetSelectorAgent to identify which sheets contain CoA-related data
        logger.info("=== Using SheetSelectorAgent to identify relevant sheets ===")
        sheet_selector_agent = SheetSelectorAgent(api_key=api_key)
        sheet_selection_response = sheet_selector_agent.select_sheets(sheet_names, coa_items, excel_file_path=excel_file)
        
        # Get the selected sheet names
        selected_sheet_names = [sheet.sheet_name for sheet in sheet_selection_response.selected_sheets if sheet.include]
        logger.info("Selected %d sheets for encoding: %s", len(selected_sheet_names), selected_sheet_names)
        
        # Save the selected sheet names to a JSON file in the client folder
        with open(selected_sheets_file, "w", encoding="utf-8") as f:
            json.dump(selected_sheet_names, f, indent=2, ensure_ascii=False)
        logger.info("Saved selected sheet names to: %s", selected_sheets_file)


    
    
    # # Encode only the selected sheets
    # logger.info("=== Encoding selected sheets ===")
    # encoder_agent = SpreadsheetEncoderAgent(api_key=api_key)
    # all_sheet_encodings = []
    
    # for sheet_name in selected_sheet_names:
    #     logger.info("Encoding sheet: %s", sheet_name)
    #     sheet_encoding = encoder_agent.encode(excel_file, sheet_name=sheet_name)
        
    #     # Save individual sheet encoding to separate JSON file
    #     sheet_filename = f"{sheet_name}.json"
    #     sheet_filepath = os.path.join(encoded_sheets_dir, sheet_filename)
    #     with open(sheet_filepath, "w", encoding="utf-8") as f:
    #         json.dump(sheet_encoding.model_dump(), f, indent=2, ensure_ascii=False)
    #     logger.info("Saved sheet encoding to: %s", sheet_filepath)
        
    #     all_sheet_encodings.append(sheet_encoding)
    #     logger.info("Successfully encoded sheet: %s", sheet_name)
    
    # logger.info("Successfully encoded all selected sheets and saved individual files to %s", encoded_sheets_dir)
   
    
    # Example 2: Use ExcelAgent for task execution on each selected sheet
    selected_sheet_names = [
        "Exceptionals",
        "FY25 Capex",
        "FY25 Full Year",
        "FY25 Monthly P&L",
        "FY25 Restaurants",
    ]
    
    logger.info("Reading CoA codes from client mapping file")
    with open(client_coa_mapping_file, "r", encoding="utf-8") as f:
        coa_items = json.load(f)
    logger.info("Read %d CoA items from %s", len(coa_items), client_coa_mapping_file)
    
    # Create mappings directory if it doesn't exist
    mappings_dir = f"data/{client_name}/mappings"
    os.makedirs(mappings_dir, exist_ok=True)
    
    # Process each selected sheet with ExcelAgent
    logger.info("=== Processing selected sheets with ExcelAgent ===")
    agent = ExcelAgent(api_key=api_key)
    
    for sheet_name in selected_sheet_names:
        logger.info("Processing sheet: %s", sheet_name)
        
        # Execute CoA mapping for this sheet
        result = agent.execute(excel_file, sheet_name=sheet_name, coa_items=coa_items)
        
        # Save the mapping result to a JSON file
        mapping_filename = f"{sheet_name}.json"
        mapping_filepath = os.path.join(mappings_dir, mapping_filename)
        with open(mapping_filepath, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)
        logger.info("Saved mapping result to: %s", mapping_filepath)
        
        logger.info("Successfully processed sheet: %s", sheet_name)
    
    logger.info("Successfully processed all selected sheets and saved mapping results to %s", mappings_dir)

if __name__ == "__main__":
    main()
