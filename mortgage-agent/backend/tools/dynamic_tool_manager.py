"""
Dynamic Tool Manager - LLM-driven tool management

This module allows LLM to dynamically add/remove tools based on conversation context.
Can be easily enabled/disabled by setting ENABLE_DYNAMIC_TOOLS flag.
"""
import json
from typing import List, Optional
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


# ============================================================================
# Configuration
# ============================================================================
ENABLE_DYNAMIC_TOOLS = True  # Set to False to disable dynamic tool management


# ============================================================================
# Tool Analysis Schema
# ============================================================================
class ToolDecision(BaseModel):
    """LLM's decision on tool management"""
    should_add: List[str] = []      # Tool names to add (e.g., ["recommend_loan_officer"])
    should_remove: List[str] = []   # Tool names to remove
    reason: str                     # Why this decision was made


# ============================================================================
# Tool Analysis Prompt
# ============================================================================
TOOL_ANALYSIS_PROMPT = """Analyze the conversation and decide which tools should be available.

Current conversation context:
- User has been chatting with a mortgage advisor
- Available tools can be dynamically added or removed based on needs

Available tools:
1. generate_loan_form_url - Send loan application form (can only be used once)
2. query_mortgage_rag - Query mortgage knowledge base
3. recommend_loan_officer - Recommend loan officers (requires user info to be complete)
4. requirements - Update user's loan requirements

Current tool status:
{current_tools}

User's latest message: "{user_message}"

Based on the conversation flow, decide:
- Should we ADD any tools? (e.g., if user info is complete, add recommend_loan_officer)
- Should we REMOVE any tools? (e.g., if loan form already sent, remove generate_loan_form_url)

Rules:
- Only add recommend_loan_officer if user explicitly requests recommendations OR if requirements are complete and user is ready for next step
- Remove generate_loan_form_url after it's been called once
- Keep query_mortgage_rag and requirements available most of the time
- If no changes needed, return empty lists

Return your decision as JSON with: should_add, should_remove, and reason.
"""


# ============================================================================
# Dynamic Tool Manager
# ============================================================================
async def analyze_and_update_tools(
    conversation,
    user_message: str,
    current_tools: List,
    tool_map: dict,
    api_key: str
) -> Optional[ToolDecision]:
    """
    Analyze conversation and let LLM decide tool changes.
    
    This is the main function that can be called from agent.
    If ENABLE_DYNAMIC_TOOLS is False, returns None immediately.
    
    Args:
        conversation: Main conversation instance
        user_message: User's latest message
        current_tools: Current tool list
        tool_map: Mapping from tool names to tool objects
        api_key: API key for creating analysis conversation
        
    Returns:
        ToolDecision if changes were made, None otherwise
    """
    if not ENABLE_DYNAMIC_TOOLS:
        return None
    
    # Get current tool names
    current_tool_names = [
        t.__name__ if hasattr(t, '__name__') else type(t).__name__ 
        for t in current_tools
    ]
    
    # Build analysis prompt
    prompt = TOOL_ANALYSIS_PROMPT.format(
        current_tools=", ".join(current_tool_names),
        user_message=user_message
    )
    
    # Create temporary conversation for analysis
    # Use the main conversation's messages as context
    import chak
    analysis_conv = chak.Conversation(
        "bailian/qwen-plus",
        api_key=api_key,
        system_message="You are a tool management assistant. Analyze conversation and decide tool availability."
    )
    
    # Add conversation history to analysis context (last 5 messages for efficiency)
    recent_messages = conversation.messages[-5:] if len(conversation.messages) > 5 else conversation.messages
    for msg in recent_messages:
        # Convert to dict format for add_messages
        if hasattr(msg, 'role') and hasattr(msg, 'content'):
            analysis_conv.add_messages([{
                "role": msg.role,
                "content": msg.content if isinstance(msg.content, str) else str(msg.content)
            }])
    
    try:
        # Let LLM analyze and return structured decision
        decision = await analysis_conv.asend(
            prompt,
            returns=ToolDecision
        )
        
        if not decision:
            return None
        
        # Apply tool changes
        applied = _apply_tool_changes(conversation, decision, tool_map)
        
        if applied:
            # Build rich panel for tool changes
            content = Text()
            
            if decision.should_add:
                content.append("➕ Added: ", style="bold green")
                content.append(', '.join(decision.should_add), style="green")
                content.append("\n")
            
            if decision.should_remove:
                content.append("➖ Removed: ", style="bold red")
                content.append(', '.join(decision.should_remove), style="red")
                content.append("\n")
            
            content.append("\n💡 Reason: ", style="bold cyan")
            content.append(decision.reason, style="cyan")
            
            panel = Panel(
                content,
                title="[bold magenta]🔧 Dynamic Tool Changes[/bold magenta]",
                border_style="magenta",
                padding=(1, 2)
            )
            console.print(panel)
            
            return decision
        
        return None
    
    except Exception as e:
        print(f"[DynamicTools] ⚠️ Tool analysis failed: {e}")
        return None


def _apply_tool_changes(conversation, decision: ToolDecision, tool_map: dict) -> bool:
    """
    Apply tool changes to conversation.
    
    Returns:
        True if any changes were made, False otherwise
    """
    changes_made = False
    
    # Add tools
    if decision.should_add:
        tools_to_add = []
        for tool_name in decision.should_add:
            if tool_name in tool_map:
                tool = tool_map[tool_name]
                # Check if tool is not already added
                current_tools = conversation.get_tools()
                if tool not in current_tools:
                    tools_to_add.append(tool)
        
        if tools_to_add:
            conversation.add_tools(tools_to_add)
            changes_made = True
    
    # Remove tools
    if decision.should_remove:
        tools_to_remove = []
        for tool_name in decision.should_remove:
            if tool_name in tool_map:
                tool = tool_map[tool_name]
                # Check if tool exists in current tools
                current_tools = conversation.get_tools()
                if tool in current_tools:
                    tools_to_remove.append(tool)
        
        if tools_to_remove:
            conversation.remove_tools(tools_to_remove)
            changes_made = True
    
    return changes_made
