"""
claude_tools.py
===============
Defines Claude API tool schemas and maps tool calls to pipeline_runner.py.
Used by webhook_server.py to process Claude's tool_use responses.
"""

import json
from automation.pipeline_runner import (
    run_full_pipeline,
    run_step,
    run_sharing,
    get_status,
    get_current_runtime,
    set_runtime,
    clear_data,
)

# ============================================================
# Tool schemas — sent to Claude API as "tools" parameter
# ============================================================
TOOLS = [
    {
        "name": "run_pipeline",
        "description": (
            "Run the complete Utilitics data pipeline end-to-end "
            "(generate → bronze → silver → gold → validate). "
            "Use when the user says 'run pipeline', 'start pipeline', 'run everything', etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "runtime": {
                    "type": "string",
                    "enum": ["local", "databricks"],
                    "description": "Override runtime for this run only. Omit to use current setting.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "run_step",
        "description": (
            "Run a single pipeline step by name. "
            "Steps: generate, bronze, silver, gold, validate, sharing."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "step": {
                    "type": "string",
                    "enum": ["generate", "bronze", "silver", "gold", "validate", "sharing"],
                    "description": "The pipeline step to run.",
                }
            },
            "required": ["step"],
        },
    },
    {
        "name": "run_sharing",
        "description": (
            "Run the Delta Sharing simulation. "
            "Use when the user says 'run sharing', 'simulate sharing', 'delta sharing', etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_status",
        "description": (
            "Get the status of the last pipeline run. "
            "Use when the user says 'status', 'last run', 'what happened', 'pipeline status', etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_runtime",
        "description": (
            "Get the current runtime setting (local or databricks). "
            "Use when the user asks 'what runtime', 'which mode', 'local or databricks', etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "clear_data",
        "description": (
            "Clear pipeline data from the lake folder. "
            "Use 'clear data' or 'clear our data' to wipe only Utilitics data (keeps vendor folder). "
            "Use 'clear all' or 'clear all data' to wipe everything including vendor forecast output."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "include_vendor": {
                    "type": "boolean",
                    "description": "If true, also deletes vendor_forecast_output folder. Default false.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "set_runtime",
        "description": (
            "Switch the pipeline runtime between local and databricks. "
            "Use when the user says 'switch to local', 'use databricks', 'set runtime', etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "runtime": {
                    "type": "string",
                    "enum": ["local", "databricks"],
                    "description": "The runtime to switch to.",
                }
            },
            "required": ["runtime"],
        },
    },
]


# ============================================================
# Tool dispatcher — executes the tool Claude selected
# ============================================================
def execute_tool(tool_name: str, tool_input: dict) -> dict:
    """
    Execute the tool named by Claude, return a result dict.
    All functions return dicts with at least: success, summary.
    """
    if tool_name == "run_pipeline":
        runtime = tool_input.get("runtime")   # may be None
        return run_full_pipeline(runtime_override=runtime)

    elif tool_name == "run_step":
        return run_step(tool_input["step"])

    elif tool_name == "run_sharing":
        return run_sharing()

    elif tool_name == "get_status":
        return get_status()

    elif tool_name == "get_runtime":
        runtime = get_current_runtime()
        return {
            "action":  "get_runtime",
            "success": True,
            "summary": f"Current runtime: {runtime}",
            "runtime": runtime,
        }

    elif tool_name == "clear_data":
        include_vendor = tool_input.get("include_vendor", False)
        return clear_data(include_vendor=include_vendor)

    elif tool_name == "set_runtime":
        return set_runtime(tool_input["runtime"])

    else:
        return {
            "action":  tool_name,
            "success": False,
            "summary": f"Unknown tool: {tool_name}",
        }


# ============================================================
# Format tool result as a string for the tool_result message
# ============================================================
def format_tool_result(result: dict) -> str:
    """Convert a result dict to a compact JSON string for Claude."""
    return json.dumps(result, indent=2)
