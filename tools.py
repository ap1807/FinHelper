from langchain_core.tools import tool


def _inr(x: float) -> str:
    s = f"{x:,.2f}"
    parts = s.split(".")
    whole = parts[0].replace(",", "")
    neg = whole.startswith("-")
    if neg:
        whole = whole[1:]
    if len(whole) <= 3:
        grouped = whole
    else:
        last3 = whole[-3:]
        rest = whole[:-3]
        chunks = []
        while len(rest) > 2:
            chunks.append(rest[-2:])
            rest = rest[:-2]
        if rest:
            chunks.append(rest)
        grouped = ",".join(reversed(chunks)) + "," + last3
    sign = "-" if neg else ""
    return f"₹{sign}{grouped}.{parts[1]}"


@tool
def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> str:
    """Calculate the monthly EMI for a loan using the standard reducing-balance formula.

    Args:
        principal: Loan amount in INR.
        annual_rate: Annual interest rate in percent (e.g. 8.5).
        tenure_months: Loan tenure in months.
    """
    if principal <= 0 or tenure_months <= 0 or annual_rate < 0:
        return "Invalid input: principal, tenure and rate must be positive."
    n = int(tenure_months)
    r = annual_rate / 1200.0
    if r == 0:
        emi = principal / n
    else:
        emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    total_payment = emi * n
    total_interest = total_payment - principal
    ratio = (total_interest / principal) * 100.0 if principal > 0 else 0.0
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
    if years <= 0 or annual_rate < 0 or principal < 0 or monthly_sip < 0:
        return "Invalid input: values must be non-negative and years > 0."
    fd_maturity = principal * (1 + annual_rate / 400.0) ** (4 * years) if principal > 0 else 0.0
    fd_interest = fd_maturity - principal
    months = years * 12
    mr = annual_rate / 1200.0
    if monthly_sip > 0 and mr > 0:
        sip_corpus = monthly_sip * (((1 + mr) ** months - 1) / mr) * (1 + mr)
    elif monthly_sip > 0:
        sip_corpus = monthly_sip * months
    else:
        sip_corpus = 0.0
    sip_invested = monthly_sip * months
    sip_gain = sip_corpus - sip_invested
    total_corpus = fd_maturity + sip_corpus

    out = [
        "**Savings Projection**\n",
        f"- Horizon: {years} years @ {annual_rate}% p.a.",
        f"- FD Principal: {_inr(principal)}",
        f"- FD Maturity (quarterly compounding): **{_inr(fd_maturity)}**",
        f"- FD Interest Earned: {_inr(fd_interest)}",
    ]
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


@tool
def calculate_tax(annual_income: float, regime: str = "new") -> str:
    """Estimate India income tax for FY 2024-25 under new or old regime.

    Args:
        annual_income: Gross annual income in INR.
        regime: "new" (default) or "old".
    """
    if annual_income < 0:
        return "Invalid input: income cannot be negative."
    regime = (regime or "new").lower().strip()
    if regime not in ("new", "old"):
        return "Invalid regime. Use 'new' or 'old'."

    if regime == "new":
        std_ded = 75_000.0
        slabs = [
            (0, 300_000, 0.00), (300_000, 700_000, 0.05),
            (700_000, 1_000_000, 0.10), (1_000_000, 1_200_000, 0.15),
            (1_200_000, 1_500_000, 0.20), (1_500_000, float("inf"), 0.30),
        ]
        rebate_limit = 700_000.0
    else:
        std_ded = 50_000.0
        slabs = [
            (0, 250_000, 0.00), (250_000, 500_000, 0.05),
            (500_000, 1_000_000, 0.20), (1_000_000, float("inf"), 0.30),
        ]
        rebate_limit = 500_000.0

    taxable = max(0.0, annual_income - std_ded)
    basic_tax = 0.0
    for lo, hi, rate in slabs:
        if taxable <= lo:
            break
        chunk = min(taxable, hi) - lo
        if chunk > 0:
            basic_tax += chunk * rate
    if taxable <= rebate_limit:
        basic_tax = 0.0
    cess = basic_tax * 0.04
    total_tax = basic_tax + cess
    effective = (total_tax / annual_income * 100.0) if annual_income > 0 else 0.0
    monthly = total_tax / 12.0

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

    def _emi(p, ar, n):
        r = ar / 1200.0
        if p <= 0 or n <= 0:
            return 0.0, 0.0, 0.0
        if r == 0:
            e = p / n
        else:
            e = p * r * (1 + r) ** n / ((1 + r) ** n - 1)
        tp = e * n
        ti = tp - p
        return e, tp, ti

    e1, tp1, ti1 = _emi(loan1_principal, loan1_rate, int(loan1_tenure_months))
    e2, tp2, ti2 = _emi(loan2_principal, loan2_rate, int(loan2_tenure_months))
    winner_name = loan1_name if tp1 < tp2 else (loan2_name if tp2 < tp1 else "Tie")
    savings = abs(tp1 - tp2)

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
    if winner_name == "Tie":
        verdict = "\n**Verdict:** Both options cost the same overall."
    else:
        verdict = f"\n**Winner:** {winner_name} — saves **{_inr(savings)}** in total payment."
    return header + "\n" + table + verdict
