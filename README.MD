# 💰 FinHelper

An AI-powered personal finance assistant for Indian users built using **Streamlit**, **LangChain**, and **OpenAI GPT-4o Mini**.

FinHelper helps users calculate EMIs, estimate income tax, project savings, compare loan options, and answer finance-related questions using an AI-powered conversational interface.

---

# Features

✅ AI Chat Assistant

✅ EMI Calculator

✅ Savings Calculator (FD + SIP)

✅ Income Tax Estimator (India FY 2024-25)

✅ Loan Comparison Tool

✅ Interactive Chat Interface

✅ Tool Calling with LangChain

✅ AI-powered Financial Guidance

---

# Tech Stack

### Programming Language

- Python 3

### Frontend

- Streamlit

### AI Framework

- LangChain

### LLM

- OpenAI GPT-4o Mini

### Libraries

- Streamlit
- LangChain
- LangChain OpenAI
- Pandas
- NumPy
- Python Dotenv

### Environment

- OpenAI API
- Environment Variables

---

# Project Structure

```
FinHelper/
│
├── app.py
├── agent.py
├── tools.py
├── requirements.txt
├── README.md
├── .env
└── .venv/
```

---

# Architecture

```
                User
                  │
                  ▼
          Streamlit Frontend
                  │
                  ▼
      LangChain Tool Calling Agent
                  │
         GPT-4o Mini (OpenAI)
                  │
        Select Appropriate Tool
                  │
      ┌───────────┼────────────┐
      ▼           ▼            ▼
 EMI Calculator  Savings    Tax Estimator
                 Calculator
                      │
                      ▼
             Loan Comparator
                      │
                      ▼
              AI Response
                      │
                      ▼
                 Streamlit UI
```

---

# Installation

## Clone Repository

```bash
git clone <repository-url>
```

```bash
cd FinHelper
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv .venv
```

Activate

```bash
.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configure Environment Variables

Create a `.env` file.

```env
LLM_API_KEY=your_openai_api_key
LLM_MODEL=gpt-4o-mini
```

---

# Run Application

```bash
streamlit run app.py
```

The application will open in your browser.

---

# Available Tools

## EMI Calculator

Calculates

- Monthly EMI
- Total Interest
- Total Payment

---

## Savings Calculator

Supports

- Fixed Deposit
- SIP

Returns

- Maturity Amount
- Interest Earned
- Total Corpus

---

## Income Tax Estimator

Supports

- New Tax Regime
- Old Tax Regime

Returns

- Taxable Income
- Total Tax
- Effective Tax Rate

---

## Loan Comparison

Compares

- Monthly EMI
- Interest
- Total Payment

Recommends the better loan option.

---

# AI Features

- Tool Calling
- Function Calling
- Chat History
- Conversation Memory
- Prompt Engineering
- Financial Tool Routing

---

# Screenshots

Add screenshots here.

Example:

```
screenshots/
    home.png
    chat.png
    comparison.png
```

---

# Future Improvements

- User Authentication
- Database Integration
- Portfolio Tracker
- Mutual Fund Analysis
- Stock Market APIs
- Expense Tracker
- PDF Report Generation
- Voice Assistant
- Dark Mode

---

# Disclaimer

This project is developed for educational and informational purposes only.

It does **not** provide financial advice.

Always consult a SEBI-registered financial advisor before making investment or financial decisions.

---

# Author

**Adityaraj Patil**

B.Tech CSE (AI & ML)

Lovely Professional University

GitHub: *Add your GitHub Profile*

LinkedIn: *Add your LinkedIn Profile*