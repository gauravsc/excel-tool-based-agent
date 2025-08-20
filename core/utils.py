import openpyxl
from openpyxl.utils import get_column_letter, column_index_from_string
from openpyxl.styles import Border
from typing import List, Optional, Dict
from core.logger import setup_logger
from openpyxl import load_workbook

logger = setup_logger(__name__)

def remove_hidden_columns(file_path: str, sheet_name: str, output_path: Optional[str] = None) -> List[str]:
    """Remove hidden and grouped columns from an Excel sheet and return list of removed columns."""
    # Load workbook
    wb = openpyxl.load_workbook(file_path)
    ws = wb[sheet_name]
    
    # Get all column letters
    max_col = ws.max_column
    cols = [get_column_letter(i) for i in range(1, max_col + 1)]
    
    # Find hidden columns
    hidden_cols = []
    last_hidden = 0
    for i, col in enumerate(cols):
        # Column is hidden
        if ws.column_dimensions[col].hidden:
            hidden_cols.append(col)
            # Last column in the hidden group
            last_hidden = ws.column_dimensions[col].max
        # Appending column if more columns in the group
        elif i + 1 <= last_hidden:
            hidden_cols.append(col)
    
    # Get visible columns
    visible_cols = [col for col in cols if col not in hidden_cols]
    
    # Clear hidden column data
    cols_to_delete = [column_index_from_string(col) for col in hidden_cols]
    for col_idx in sorted(set(cols_to_delete), reverse=True):
        for row in range(2, ws.max_row + 1):  # start from 2 to skip header
            cell = ws[f"{get_column_letter(col_idx)}{row}"]
            cell.value = None
            cell.border = Border()
    
    # Reset column dimensions for hidden columns
    for col, dim in ws.column_dimensions.items():
        if ws.column_dimensions[col].hidden:
            ws.column_dimensions[col].hidden = False
            ws.column_dimensions[col].outlineLevel = False
            ws.column_dimensions[col].max = column_index_from_string(col)
    
    # Save to output path or original file
    if output_path:
        wb.save(output_path)
    else:
        wb.save(file_path)
    
    return hidden_cols


def remove_hidden_columns_all_sheets(file_path: str, output_path: Optional[str] = None) -> Dict[str, List[str]]:
    """Remove hidden and grouped columns from all sheets in an Excel workbook and return dict mapping sheet names to removed columns."""
    # Load workbook to get sheet names
    wb = openpyxl.load_workbook(file_path)
    sheet_names = wb.sheetnames
    wb.close()
    
    # Dictionary to store results for each sheet
    results = {}
    
    # Process each sheet by calling remove_hidden_columns
    for sheet_name in sheet_names:
        # Call remove_hidden_columns for this specific sheet
        hidden_cols = remove_hidden_columns(file_path, sheet_name)
        results[sheet_name] = hidden_cols
    
    return results


def get_sheet_names(file_path: str) -> List[str]:
    """Get all sheet names from the Excel file."""
    logger.info("Getting sheet names from %s", file_path)
    workbook = load_workbook(file_path)
    result = workbook.sheetnames
    logger.info("Found %d sheets: %s", len(result), result)
    return result
