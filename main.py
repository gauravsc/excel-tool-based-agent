#!/usr/bin/env python3
"""
Excel Tool-Based Agent - Main Script
Handles multi-step sequential tasks for Excel file processing
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import our tools
from tools.tools import (
    load_excel_file, get_sheet_names, get_row_values, get_column_values,
    get_cell_value, get_detailed_data_types, get_data_types_row, get_data_types_column,
    get_sheet_dimensions, get_header_row, find_cells_with_value, get_range_values
)
from core.utils import remove_hidden_columns


class ExcelAgent:
    """Agent for processing Excel files with multi-step tasks."""
    
    def __init__(self, data_folder: str = "data"):
        self.data_folder = Path(data_folder)
        self.current_file = None
        self.current_sheet = None
        
    def load_task_file(self, task_file: str) -> Dict[str, Any]:
        """Load task description from a JSON file in the data folder."""
        task_path = self.data_folder / task_file
        if not task_path.exists():
            raise FileNotFoundError(f"Task file not found: {task_path}")
        
        with open(task_path, 'r') as f:
            return json.load(f)
    
    def load_text_file(self, text_file: str) -> str:
        """Load text content from a file in the data folder."""
        text_path = self.data_folder / text_file
        if not text_path.exists():
            raise FileNotFoundError(f"Text file not found: {text_path}")
        
        with open(text_path, 'r') as f:
            return f.read()
    
    def execute_task(self, task_description: str, content_file: Optional[str] = None) -> Dict[str, Any]:
        """Execute a multi-step task based on description and optional content file."""
        results = {
            "task": task_description,
            "steps": [],
            "final_output": None
        }
        
        # Load content if provided
        content = None
        if content_file:
            content = self.load_text_file(content_file)
            results["content_file"] = content_file
            results["content"] = content
        
        # Parse task and execute steps
        steps = self._parse_task(task_description, content)
        
        for i, step in enumerate(steps, 1):
            step_result = self._execute_step(step, results)
            results["steps"].append({
                "step": i,
                "action": step["action"],
                "result": step_result
            })
            print(f"Step {i}: {step['action']} - Completed")
        
        results["final_output"] = self._generate_final_output(results["steps"])
        return results
    
    def _parse_task(self, task_description: str, content: Optional[str] = None) -> List[Dict[str, Any]]:
        """Parse task description into executable steps."""
        steps = []
        
        # Simple task parser - can be enhanced with NLP
        task_lower = task_description.lower()
        
        if "analyze" in task_lower and "excel" in task_lower:
            steps.extend([
                {"action": "list_sheets", "description": "Get all sheet names"},
                {"action": "get_dimensions", "description": "Get sheet dimensions"},
                {"action": "get_headers", "description": "Get header information"}
            ])
        
        if "data types" in task_lower or "datatypes" in task_lower:
            steps.extend([
                {"action": "analyze_data_types", "description": "Analyze data types in columns"}
            ])
        
        if "hidden" in task_lower and "columns" in task_lower:
            steps.extend([
                {"action": "remove_hidden_columns", "description": "Remove hidden columns"}
            ])
        
        if "find" in task_lower and "value" in task_lower:
            steps.extend([
                {"action": "search_values", "description": "Search for specific values"}
            ])
        
        # Default steps if no specific pattern matched
        if not steps:
            steps = [
                {"action": "list_sheets", "description": "Get all sheet names"},
                {"action": "get_dimensions", "description": "Get sheet dimensions"}
            ]
        
        return steps
    
    def _execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute a single step."""
        action = step["action"]
        
        if action == "list_sheets":
            if not self.current_file:
                raise ValueError("No Excel file loaded. Please specify a file path.")
            return get_sheet_names(self.current_file)
        
        elif action == "get_dimensions":
            if not self.current_file or not self.current_sheet:
                raise ValueError("No Excel file or sheet specified.")
            return get_sheet_dimensions(self.current_file, self.current_sheet)
        
        elif action == "get_headers":
            if not self.current_file or not self.current_sheet:
                raise ValueError("No Excel file or sheet specified.")
            return get_header_row(self.current_file, self.current_sheet)
        
        elif action == "analyze_data_types":
            if not self.current_file or not self.current_sheet:
                raise ValueError("No Excel file or sheet specified.")
            # Analyze first few columns
            dimensions = get_sheet_dimensions(self.current_file, self.current_sheet)
            max_cols = min(5, dimensions["columns"])  # Analyze first 5 columns
            
            data_types = {}
            for i in range(1, max_cols + 1):
                col_letter = chr(64 + i)  # A, B, C, etc.
                types = get_data_types_column(self.current_file, self.current_sheet, col_letter)
                data_types[col_letter] = types[:10]  # First 10 values
            
            return data_types
        
        elif action == "remove_hidden_columns":
            if not self.current_file or not self.current_sheet:
                raise ValueError("No Excel file or sheet specified.")
            return remove_hidden_columns(self.current_file, self.current_sheet)
        
        elif action == "search_values":
            # This would need a specific value to search for
            return "Search functionality requires specific value to search for"
        
        else:
            return f"Unknown action: {action}"
    
    def _generate_final_output(self, steps: List[Dict[str, Any]]) -> str:
        """Generate a readable final output from all steps."""
        output_lines = ["=== EXCEL ANALYSIS RESULTS ===\n"]
        
        for step in steps:
            output_lines.append(f"Step {step['step']}: {step['action']}")
            output_lines.append(f"Result: {step['result']}")
            output_lines.append("-" * 40)
        
        return "\n".join(output_lines)
    
    def set_current_file(self, file_path: str):
        """Set the current Excel file to work with."""
        full_path = self.data_folder / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"Excel file not found: {full_path}")
        self.current_file = str(full_path)
    
    def set_current_sheet(self, sheet_name: str):
        """Set the current sheet to work with."""
        if not self.current_file:
            raise ValueError("No Excel file loaded. Please set a file first.")
        
        sheets = get_sheet_names(self.current_file)
        if sheet_name not in sheets:
            raise ValueError(f"Sheet '{sheet_name}' not found. Available sheets: {sheets}")
        
        self.current_sheet = sheet_name


def main():
    """Main function to run the Excel agent."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <task_description> [content_file] [excel_file] [sheet_name]")
        print("Example: python main.py 'analyze excel file data types' content.txt data.xlsx 'Sheet1'")
        sys.exit(1)
    
    task_description = sys.argv[1]
    content_file = sys.argv[2] if len(sys.argv) > 2 else None
    excel_file = sys.argv[3] if len(sys.argv) > 3 else None
    sheet_name = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Create agent
    agent = ExcelAgent()
    
    try:
        # Set up file and sheet if provided
        if excel_file:
            agent.set_current_file(excel_file)
            print(f"Loaded Excel file: {excel_file}")
        
        if sheet_name:
            agent.set_current_sheet(sheet_name)
            print(f"Set active sheet: {sheet_name}")
        
        # Execute task
        print(f"Executing task: {task_description}")
        results = agent.execute_task(task_description, content_file)
        
        # Print final output
        print("\n" + results["final_output"])
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
