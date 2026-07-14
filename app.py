import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

from agent import get_agent_executor

load_dotenv()

st.set_page_config(page_title="FinHelper", page_icon="💰", layout="wide")

TOOL_BADGES = {
    "calculate_emi": "📐 EMI Calculator",
    "calculate_savings": "💰 Savings Calculator",
    "calculate_tax": "📋 Tax Estimator",
    "compare_loan_scenarios": "⚖️ Loan Comparator",
}

EXAMPLE_QUERIES = [
    "What is the EMI on a ₹25L home loan at 8.5% for 20 years?",
    "How much will ₹1L in FD at 7% for 5 years grow to?",
    "Calculate tax on ₹15L annual income under new regime",
    "Compare ₹20L @ 9% for 15 yrs vs ₹20L @ 8.5% for 20 yrs",
    "Explain the difference between PPF and ELSS",
]

WELCOME = (
    "👋 Hi! I'm **FinHelper** — your informational personal-finance assistant.\n\n"
    "I can help you with:\n"
    "- 📐 **EMI calculations** for any loan\n"
    "- 💰 **FD & SIP savings projections**\n"
    "- 📋 **Income tax estimates** (new & old regime, FY 2024-25)\n"
    "- ⚖️ **Side-by-side loan comparison**\n\n"
    "Ask me anything about EMI, FD, SIP, tax, or loan comparisons.\n\n"
    "⚠️ Disclaimer: For informational purposes only. Not financial advice. Consult a SEBI-registered advisor."
)


