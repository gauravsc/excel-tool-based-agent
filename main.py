from agent import ExcelAgent
from core.logger import logger

def main():
    """Example usage of ExcelAgent."""
    logger.info("Starting ExcelAgent application")
    
    agent = ExcelAgent()
    
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
