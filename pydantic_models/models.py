from pydantic import BaseModel, Field
from typing import Optional


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


class GroundTruthList(BaseModel):
    """
    Model for a list of ground truth entries.
    """
    entries: list[GroundTruth] = Field(..., description="List of ground truth entries")
