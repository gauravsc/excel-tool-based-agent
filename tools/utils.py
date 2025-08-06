from openpyxl import load_workbook
from typing import List, Any, Dict
from datetime import datetime, date
import re
from langchain.tools import tool
from core.logger import setup_logger

logger = setup_logger(__name__)

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