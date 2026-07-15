
"""
Financial Calculation Tools for FinHelper LangChain Agent

This module defines LangChain @tool decorated functions for:
- EMI (Equated Monthly Installment) calculation
- FD (Fixed Deposit) and SIP (Systematic Investment Plan) maturity projections
- India income tax estimation (FY 2024-25, both regimes)
- Side-by-side loan scenario comparison

All tools return formatted markdown strings for display in the chat interface.
"""

from langchain_core.tools import tool


# =============================================================================
# HELPER FUNCTION: Indian Number Formatting
# =============================================================================
def _inr(x: float) -> str:
    """
    Format a number as Indian Rupee currency string.
    
    Indian numbering system groups digits differently:
    - First 3 digits from right (hundreds, tens, units)
    - Then groups of 2 digits thereafter (lakhs, crores, etc.)
    
    Examples:
        1234567.89 → "₹12,34,567.89"
        1000.00 → "₹1,000.00"
        -500.50 → "₹-500.50"
    
    Args:
        x: Numeric value to format
        
    Returns:
        Formatted string with ₹ symbol and Indian grouping
    """
    # Format with standard comma grouping first
    s = f"{x:,.2f}"
    parts = s.split(".")
    
    # Remove existing commas to regroup Indian-style
    whole = parts[0].replace(",", "")
    
    # Handle negative numbers separately
    neg = whole.startswith("-")
    if neg:
        whole = whole[1:]
    
    # Apply Indian grouping logic
    if len(whole) <= 3:
        # Small numbers don't need grouping
        grouped = whole
    else:
        # Last 3 digits form the first group (hundreds place)
        last3 = whole[-3:]
        rest = whole[:-3]
        
        # Remaining digits are grouped in pairs from right to left
        chunks = []
        while len(rest) > 2:
            chunks.append(rest[-2:])
            rest = rest[:-2]
        if rest:
            chunks.append(rest)
        
        # Reverse chunks and join with commas
        grouped = ",".join(reversed(chunks)) + "," + last3
    
    # Reconstruct final string with sign and decimal
    sign = "-" if neg else ""
    return f"₹{sign}{grouped}.{parts[1]}"


# =============================================================================
# TOOL 1: EMI Calculator
# =============================================================================
@tool
def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> str:
    """Calculate the monthly EMI for a loan using the standard reducing-balance formula.

    Args:
        principal: Loan amount in INR.
        annual_rate: Annual interest rate in percent (e.g. 8.5).
        tenure_months: Loan tenure in months.
    """
    # Input validation
    if principal <= 0 or tenure_months <= 0 or annual_rate < 0:
        return "Invalid input: principal, tenure and rate must be positive."
    
    # Ensure tenure is integer
    n = int(tenure_months)
    
    # Convert annual percentage rate to monthly decimal rate
    # Formula: monthly_rate = annual_rate / 12 / 100
    r = annual_rate / 1200.0
    
    # Calculate EMI using reducing balance formula
    # Special case: if rate is 0%, simple division
    if r == 0:
        emi = principal / n
    else:
        # Standard EMI formula: EMI = P × r × (1+r)^n / ((1+r)^n - 1)
        emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    
    # Calculate derived metrics
    total_payment = emi * n          # Total amount paid over loan lifetime
    total_interest = total_payment - principal  # Total interest component
    ratio = (total_interest / principal) * 100.0 if principal > 0 else 0.0  # Interest as % of principal
    
    # Format output as markdown with all relevant details
    return (
        f"**Loan EMI Calculation**\n\n"
        f"- Principal: {_inr(principal)}\n"
        f"- Annual Rate: {annual_rate}% p.a.\n"
        f"- Tenure: {n} months ({n // 12} yrs {n % 12} mo)\n\n"
        f"**Monthly EMI: {_inr(emi)}**\n"
        f"- Total Payment: {_inr(total_payment)}\n"
        f"- Total Interest: {_inr(total_interest)}\n"
        f"- Interest Ratio: {ratio:.2f}% of principal"
    )


