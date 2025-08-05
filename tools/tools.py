from openpyxl import load_workbook
from typing import List, Any, Dict
from datetime import datetime, date
import re
from langchain.tools import tool
from core.logger import logger


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
def get_detailed_data_types(values: List[Any]) -> List[str]:
    """Get detailed data types of values including dates, times, percentages, etc."""
    logger.info(f"Analyzing data types for {len(values)} values")
    def categorize_value(value):
        if value is None:
            return "null"
        if isinstance(value, datetime):
            return "datetime"
        if isinstance(value, date):
            return "date"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            if value.is_integer():
                return "integer"
            return "float"
        if isinstance(value, str):
            value_str = str(value).strip()
            if not value_str:
                return "empty_string"
            if re.match(r'^\d+%$', value_str):
                return "percentage"
            if re.match(r'^\d+\.\d+%$', value_str):
                return "percentage"
            if re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', value_str):
                return "time"
            if re.match(r'^\d{1,2}/\d{1,2}/\d{2,4}$', value_str):
                return "date_string"
            if re.match(r'^\d{4}-\d{2}-\d{2}$', value_str):
                return "date_string"
            if re.match(r'^\d+$', value_str):
                return "integer_string"
            if re.match(r'^\d+\.\d+$', value_str):
                return "float_string"
            if re.match(r'^\$[\d,]+\.?\d*$', value_str):
                return "currency"
            return "text"
        return "unknown"
    
    result = [categorize_value(value) for value in values]
    logger.info(f"Data type analysis complete: {len(set(result))} unique types found")
    return result


@tool
def get_data_types_column(file_path: str, sheet_name: str, column_letter: str) -> List[str]:
    """Get the data types of all values in a specific column."""
    logger.info(f"Getting data types for column {column_letter} in sheet '{sheet_name}' from {file_path}")
    values = get_column_values(file_path, sheet_name, column_letter)
    return get_detailed_data_types(values)


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
def get_header_row(file_path: str, sheet_name: str, header_row: int = 1) -> List[str]:
    """Get the header row values from the Excel sheet."""
    logger.info(f"Getting header row {header_row} from sheet '{sheet_name}' in {file_path}")
    result = get_row_values(file_path, sheet_name, header_row)
    logger.info(f"Header row contains {len(result)} columns")
    return result


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