with st.sidebar:
    st.markdown("# 💰 FinHelper")
    st.markdown(
        """
<div style="background:#fee2e2; border:2px solid #dc2626; border-radius:6px;
            padding:12px 14px; color:#7f1d1d; font-size:0.85rem; margin-bottom:14px;">
<strong>⚠️ DISCLAIMER</strong><br/>
For informational purposes only. Not financial advice. Consult a
SEBI-registered financial advisor.
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🧰 Available tools")
    st.markdown(
        "- 📐 **EMI Calculator**\n"
        "- 💰 **Savings Calculator** (FD + SIP)\n"
        "- 📋 **Tax Estimator** (India FY 2024-25)\n"
        "- ⚖️ **Loan Comparator**"
    )

    st.markdown("### 💡 Try asking")
    for q in EXAMPLE_QUERIES:
        st.code(q, language=None)

    st.markdown("---")
    if st.button("🗑️  Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent_executor" not in st.session_state:
    st.session_state.agent_executor = None


tab_chat, tab_compare = st.tabs(["💬 Chat Assistant", "⚖️ Loan Scenario Comparison"])


with tab_chat:
    st.markdown("### 💬 Chat with FinHelper")

    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(WELCOME)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("tools_used"):
                badges = " ".join(
                    f"`{TOOL_BADGES.get(t, t)}`" for t in msg["tools_used"]
                )
                st.caption(f"🔧 Tools used: {badges}")

    prompt = st.chat_input("Ask about EMI, FD, SIP, tax, or compare loans…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        api_key = os.getenv("LLM_API_KEY", "").strip()
        with st.chat_message("assistant"):
            if not api_key or api_key.lower().startswith("your-"):
                text = (
                    "The chat needs an OpenAI API key. Add one to `/app/backend/.env` "
                    "as `LLM_API_KEY=sk-...` and rerun.\n\n"
                    "⚠️ Disclaimer: For informational purposes only. Not financial advice. "
                    "Consult a SEBI-registered advisor."
                )
                st.markdown(text)
                st.session_state.messages.append(
                    {"role": "assistant", "content": text, "tools_used": []}
                )
            else:
                try:
                    if st.session_state.agent_executor is None:
                        st.session_state.agent_executor = get_agent_executor()
                    with st.spinner("Thinking…"):
                        response = st.session_state.agent_executor.invoke({
                            "input": prompt,
                            "chat_history": st.session_state.chat_history,
                        })
                    answer = response.get("output", "").strip() or "No response."
                    steps = response.get("intermediate_steps", []) or []
                    tools_used = []
                    for action, _obs in steps:
                        name = getattr(action, "tool", None)
                        if name and name not in tools_used:
                            tools_used.append(name)
                    st.markdown(answer)
                    if tools_used:
                        badges = " ".join(
                            f"`{TOOL_BADGES.get(t, t)}`" for t in tools_used
                        )
                        st.caption(f"🔧 Tools used: {badges}")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer, "tools_used": tools_used}
                    )
                    st.session_state.chat_history.append(HumanMessage(content=prompt))
                    st.session_state.chat_history.append(AIMessage(content=answer))
                    if len(st.session_state.chat_history) > 10:
                        st.session_state.chat_history = st.session_state.chat_history[-10:]
                except Exception as e:
                    err = (
                        f"Sorry, the assistant hit an error: `{e}`. Please try again.\n\n"
                        "⚠️ Disclaimer: For informational purposes only. Not financial advice. "
                        "Consult a SEBI-registered advisor."
                    )
                    st.error(err)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": err, "tools_used": []}
                    )


with tab_compare:
    st.markdown("### ⚖️ Compare two loan scenarios side-by-side")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 🅰️ Option A")
        a_name = st.text_input("Label", value="Bank A", key="a_name")
        a_principal = st.number_input(
            "Principal (₹)", min_value=1000.0, value=2_500_000.0, step=50_000.0, key="a_p"
        )
        a_rate = st.number_input(
            "Annual Rate (%)", min_value=0.1, max_value=40.0, value=8.5, step=0.1, key="a_r"
        )
        a_months = st.number_input(
            "Tenure (months)", min_value=1, max_value=480, value=240, step=12, key="a_t"
        )
        st.caption(f"↳ {int(a_months) // 12} years {int(a_months) % 12} months")

    with col_b:
        st.markdown("#### 🅱️ Option B")
        b_name = st.text_input("Label", value="Bank B", key="b_name")
        b_principal = st.number_input(
            "Principal (₹)", min_value=1000.0, value=2_500_000.0, step=50_000.0, key="b_p"
        )
        b_rate = st.number_input(
            "Annual Rate (%)", min_value=0.1, max_value=40.0, value=9.0, step=0.1, key="b_r"
        )
        b_months = st.number_input(
            "Tenure (months)", min_value=1, max_value=480, value=180, step=12, key="b_t"
        )
        st.caption(f"↳ {int(b_months) // 12} years {int(b_months) % 12} months")

    def _emi_local(p: float, ar: float, n: int):
        r = ar / 1200.0
        if r == 0:
            e = p / n
        else:
            e = p * r * (1 + r) ** n / ((1 + r) ** n - 1)
        tp = e * n
        ti = tp - p
        return e, tp, ti

    if st.button("🔍 Compare Now", type="primary", use_container_width=True):
        ea, tpa, tia = _emi_local(a_principal, a_rate, int(a_months))
        eb, tpb, tib = _emi_local(b_principal, b_rate, int(b_months))

        st.markdown("---")
        st.markdown("### 📊 Results")
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"#### 🅰️ {a_name}")
            st.metric("Monthly EMI", f"₹{ea:,.2f}")
            st.metric("Total Interest", f"₹{tia:,.2f}")
            st.metric("Total Payment", f"₹{tpa:,.2f}")
        with m2:
            st.markdown(f"#### 🅱️ {b_name}")
            st.metric("Monthly EMI", f"₹{eb:,.2f}")
            st.metric("Total Interest", f"₹{tib:,.2f}")
            st.metric("Total Payment", f"₹{tpb:,.2f}")

        chart_df = pd.DataFrame(
            {
                "Principal": [a_principal, b_principal],
                "Interest": [tia, tib],
            },
            index=[a_name, b_name],
        )
        st.markdown("#### Principal vs Interest")
        st.bar_chart(chart_df)

        table_df = pd.DataFrame(
            {
                "Metric": [
                    "Principal (₹)", "Annual Rate (%)", "Tenure (months)",
                    "Monthly EMI (₹)", "Total Interest (₹)", "Total Payment (₹)",
                ],
                a_name: [
                    f"{a_principal:,.2f}", f"{a_rate}", f"{int(a_months)}",
                    f"{ea:,.2f}", f"{tia:,.2f}", f"{tpa:,.2f}",
                ],
                b_name: [
                    f"{b_principal:,.2f}", f"{b_rate}", f"{int(b_months)}",
                    f"{eb:,.2f}", f"{tib:,.2f}", f"{tpb:,.2f}",
                ],
            }
        )
        st.markdown("#### Full comparison")
        st.dataframe(table_df, use_container_width=True, hide_index=True)

        if tpa < tpb:
            savings = tpb - tpa
            st.success(
                f"🏆 **{a_name}** is the better option — saves **₹{savings:,.2f}** "
                f"in total payment over the life of the loan."
            )
        elif tpb < tpa:
            savings = tpa - tpb
            st.success(
                f"🏆 **{b_name}** is the better option — saves **₹{savings:,.2f}** "
                f"in total payment over the life of the loan."
            )
        else:
            st.info("Both loans cost exactly the same overall — it's a tie.")

        st.warning(
            "⚠️ Disclaimer: For informational purposes only. Not financial advice. "
            "Consult a SEBI-registered advisor."
        )