# =============================================================================
# TOOL 2: Savings Calculator (FD + SIP)
# =============================================================================
@tool
def calculate_savings(
    principal: float,
    annual_rate: float,
    years: int,
    monthly_sip: float = 0,
) -> str:
    """Estimate maturity value of an FD (quarterly compounding) with an optional monthly SIP.

    Args:
        principal: Lump-sum FD amount in INR.
        annual_rate: Annual interest rate in percent.
        years: Investment horizon in whole years.
        monthly_sip: Optional monthly SIP amount in INR (default 0).
    """
    # Input validation
    if years <= 0 or annual_rate < 0 or principal < 0 or monthly_sip < 0:
        return "Invalid input: values must be non-negative and years > 0."
    
    # --- FD Calculation (Quarterly Compounding) ---
    # Formula: A = P × (1 + r/4)^(4×t)
    # Where r = annual rate, t = years, 4 = quarterly compounding frequency
    fd_maturity = principal * (1 + annual_rate / 400.0) ** (4 * years) if principal > 0 else 0.0
    fd_interest = fd_maturity - principal
    
    # --- SIP Calculation (Monthly Compounding) ---
    months = years * 12
    mr = annual_rate / 1200.0  # Monthly rate
    
    if monthly_sip > 0 and mr > 0:
        # Future Value of SIP: FV = P × [((1+r)^n - 1) / r] × (1+r)
        # This accounts for payments at the beginning of each period
        sip_corpus = monthly_sip * (((1 + mr) ** months - 1) / mr) * (1 + mr)
    elif monthly_sip > 0:
        # If rate is 0%, just sum up all SIP payments
        sip_corpus = monthly_sip * months
    else:
        # No SIP component
        sip_corpus = 0.0
    
    # Calculate SIP returns
    sip_invested = monthly_sip * months  # Total amount invested via SIP
    sip_gain = sip_corpus - sip_invested  # Returns from SIP
    
    # Combined corpus
    total_corpus = fd_maturity + sip_corpus

    # Build output message
    out = [
        "**Savings Projection**\n",
        f"- Horizon: {years} years @ {annual_rate}% p.a.",
        f"- FD Principal: {_inr(principal)}",
        f"- FD Maturity (quarterly compounding): **{_inr(fd_maturity)}**",
        f"- FD Interest Earned: {_inr(fd_interest)}",
    ]
    
    # Add SIP details only if SIP amount is specified
    if monthly_sip > 0:
        out.extend([
            "",
            f"- Monthly SIP: {_inr(monthly_sip)} for {months} months",
            f"- SIP Invested: {_inr(sip_invested)}",
            f"- SIP Corpus: **{_inr(sip_corpus)}**",
            f"- SIP Gain: {_inr(sip_gain)}",
            "",
            f"**Total Corpus (FD + SIP): {_inr(total_corpus)}**",
        ])
    
    return "\n".join(out)


# =============================================================================
# TOOL 3: Income Tax Estimator (India FY 2024-25)
# =============================================================================
@tool
def calculate_tax(annual_income: float, regime: str = "new") -> str:
    """Estimate India income tax for FY 2024-25 under new or old regime.

    Args:
        annual_income: Gross annual income in INR.
        regime: "new" (default) or "old".
    """
    # Input validation
    if annual_income < 0:
        return "Invalid input: income cannot be negative."
    
    # Normalize regime input
    regime = (regime or "new").lower().strip()
    if regime not in ("new", "old"):
        return "Invalid regime. Use 'new' or 'old'."

    # --- Configure tax parameters based on regime ---
    if regime == "new":
        # New regime (FY 2024-25): Higher standard deduction, more slabs
        std_ded = 75_000.0
        slabs = [
            (0, 300_000, 0.00),           # 0-3L: Nil
            (300_000, 700_000, 0.05),     # 3-7L: 5%
            (700_000, 1_000_000, 0.10),   # 7-10L: 10%
            (1_000_000, 1_200_000, 0.15), # 10-12L: 15%
            (1_200_000, 1_500_000, 0.20), # 12-15L: 20%
            (1_500_000, float("inf"), 0.30), # 15L+: 30%
        ]
        rebate_limit = 700_000.0  # Full rebate if taxable income ≤ 7L
    else:
        # Old regime: Lower standard deduction, fewer slabs but more deductions allowed
        std_ded = 50_000.0
        slabs = [
            (0, 250_000, 0.00),           # 0-2.5L: Nil
            (250_000, 500_000, 0.05),     # 2.5-5L: 5%
            (500_000, 1_000_000, 0.20),   # 5-10L: 20%
            (1_000_000, float("inf"), 0.30), # 10L+: 30%
        ]
        rebate_limit = 500_000.0  # Full rebate if taxable income ≤ 5L

    # --- Calculate Taxable Income ---
    taxable = max(0.0, annual_income - std_ded)
    
    # --- Calculate Basic Tax using slab system ---
    basic_tax = 0.0
    for lo, hi, rate in slabs:
        if taxable <= lo:
            # Income doesn't reach this slab
            break
        # Calculate taxable amount in current slab
        chunk = min(taxable, hi) - lo
        if chunk > 0:
            basic_tax += chunk * rate
    
    # --- Apply Rebate (Section 87A) ---
    # If taxable income is within rebate limit, tax becomes zero
    if taxable <= rebate_limit:
        basic_tax = 0.0
    
    # --- Add Health & Education Cess (4% on basic tax) ---
    cess = basic_tax * 0.04
    
    # --- Final Calculations ---
    total_tax = basic_tax + cess
    effective = (total_tax / annual_income * 100.0) if annual_income > 0 else 0.0
    monthly = total_tax / 12.0  # Approximate monthly tax outflow

    return (
        f"**Income Tax Estimate — {regime.title()} Regime (FY 2024-25)**\n\n"
        f"- Gross Income: {_inr(annual_income)}\n"
        f"- Standard Deduction: {_inr(std_ded)}\n"
        f"- Taxable Income: {_inr(taxable)}\n\n"
        f"- Basic Tax: {_inr(basic_tax)}\n"
        f"- Health & Education Cess (4%): {_inr(cess)}\n"
        f"- **Total Tax: {_inr(total_tax)}**\n"
        f"- Effective Tax Rate: {effective:.2f}%\n"
        f"- Approx. Monthly Tax Outflow: {_inr(monthly)}"
    )


