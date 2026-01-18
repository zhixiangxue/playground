"""Mortgage Agent - Expert assistant for US mortgage and real estate"""
import os
from dotenv import load_dotenv
import chak

from tools.loan_form import generate_loan_form_url
from tools.rag_search import query_mortgage_rag
from tools.requirements import LoanRequirements
from tools.recommend_officer import recommend_loan_officer
from tools.dynamic_tool_manager import analyze_and_update_tools


load_dotenv()


# System prompt (English as per best practice)
SYSTEM_PROMPT = """You are a friendly and professional mortgage advisor specializing in US residential mortgages.

Your mission:
Help users navigate the mortgage process with clear, personalized guidance. Make complex topics easy to understand.

Key principles:
- Be conversational and warm, not robotic
- Explain financial terms in simple language
- Ask clarifying questions when needed
- Provide actionable next steps

Important notes:
- When using tools that display visual content (forms, recommendations), let the tool do its work without adding extra commentary
- Never generate markdown links or URLs - the system handles all UI interactions
- Stay focused on mortgage and real estate topics

Remember: You're here to guide and support, not just provide information."""


class MortgageAgent:
    """Mortgage advisory agent with tool calling capabilities"""
    
    def __init__(self):
        self.api_key = os.getenv("BAILIAN_API_KEY")
        if not self.api_key:
            raise ValueError("BAILIAN_API_KEY not found in environment")
        
        # Create loan requirements tracker
        self.requirements = LoanRequirements()
        
        # Track if loan form has been sent
        self.loan_form_sent = False
        
        # Create recommend_loan_officer function with access to requirements
        def _recommend_loan_officer() -> str:
            """Recommend suitable loan officers based on user requirements."""
            return recommend_loan_officer(self.requirements)
        
        # Store reference for dynamic tool management
        self._recommend_loan_officer = _recommend_loan_officer
        
        # Tool name to object mapping (for dynamic tool manager)
        self.tool_map = {
            "generate_loan_form_url": generate_loan_form_url,
            "query_mortgage_rag": query_mortgage_rag,
            "recommend_loan_officer": _recommend_loan_officer,
            "LoanRequirements": self.requirements
        }
        
        # Available tools list
        self.tools = [
            generate_loan_form_url,
            query_mortgage_rag,
            _recommend_loan_officer,
            self.requirements  # Pass object directly
        ]
        
        print(f"[Agent] Initialized with {len(self.tools)} tools: {[t.__name__ if hasattr(t, '__name__') else type(t).__name__ for t in self.tools]}")
        print(f"[Agent] loan_form_sent = {self.loan_form_sent}")
        
        # Create conversation
        self.conversation = chak.Conversation(
            "bailian/qwen-plus",
            api_key=self.api_key,
            system_message=SYSTEM_PROMPT,
            tools=self.tools
        )
    
    async def send_message(self, message: str, stream: bool = True):
        """
        Send user message and get response
        
        Args:
            message: User's message
            stream: Whether to stream response
            
        Yields or Returns:
            Response chunks if streaming, else returns full response
        """
        # ============================================================
        # Dynamic Tool Management (LLM-driven)
        # ============================================================
        try:
            await analyze_and_update_tools(
                conversation=self.conversation,
                user_message=message,
                current_tools=self.conversation.get_tools(),
                tool_map=self.tool_map,
                api_key=self.api_key
            )
        except Exception as e:
            print(f"[Agent] ⚠️ Dynamic tool analysis failed: {e}")
            # Continue even if tool analysis fails
        
        # ============================================================
        # Legacy: Remove loan form tool if already sent
        # (This can be removed once dynamic tool manager is stable)
        # ============================================================
        if self.loan_form_sent and generate_loan_form_url in self.tools:
            print(f"[Agent] loan_form_sent={self.loan_form_sent}, removing generate_loan_form_url")
            self.tools.remove(generate_loan_form_url)
            # Update ToolManager directly without recreating Conversation
            from chak.tools import wrap_tools
            from chak.tools.manager import ToolManager
            wrapped_tools = wrap_tools(self.tools)
            self.conversation._tool_manager = ToolManager(
                wrapped_tools, 
                executor=self.conversation._get_executor()
            )
            print("[Agent] Removed generate_loan_form_url tool from available tools")
        else:
            print(f"[Agent] loan_form_sent={self.loan_form_sent}, keeping all tools")
        
        # Send message
        response = await self.conversation.asend(message, stream=stream, event=stream)
                
        if stream:
            # Return async generator for streaming
            async def stream_with_tracking():
                from chak.message import MessageChunk
                
                async for event in response:
                    # Check if loan form tool was called (only for MessageChunk)
                    if isinstance(event, MessageChunk) and event.is_final and event.final_message:
                        # Check metadata for tool calls
                        if hasattr(event.final_message, 'metadata'):
                            metadata = event.final_message.metadata
                            if metadata and 'tool_calls' in str(metadata):
                                # Check if generate_loan_form_url was called
                                if 'generate_loan_form_url' in str(metadata):
                                    self.loan_form_sent = True
                    
                    yield event
            
            return stream_with_tracking()
        else:
            # Non-streaming - return response directly
            # Check if loan form tool was called
            if hasattr(response, 'metadata'):
                metadata = response.metadata
                if metadata and 'tool_calls' in str(metadata):
                    if 'generate_loan_form_url' in str(metadata):
                        self.loan_form_sent = True
            
            return response
    
    def reset(self):
        """Reset conversation and requirements"""
        self.conversation.clear()
        self.requirements = LoanRequirements()
        self.loan_form_sent = False
        
        # Recreate recommend_loan_officer with new requirements instance
        def _recommend_loan_officer() -> str:
            """Recommend suitable loan officers based on user requirements."""
            return recommend_loan_officer(self.requirements)
        
        self.tools = [
            generate_loan_form_url,
            query_mortgage_rag,
            _recommend_loan_officer,
            self.requirements
        ]
        self.conversation = chak.Conversation(
            "bailian/qwen-plus",
            api_key=self.api_key,
            system_message=SYSTEM_PROMPT,
            tools=self.tools
        )
