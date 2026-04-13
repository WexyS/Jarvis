"""Hermes-Agent Integration Bridge — main module.

Usage:
    from ultron.v2.core.hermes import HermesTool, SchemaTranslator, HermesExecutionLoop
    
    # Convert existing tool definitions
    hermes_tools = [SchemaTranslator.translate_tooldef(td) for td in local_tool_defs]
    
    # Or from Python functions
    hermes_tools = [SchemaTranslator.translate_function_to_schema(my_func)]
    
    # Run the TAO loop
    loop = HermesExecutionLoop(llm_router, hermes_tools)
    trajectory = await loop.run("Do something complex")
"""
from ultron.v2.core.hermes_tool import HermesTool
from ultron.v2.core.hermes_translator import SchemaTranslator
from ultron.v2.core.hermes_prompt import to_hermes_system_prompt
from ultron.v2.core.hermes_trajectory import ExecutionTrajectory
from ultron.v2.core.hermes_loop import HermesExecutionLoop

__all__ = [
    "HermesTool",
    "SchemaTranslator", 
    "to_hermes_system_prompt",
    "ExecutionTrajectory",
    "HermesExecutionLoop",
]
