
"""
LangChain Agent Configuration for FinHelper

This module sets up the conversational AI agent that powers the FinHelper chat interface.
It configures:
- An OpenAI LLM as the reasoning engine
- A set of financial calculation tools
- A system prompt with routing rules and safety guardrails
- An agent executor that orchestrates tool calls

The agent uses OpenAI's function/tool calling API to decide when and which
financial tools to invoke based on user queries.
"""

import os

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

# Import the financial calculation tools defined in tools.py
# Each tool is a @tool-decorated function that the agent can invoke
from tools import (
    calculate_emi,
    calculate_savings,
    calculate_tax,
    compare_loan_scenarios,
)

# Load environment variables from .env file
# Expected variables: LLM_API_KEY, LLM_MODEL (optional)
load_dotenv()

# =============================================================================
# TOOL REGISTRY
# =============================================================================
# List of all tools available to the agent
# The agent will use these based on the routing rules in the system prompt
TOOLS = [calculate_emi, calculate_savings, calculate_tax, compare_loan_scenarios]

# =============================================================================
# SYSTEM PROMPT
# =============================================================================
# Defines the agent's personality, capabilities, constraints, and behavior rules
# This is critical for reliable tool routing and safe responses
SYSTEM_PROMPT = (
    # --- Identity & Context ---
    "You are **FinHelper**, an informational personal-finance assistant for Indian users. "
    "All currency is INR (₹). Use Indian financial products (PPF, NPS, SIP, FD, ELSS) as reference points.\n\n"
    
    # --- Tool Routing Rules ---
    # Explicit rules to ensure the agent uses tools instead of manual calculation
    # This prevents hallucinated numbers and ensures accurate results
    "## Tool routing rules\n"
    "- For any loan EMI question, ALWAYS call `calculate_emi`.\n"
    "- For FD / savings / SIP projections, ALWAYS call `calculate_savings`.\n"
    "- For income-tax questions, ALWAYS call `calculate_tax`.\n"
    "- When the user mentions TWO loan options, ALWAYS call `compare_loan_scenarios`.\n"
    "- Never compute EMI, tax, interest or maturity numbers manually — always route through the tools.\n\n"
    
    # --- Safety Guardrails ---
    # Prevents the agent from giving personalized financial advice
    # which could have legal/regulatory implications
    "## Refusal policy\n"
    "You are NOT a financial advisor. Politely refuse personalised investment advice such as:\n"
    "  - 'Should I invest in X?'\n"
    "  - 'Which stock/fund should I buy?'\n"
    "  - 'Is this a good deal for me?'\n"
    "When refusing, briefly state what you CAN help with instead — computing EMI, tax, FD/SIP "
    "projections, or comparing two specific loan options with numbers.\n\n"
    
    # --- Output Formatting ---
    "## Style\n"
    "- Use the ₹ symbol and Indian number formatting.\n"
    "- Show the numbers returned by tools clearly; do not restate them incorrectly.\n"
    "- Keep replies concise and neutral.\n\n"
    
    # --- Mandatory Disclaimer ---
    # Legal protection - must appear in EVERY response without exception
    "## Mandatory closing line\n"
    "ALWAYS end EVERY response (including refusals and greetings) with EXACTLY this line on its own:\n"
    "⚠️ Disclaimer: For informational purposes only. Not financial advice. Consult a SEBI-registered advisor."
)


# =============================================================================
# AGENT EXECUTOR FACTORY
# =============================================================================
def get_agent_executor() -> AgentExecutor:
    """
    Create and configure the LangChain agent executor.
    
    The executor orchestrates the interaction between:
    1. The LLM (for reasoning and decision-making)
    2. The tools (for accurate financial calculations)
    3. The prompt template (for context and instructions)
    
    Returns:
        AgentExecutor: Configured agent ready to process user queries
    """
    # --- LLM Configuration ---
    # Read configuration from environment variables for flexibility
    api_key = os.getenv("LLM_API_KEY", "")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")  # Default to cost-effective model
    
    # Initialize OpenAI chat model
    # temperature=0: Deterministic responses, crucial for accurate financial info
    llm = ChatOpenAI(model=model, temperature=0, api_key=api_key)
    
    # --- Prompt Template ---
    # Defines the message structure sent to the LLM on each invocation:
    # 1. System message: Identity, rules, constraints
    # 2. Chat history: Previous conversation for context (optional)
    # 3. Human message: Current user query
    # 4. Agent scratchpad: Intermediate steps/tool calls (managed by agent)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # --- Agent Creation ---
    # create_tool_calling_agent uses OpenAI's native function calling API
    # This is more reliable than older ReAct-style agents for tool selection
    agent = create_tool_calling_agent(llm, TOOLS, prompt)
    
    # --- Executor Configuration ---
    executor = AgentExecutor(
        agent=agent,
        tools=TOOLS,
        
        # Include intermediate steps in response for tracking which tools were used
        # Used by the UI to display tool badges
        return_intermediate_steps=True,
        
        # Gracefully handle cases where LLM output can't be parsed as tool calls
        # Instead of crashing, the executor will try to recover
        handle_parsing_errors=True,
        
        # Limit iterations to prevent infinite loops
        # 5 iterations allows for: think → tool1 → think → tool2 → final answer
        max_iterations=5,
        
        # Disable verbose logging in production
        # Set to True for debugging tool calling behavior
        verbose=False,
    )
    
    return executor
