from openpyxl import load_workbook
from typing import List, Any, Dict
from datetime import datetime, date
import re
from langchain.tools import tool
from core.logger import setup_logger
from tools.utils import get_detailed_data_types

logger = setup_logger(__name__)


@tool
def get_sheet_names(file_path: str) -> List[str]:
    """Get all sheet names from the Excel file."""
    logger.info(f"Getting sheet names from {file_path}")
    workbook = load_workbook(file_path)
    result = workbook.sheetnames
    logger.info(f"Found {len(result)} sheets: {result}")
    return result


@tool
def get_row_values(file_path: str, sheet_name: str, row_number: int) -> List[Any]:
    """Get all values from a specific row in the Excel sheet."""
    logger.info(f"Getting row {row_number} values from sheet '{sheet_name}' in {file_path}")
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    result = [cell.value for cell in sheet[row_number]]
    logger.info(f"Row {row_number} has {len(result)} values")
    return result


@tool
def get_column_values(file_path: str, sheet_name: str, column_letter: str) -> List[Any]:
    """Get all values from a specific column in the Excel sheet."""
    logger.info(f"Getting column {column_letter} values from sheet '{sheet_name}' in {file_path}")
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    result = [cell.value for cell in sheet[column_letter]]
    logger.info(f"Column {column_letter} has {len(result)} values")
    return result


@tool
def get_cell_value(file_path: str, sheet_name: str, cell_reference: str) -> Any:
    """Get the value of a specific cell in the Excel sheet."""
    logger.info(f"Getting cell {cell_reference} value from sheet '{sheet_name}' in {file_path}")
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    result = sheet[cell_reference].value
    logger.info(f"Cell {cell_reference} value: {result}")
    return result


@tool
def get_data_types_column(file_path: str, sheet_name: str, column_letter: str) -> List[str]:
    """Get the data types of all values in a specific column."""
    logger.info(f"Getting data types for column {column_letter} in sheet '{sheet_name}' from {file_path}")
    # Read the column values directly instead of calling get_column_values
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    result = [cell.value for cell in sheet[column_letter]]
    logger.info(f"Column {column_letter} has {len(result)} values")
    return get_detailed_data_types(result)


@tool
def get_sheet_dimensions(file_path: str, sheet_name: str) -> Dict[str, int]:
    """Get the number of rows and columns in the Excel sheet."""
    logger.info(f"Getting dimensions for sheet '{sheet_name}' in {file_path}")
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    result = {"rows": sheet.max_row, "columns": sheet.max_column}
    logger.info(f"Sheet '{sheet_name}' dimensions: {result['rows']} rows x {result['columns']} columns")
    return result


@tool
def get_max_rows(file_path: str, sheet_name: str) -> int:
    """Get the maximum number of rows in the Excel sheet."""
    logger.info(f"Getting max rows for sheet '{sheet_name}' in {file_path}")
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    result = sheet.max_row
    logger.info(f"Sheet '{sheet_name}' has {result} rows")
    return result


@tool
def get_max_columns(file_path: str, sheet_name: str) -> int:
    """Get the maximum number of columns in the Excel sheet."""
    logger.info(f"Getting max columns for sheet '{sheet_name}' in {file_path}")
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    result = sheet.max_column
    logger.info(f"Sheet '{sheet_name}' has {result} columns")
    return result


# @tool
# def get_header_row(file_path: str, sheet_name: str, header_row: int = 1) -> List[str]:
#     """Get the header row values from the Excel sheet."""
#     logger.info(f"Getting header row {header_row} from sheet '{sheet_name}' in {file_path}")
#     result = get_row_values(file_path, sheet_name, header_row)
#     logger.info(f"Header row contains {len(result)} columns")
#     return result


@tool
def find_cells_with_value(file_path: str, sheet_name: str, search_value: Any) -> List[str]:
    """Find all cell references that contain a specific value."""
    logger.info(f"Searching for value '{search_value}' in sheet '{sheet_name}' from {file_path}")
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    cells = []
    for row in sheet.iter_rows():
        for cell in row:
            if cell.value == search_value:
                cells.append(cell.coordinate)
    logger.info(f"Found {len(cells)} cells with value '{search_value}': {cells}")
    return cells


@tool
def get_range_values(file_path: str, sheet_name: str, start_cell: str, end_cell: str) -> List[List[Any]]:
    """Get values from a range of cells in the Excel sheet."""
    logger.info(f"Getting range {start_cell}:{end_cell} from sheet '{sheet_name}' in {file_path}")
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    range_data = sheet[start_cell:end_cell]
    result = [[cell.value for cell in row] for row in range_data]
    logger.info(f"Range {start_cell}:{end_cell} contains {len(result)} rows")
    return result


@tool
def get_sheet_content(file_path: str, sheet_name: str) -> Dict[int, Dict[str, Any]]:
    """Get all content of the sheet as a nested dictionary where outer dict keys are row numbers and inner dict keys are column letters."""
    logger.info(f"Getting all content from sheet '{sheet_name}' in {file_path}")
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    
    result = {}
    for row in sheet.iter_rows():
        row_dict = {}
        for cell in row:
            if cell.value is not None:  # Only include non-empty cells
                row_dict[cell.column_letter] = cell.value
        if row_dict:  # Only include rows with data
            result[cell.row] = row_dict
    
    logger.info(f"Retrieved {len(result)} rows with data from sheet '{sheet_name}'")
    return result

