import os
from dotenv import load_dotenv
from agents import ExcelAgent
from core.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Example usage of ExcelAgent."""
    logger.info("Starting ExcelAgent application")
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    logger.info("Environment variables loaded")
    
    agent = ExcelAgent(api_key=api_key)
    
    # Example task
    task_description = "Map values to the CoA codes based on the CoA codes in the below text"
    logger.info(f"Task description: {task_description}")
    
    logger.info("Reading CoA codes from file")
    with open("data/coa_codes.txt", "r", encoding="utf-8") as f:
        coa_text = f.read()
    logger.info(f"Read {len(coa_text)} characters from coa_codes.txt")
    
    task = f"{task_description}\n\n{coa_text}"
    excel_file = "data/dummy_financials.xlsx"
    
    logger.info(f"Executing task on Excel file: {excel_file}")
    result = agent.execute(task, excel_file)
    
    logger.info("Task execution completed successfully")
    logger.info(f"Result length: {len(result)} characters")
    print(result)

if __name__ == "__main__":
    main()
