import json
from pydantic_models.models import SheetSelectionResponse

def get_task_prompt(sheet_names: list, coa_items: list, excel_file_path: str = None) -> str:
    """Generate the task prompt for the sheet selector agent."""
    
    # Generate the schema from the Pydantic model
    schema = SheetSelectionResponse.model_json_schema()
    schema_json = json.dumps(schema, indent=2)
    
    coa_items_text = "\n".join([f"- {item}" for item in coa_items])
    
    prompt = f"""
You are a financial data analyst tasked with identifying which Excel sheets are likely to contain values corresponding to specific Chart of Accounts (CoA) items.

**EXCEL FILE:** {excel_file_path or "Not specified"}

**TASK:**
Analyze the provided list of sheet names from the Excel file and determine which sheets are likely to contain financial data that corresponds to the CoA items listed below.

**CHART OF ACCOUNTS ITEMS TO MATCH:**
```
{coa_items_text}
```

**SHEET NAMES TO EVALUATE:**
```
{chr(10).join([f"- {sheet}" for sheet in sheet_names])}
```

**INSTRUCTIONS:**

1. **For each sheet name, analyze whether it's likely to contain financial data that would map to any of the CoA items**

2. **Consider the following factors:**
   - Sheet names that suggest financial statements (P&L, Balance Sheet, Cash Flow, etc.)
   - Sheets with names indicating revenue, expenses, assets, liabilities, or equity
   - Sheets that might contain operational data that feeds into financial statements
   - Sheets with names suggesting budgets, forecasts, or actuals
   - Sheets that might contain supporting schedules or detailed breakdowns

3. **TOOL USAGE STRATEGY:**
   - If the sheet name clearly indicates financial content (e.g., "P&L", "Balance Sheet"), you can make a decision without using tools
   - If the sheet name is ambiguous or unclear (e.g., "Sheet1", "Data", "Summary"), use tools to examine the sheet content
   - Use tools efficiently - examine only a small sample of data to understand the sheet's purpose

4. **Return a JSON response that follows the SheetSelectionResponse schema structure with:**
   - `selected_sheets`: List of SheetSelection objects
   - Each SheetSelection contains:
     - `sheet_name`: Name of the sheet
     - `include`: Boolean indicating whether to include the sheet
     - `reasoning`: Brief explanation of why this sheet should/shouldn't be included

**EFFICIENCY GUIDELINES:**
- Make decisions based on sheet names when possible
- Only use tools when the sheet name is ambiguous or unclear
- Use sampling tools rather than full content retrieval
- Keep tool calls to a minimum while ensuring accurate decisions
- **IMPORTANT: Be selective and choose fewer sheets rather than more to avoid processing too much data**
- Prioritize the most relevant sheets that are likely to contain the specific CoA items
- If multiple sheets seem similar, choose the one that appears most comprehensive or relevant

Please analyze each sheet name carefully and provide your reasoning for inclusion or exclusion. Use tools only when necessary to make an informed decision.

## Required Output Schema (SheetSelectionResponse)

```json
{schema_json}
```
"""
    
    return prompt
