from openpyxl import load_workbook
from typing import List, Any, Dict
from datetime import datetime, date
import re


def load_excel_file(file_path: str) -> Any:
    """Load an Excel file and return the workbook object."""
    return load_workbook(file_path)


def get_sheet_names(file_path: str) -> List[str]:
    """Get all sheet names from the Excel file."""
    workbook = load_workbook(file_path)
    return workbook.sheetnames


def get_row_values(file_path: str, sheet_name: str, row_number: int) -> List[Any]:
    """Get all values from a specific row in the Excel sheet."""
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    return [cell.value for cell in sheet[row_number]]


def get_column_values(file_path: str, sheet_name: str, column_letter: str) -> List[Any]:
    """Get all values from a specific column in the Excel sheet."""
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    return [cell.value for cell in sheet[column_letter]]


def get_cell_value(file_path: str, sheet_name: str, cell_reference: str) -> Any:
    """Get the value of a specific cell in the Excel sheet."""
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    return sheet[cell_reference].value


def get_detailed_data_types(values: List[Any]) -> List[str]:
    """Get detailed data types of values including dates, times, percentages, etc."""
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
    
    return [categorize_value(value) for value in values]


def get_data_types_row(file_path: str, sheet_name: str, row_number: int) -> List[str]:
    """Get the data types of all values in a specific row."""
    values = get_row_values(file_path, sheet_name, row_number)
    return get_detailed_data_types(values)


def get_data_types_column(file_path: str, sheet_name: str, column_letter: str) -> List[str]:
    """Get the data types of all values in a specific column."""
    values = get_column_values(file_path, sheet_name, column_letter)
    return get_detailed_data_types(values)


def get_sheet_dimensions(file_path: str, sheet_name: str) -> Dict[str, int]:
    """Get the number of rows and columns in the Excel sheet."""
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    return {"rows": sheet.max_row, "columns": sheet.max_column}


def get_header_row(file_path: str, sheet_name: str, header_row: int = 1) -> List[str]:
    """Get the header row values from the Excel sheet."""
    return get_row_values(file_path, sheet_name, header_row)


def find_cells_with_value(file_path: str, sheet_name: str, search_value: Any) -> List[str]:
    """Find all cell references that contain a specific value."""
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    cells = []
    for row in sheet.iter_rows():
        for cell in row:
            if cell.value == search_value:
                cells.append(cell.coordinate)
    return cells


def get_range_values(file_path: str, sheet_name: str, start_cell: str, end_cell: str) -> List[List[Any]]:
    """Get values from a range of cells in the Excel sheet."""
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    range_data = sheet[start_cell:end_cell]
    return [[cell.value for cell in row] for row in range_data]
