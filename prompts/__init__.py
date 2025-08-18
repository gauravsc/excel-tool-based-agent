"""
Prompts package containing system prompts for different agents.

This package contains functions that return system prompts for various agents
in the excel-tool-based-agent system.
"""

from .excel_agent import get_task_prompt as get_excel_agent_task_prompt
from .spreadsheet_encoder_agent import get_task_prompt as get_spreadsheet_encoder_agent_task_prompt

__all__ = [
    'get_excel_agent_task_prompt',
    'get_spreadsheet_encoder_agent_task_prompt'
] 