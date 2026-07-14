# 💰 FinHelper – AI Powered Personal Finance Assistant

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-red)
![LangChain](https://img.shields.io/badge/LangChain-Agentic_AI-green)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o_Mini-purple)
![License](https://img.shields.io/badge/License-Educational-orange)

An **AI-powered personal finance assistant** for Indian users built using **Python**, **Streamlit**, **LangChain**, and **OpenAI GPT-4o Mini**.

FinHelper helps users calculate **Loan EMIs**, estimate **Indian Income Tax**, project **FD & SIP savings**, compare loan options, and answer finance-related questions through an intelligent conversational AI interface. The application uses **LangChain Tool Calling Agents** to route financial queries to specialized Python tools, ensuring accurate and reliable calculations.

---

# 🚀 Features

- 🤖 AI Chat Assistant
- 📐 EMI Calculator
- 💰 Savings Calculator (FD + SIP)
- 📋 Income Tax Estimator (India FY 2024-25)
- ⚖️ Loan Comparison Tool
- 💬 Interactive Chat Interface
- 🧠 LangChain Tool Calling Agent
- 📊 Loan Comparison Dashboard
- 🔐 Secure API Key Management
- 🇮🇳 Indian Currency Formatting

---

# 🛠 Tech Stack

## Programming Language

- Python 3

## Frontend

- Streamlit

## AI Framework

- LangChain

## Large Language Model

- OpenAI GPT-4o Mini

## Libraries

- Streamlit
- LangChain
- LangChain OpenAI
- LangChain Core
- Pandas
- NumPy
- Python Dotenv

## Environment

- OpenAI API
- Environment Variables (.env)

---

# 📂 Project Structure

```text
FinHelper/
│
├── 📄 app.py
├── 📄 agent.py
├── 📄 tools.py
├── 📄 requirements.txt
├── 📄 README.md
├── 📂 screenshots/
├── 📄 .gitignore
└── 📄 .env (Not uploaded to GitHub)
```

---

# 🏗 Architecture

```text
                User
                  │
                  ▼
         Streamlit Frontend
                  │
                  ▼
      LangChain Tool Calling Agent
                  │
          OpenAI GPT-4o Mini
                  │
        Select Appropriate Tool
                  │
      ┌───────────┼──────────────┬──────────────┐
      ▼           ▼              ▼              ▼
 EMI Calculator  Savings Tool  Tax Tool  Loan Comparator
                  │
                  ▼
         Financial Calculation
                  │
                  ▼
        AI Generated Response
                  │
                  ▼
           Streamlit Interface
```

---

# 📸 Screenshots

## 🤖 AI Assistant & Available Tools

<p align="center">
  <img src="screenshots/Screenshot (4).png" width="900">
</p>

---

## ⚖️ Loan Comparator

<p align="center">
  <img src="screenshots/Screenshot (5).png" width="900">
</p>

---

## 📊 Loan Comparison Results

<p align="center">
  <img src="screenshots/Screenshot (6).png" width="900">
</p>

---

## 📈 Loan Comparison Chart

<p align="center">
  <img src="screenshots/Screenshot (7).png" width="900">
</p>

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/ap1807/FinHelper.git
```

```bash
cd FinHelper
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
```

Activate it

```bash
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
LLM_API_KEY=your_openai_api_key
LLM_MODEL=gpt-4o-mini
```

---

## 5. Run the Application

```bash
streamlit run app.py
```

The application will automatically open in your browser.

---

# 🧰 Available Tools

## 📐 EMI Calculator

Calculates:

- Monthly EMI
- Total Interest
- Total Payment
- Interest Ratio

---

## 💰 Savings Calculator

Supports:

- Fixed Deposit (FD)
- Monthly SIP

Returns:

- Maturity Amount
- Interest Earned
- SIP Corpus
- Total Corpus

---

## 📋 Income Tax Estimator

Supports:

- New Tax Regime
- Old Tax Regime

Returns:

- Taxable Income
- Basic Tax
- Health & Education Cess
- Total Tax
- Effective Tax Rate
- Monthly Tax Outflow

---

## ⚖️ Loan Comparison Tool

Compares:

- Monthly EMI
- Total Interest
- Total Payment

Recommends the better loan option based on total repayment.

---

# 🤖 AI Capabilities

- LangChain Tool Calling Agent
- OpenAI GPT-4o Mini Integration
- Prompt Engineering
- Conversation Memory
- Chat History
- Automatic Tool Selection
- Financial Tool Routing
- Deterministic Financial Calculations

---

# 💡 Skills Demonstrated

- Python Programming
- Streamlit Development
- LangChain Agents
- OpenAI API Integration
- Prompt Engineering
- Tool Calling
- Function Calling
- Agentic AI
- Financial Calculations
- Environment Variable Management
- Interactive Dashboard Development

---

# 🔮 Future Improvements

- User Authentication
- Database Integration
- Expense Tracker
- Portfolio Tracker
- Mutual Fund Analysis
- Stock Market API Integration
- PDF Report Generation
- Voice Assistant
- Dark Mode
- Multi-language Support

---

# 📜 Disclaimer

This project is developed for **educational and informational purposes only**.

It does **not** provide financial, investment, or legal advice.

Users should consult a **SEBI-registered financial advisor** before making investment or financial decisions.

---

# 👨‍💻 Author

**Adityaraj Patil**

B.Tech – Computer Science & Engineering (AI & ML)  
Lovely Professional University

- GitHub: https://github.com/ap1807
- LinkedIn: *Add your LinkedIn profile here*

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub. It helps others discover the project and motivates future improvements.