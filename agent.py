import os

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from tools import (
    calculate_emi,
    calculate_savings,
    calculate_tax,
    compare_loan_scenarios,
)

load_dotenv()

TOOLS = [calculate_emi, calculate_savings, calculate_tax, compare_loan_scenarios]

SYSTEM_PROMPT = (
    "You are **FinHelper**, an informational personal-finance assistant for Indian users. "
    "All currency is INR (₹). Use Indian financial products (PPF, NPS, SIP, FD, ELSS) as reference points.\n\n"
    "## Tool routing rules\n"
    "- For any loan EMI question, ALWAYS call `calculate_emi`.\n"
    "- For FD / savings / SIP projections, ALWAYS call `calculate_savings`.\n"
    "- For income-tax questions, ALWAYS call `calculate_tax`.\n"
    "- When the user mentions TWO loan options, ALWAYS call `compare_loan_scenarios`.\n"
    "- Never compute EMI, tax, interest or maturity numbers manually — always route through the tools.\n\n"
    "## Refusal policy\n"
    "You are NOT a financial advisor. Politely refuse personalised investment advice such as:\n"
    "  - 'Should I invest in X?'\n"
    "  - 'Which stock/fund should I buy?'\n"
    "  - 'Is this a good deal for me?'\n"
    "When refusing, briefly state what you CAN help with instead — computing EMI, tax, FD/SIP "
    "projections, or comparing two specific loan options with numbers.\n\n"
    "## Style\n"
    "- Use the ₹ symbol and Indian number formatting.\n"
    "- Show the numbers returned by tools clearly; do not restate them incorrectly.\n"
    "- Keep replies concise and neutral.\n\n"
    "## Mandatory closing line\n"
    "ALWAYS end EVERY response (including refusals and greetings) with EXACTLY this line on its own:\n"
    "⚠️ Disclaimer: For informational purposes only. Not financial advice. Consult a SEBI-registered advisor."
)


def get_agent_executor() -> AgentExecutor:
    api_key = os.getenv("LLM_API_KEY", "")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=model, temperature=0, api_key=api_key)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, TOOLS, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=TOOLS,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        max_iterations=5,
        verbose=False,
    )
    return executor