# =============================================================================
# TOOL 4: Loan Scenario Comparison
# =============================================================================
@tool
def compare_loan_scenarios(
    loan1_name: str, loan1_principal: float, loan1_rate: float, loan1_tenure_months: int,
    loan2_name: str, loan2_principal: float, loan2_rate: float, loan2_tenure_months: int,
) -> str:
    """Compare two loan options side-by-side and pick the cheaper one by total payment.

    Args:
        loan1_name: Label for loan 1 (e.g. "Bank A").
        loan1_principal: Principal for loan 1 in INR.
        loan1_rate: Annual rate for loan 1 in percent.
        loan1_tenure_months: Tenure for loan 1 in months.
        loan2_name: Label for loan 2 (e.g. "Bank B").
        loan2_principal: Principal for loan 2 in INR.
        loan2_rate: Annual rate for loan 2 in percent.
        loan2_tenure_months: Tenure for loan 2 in months.
    """

    # --- Internal EMI helper function ---
    def _emi(p, ar, n):
        """
        Calculate EMI and related metrics.
        
        Returns:
            Tuple of (emi, total_payment, total_interest)
        """
        r = ar / 1200.0
        
        # Handle invalid inputs
        if p <= 0 or n <= 0:
            return 0.0, 0.0, 0.0
        
        # Calculate EMI
        if r == 0:
            e = p / n
        else:
            e = p * r * (1 + r) ** n / ((1 + r) ** n - 1)
        
        tp = e * n      # Total payment
        ti = tp - p     # Total interest
        return e, tp, ti

    # --- Calculate EMI for both loans ---
    e1, tp1, ti1 = _emi(loan1_principal, loan1_rate, int(loan1_tenure_months))
    e2, tp2, ti2 = _emi(loan2_principal, loan2_rate, int(loan2_tenure_months))
    
    # --- Determine winner based on total payment ---
    # Lower total payment is considered better
    winner_name = loan1_name if tp1 < tp2 else (loan2_name if tp2 < tp1 else "Tie")
    savings = abs(tp1 - tp2)  # Absolute difference in total payments

    # --- Build comparison table in markdown format ---
    header = f"**Loan Comparison — {loan1_name} vs {loan2_name}**\n"
    table = (
        f"| Metric | {loan1_name} | {loan2_name} |\n"
        f"|---|---|---|\n"
        f"| Principal | {_inr(loan1_principal)} | {_inr(loan2_principal)} |\n"
        f"| Rate | {loan1_rate}% p.a. | {loan2_rate}% p.a. |\n"
        f"| Tenure | {int(loan1_tenure_months)} mo | {int(loan2_tenure_months)} mo |\n"
        f"| Monthly EMI | {_inr(e1)} | {_inr(e2)} |\n"
        f"| Total Interest | {_inr(ti1)} | {_inr(ti2)} |\n"
        f"| Total Payment | {_inr(tp1)} | {_inr(tp2)} |\n"
    )
    
    # --- Add verdict ---
    if winner_name == "Tie":
        verdict = "\n**Verdict:** Both options cost the same overall."
    else:
        verdict = f"\n**Winner:** {winner_name} — saves **{_inr(savings)}** in total payment."
    
    return header + "\n" + table + verdict
