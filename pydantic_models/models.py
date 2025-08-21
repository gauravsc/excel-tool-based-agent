from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ExpectedOutput(BaseModel):
    """
    Model representing the expected output of our models - a value found in a specific location within a spreadsheet sheet.
    """
    sheet_name: str = Field(..., description="Name of the sheet containing the value")
    location_in_sheet: str = Field(..., description="Cell reference where the value is located (e.g., 'A1', 'B2')")
    value: int = Field(..., description="The numeric value found in the cell")
    CoA_label: str = Field(..., description="Chart of Accounts label (e.g., '1100', '2100')")
    timestamp_of_value: str = Field(..., description="Date or period when the value was recorded (e.g., 'Feb 2023', 'Jan 2023')")
    unit: str = Field(..., description="Descriptive text about what the unit represents (e.g., 'e.g. restaurant name, building location, etc.')")


class GroundTruth(BaseModel):
    """
    Model representing the ground truth data to evaluate against - a financial entry with value, label, timestamp, and unit information.
    """
    value: int = Field(..., description="The numeric value of the financial entry")
    CoA_label: str = Field(..., description="Chart of Accounts label (e.g., 'Revenue', 'Expense')")
    timestamp_of_value: str = Field(..., description="Date or period when the value was recorded (e.g., 'Feb 2023', 'Jan 2023')")
    unit: str = Field(..., description="Descriptive text about what the unit represents (e.g., 'e.g. restaurant location, business address etc.')")


# Example usage models for lists
class ExpectedOutputList(BaseModel):
    """
    Model for a list of expected output entries.
    """
    entries: list[ExpectedOutput] = Field(..., description="List of expected output entries")
    class Config:
        """Configuration for ExpectedOutputList model."""
        name = "ExpectedOutputList" 


class GroundTruthList(BaseModel):
    """
    Model for a list of ground truth entries.
    """
    entries: list[GroundTruth] = Field(..., description="List of ground truth entries")


# Sheet encoding models
class ColumnInfo(BaseModel):
    """
    Model representing information about a single column in a spreadsheet table.
    """
    column_letter: str = Field(..., description="Column letter (e.g., 'A', 'B', 'F')")
    column_name: str = Field(..., description="Human-readable name of the column")
    column_description: str = Field(..., description="Detailed description of what the column contains")
    data_type: str = Field(..., description="Data type of the column (e.g., 'text', 'numeric', 'date')")
    sample_values: List[Any] = Field(..., description="Sample values from the column")
    unique_values_count: int = Field(..., description="Number of unique values in the column")
    has_null_values: bool = Field(..., description="Whether the column contains null/empty values")


class TableBoundaries(BaseModel):
    """
    Model representing the boundaries of a table within a sheet.
    """
    start_row: int = Field(..., description="Starting row number of the table")
    end_row: int = Field(..., description="Ending row number of the table")
    start_column: str = Field(..., description="Starting column letter of the table")
    end_column: str = Field(..., description="Ending column letter of the table")
    range: str = Field(..., description="Excel range notation (e.g., 'D8:P40')")


class RowHeaders(BaseModel):
    """
    Model representing row header information for a table.
    """
    has_row_headers: bool = Field(..., description="Whether the table has row headers")
    row_header_column: str = Field(..., description="Column letter containing row headers (if applicable)")
    row_header_description: str = Field(..., description="Description of row headers")


class DataQuality(BaseModel):
    """
    Model representing data quality information for a table.
    """
    completeness: str = Field(..., description="Description of data completeness")
    consistency: str = Field(..., description="Description of data consistency")
    anomalies: List[str] = Field(..., description="List of data anomalies or issues found")


class TableInfo(BaseModel):
    """
    Model representing information about a single table within a sheet.
    """
    table_name: str = Field(..., description="Name of the table")
    table_description: str = Field(..., description="Detailed description of what the table contains")
    boundaries: TableBoundaries = Field(..., description="Table boundaries within the sheet")
    columns: List[ColumnInfo] = Field(..., description="List of columns in the table")
    row_headers: RowHeaders = Field(..., description="Row header information")
    data_quality: DataQuality = Field(..., description="Data quality assessment")


class SheetDimensions(BaseModel):
    """
    Model representing the dimensions of a sheet.
    """
    rows: int = Field(..., description="Number of rows in the sheet")
    columns: int = Field(..., description="Number of columns in the sheet")
    range: str = Field(..., description="Full range of the sheet (e.g., 'A1:BB158')")


class SingleSheetEncoding(BaseModel):
    """
    Model representing a complete encoding of a single spreadsheet sheet.
    """
    name: str = Field(..., description="Name of the sheet")
    sheet_name: str = Field(..., description="Name of the sheet")
    sheet_description: str = Field(..., description="Detailed description of what the sheet contains")
    dimensions: SheetDimensions = Field(..., description="Sheet dimensions")
    tables: List[TableInfo] = Field(..., description="List of tables found in the sheet")
    class Config:
        """Configuration for SingleSheetEncoding model."""
        name = "SingleSheetEncoding" 
