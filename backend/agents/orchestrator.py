import os
import sys
import json
import re
import pandas as pd
from typing import TypedDict, Any, Dict, List
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import checkpointer
from agents.llm import llm

# ==========================================
# 1. Deep Persona Prompt Templates
# ==========================================
PERSONA_PROMPTS = {

    "buffett": """You are Warren Buffett — the Oracle of Omaha. You have spent 70 years compounding wealth through patience, discipline, and deep fundamental analysis.

Your core principles:
- Rule #1: Never lose money. Rule #2: Never forget Rule #1.
- Price is what you pay, value is what you get. Overpaying destroys returns.
- Compound interest is the eighth wonder of the world. Time in the market > timing the market.
- Avoid debt for consumption. Use capital for productive assets only.
- Savings rate is the foundation of all wealth creation.
- Ignore market noise. Focus on the business (or personal) fundamentals.
- "Do not save what is left after spending, but spend what is left after saving."

Your task: Analyze the user's spending data and deliver a structured, hard-hitting financial advisory in Buffett's voice.
Format your report with these exact sections:
1. **The Moat Assessment** — How defensible is this person's financial position?
2. **Capital Allocation Grade** — Rate their spending decisions A–F with sharp reasoning.
3. **The Compounding Opportunity** — What specific levers, if pulled, would generate long-term compounding?
4. **Red Flags** — What spending patterns would make Buffett cringe? Be direct.
5. **The 5-Year Blueprint** — Concrete, actionable steps to materially improve net worth in 5 years.

Be direct. Be specific. Use real numbers from the data. No generic advice.""",

    "fire": """You are a hardcore F.I.R.E. (Financial Independence, Retire Early) strategist. You reached FI at age 34. You live by numbers, spreadsheets, and the 4% safe withdrawal rule.

Your core framework:
- FI Number = Annual Expenses × 25 (at 4% SWR)
- Target savings rate: 50–70%. Below 30% is unacceptable.
- Every $100/month in cuts = $30,000 less needed in your FI portfolio (at 4% SWR).
- Time to FI is almost entirely determined by savings rate, not income.
- Index funds (VTI, VXUS, BND) are the vehicle. Savings rate is the engine.
- Eliminate lifestyle inflation ruthlessly. Wants vs. needs — be brutal.
- Track net worth monthly. What gets measured gets managed.

Your task: Analyse the spending data and deliver a F.I.R.E. roadmap.
Format your report with these exact sections:
1. **FI Number & Current Trajectory** — Calculate their FI number and estimated years to FI at current savings rate.
2. **Savings Rate Analysis** — Current rate vs. F.I.R.E. targets. Gap analysis.
3. **The Expense Autopsy** — Dissect each spending category. What can be cut, optimised, or eliminated?
4. **Acceleration Levers** — The top 3 changes that would shave the most years off their FI date.
5. **30-60-90 Day Action Plan** — Specific, sequenced actions with measurable outcomes.

Use the actual numbers. Be brutally honest. F.I.R.E. is not for the faint of heart.""",

    "kiyosaki": """You are Robert Kiyosaki — author of Rich Dad Poor Dad. You see the world through the lens of cashflow, assets, liabilities, and the Cashflow Quadrant.

Your core framework:
- An asset puts money IN your pocket. A liability takes money OUT. Most people confuse the two.
- Your house is NOT an asset. Your car is NOT an asset. They are liabilities consuming cashflow.
- The rich buy assets first. The poor buy liabilities and call them assets.
- Build passive income streams until they exceed your expenses. That is financial freedom.
- Tax strategy is wealth strategy. The rich use corporations to pay taxes last.
- The Cashflow Quadrant: E (Employee) → S (Self-employed) → B (Business owner) → I (Investor).
- Financial IQ is the most important intelligence to develop.

Your task: Examine the user's financial data through the Rich Dad lens.
Format your report with these exact sections:
1. **Asset vs. Liability Audit** — Classify each major spending category. What is building wealth vs. draining it?
2. **Cashflow Quadrant Position** — Where does this person sit? What needs to change?
3. **The Passive Income Gap** — How much passive income do they need? How far are they from it?
4. **Asset Acquisition Roadmap** — Specific asset classes to target given their current cashflow profile.
5. **Rich Dad's Wake-Up Call** — The single most important mindset shift this person needs to make.

Be provocative, direct, and educational. Challenge conventional thinking.""",

    "sethi": """You are Ramit Sethi — author of "I Will Teach You To Be Rich". You believe personal finance should enable your Rich Life, not restrict it.

Your core principles:
- The Conscious Spending Plan: 50–60% Fixed costs, 10% Savings, 5–10% Investments, 20–35% Guilt-free spending.
- Automate everything: salary arrives → auto-transfer to savings → auto-pay bills → rest is guilt-free.
- Optimize the Big Wins (housing cost, salary negotiation, car choice) — not the lattes.
- Spend extravagantly on what you love. Cut mercilessly on what you don't care about.
- Use credit cards for rewards; pay the full balance every month — never pay interest.
- Money is a tool for your Rich Life, not a scoreboard. Define YOUR Rich Life first.
- "I don't want to hear about your $3 latte — I want to know if you have your finances automated."

Your task: Analyse the spending data and build the user's personalised Conscious Spending Plan.
Format your report with these exact sections:
1. **Rich Life Audit** — What does this person's spending reveal about their actual priorities vs. stated priorities?
2. **Automation Blueprint** — Exact step-by-step system to automate their finances (accounts, transfers, timing).
3. **The Big Wins Analysis** — Identify the 2–3 highest-leverage cost optimizations (not small cuts).
4. **Guilt-Free Spending Budget** — How much is available for guilt-free spending after automating savings?
5. **30-Day Action Plan** — Specific, calendar-sequenced actions to implement this week, this month.

Be energetic, specific, and empowering. No shame, no deprivation — just optimization.""",

    "indian_expert": """You are a SEBI-registered Indian Certified Financial Planner (CFP) with 20 years of experience helping Indian middle-class families build wealth.

Your core framework:
- Tax-first thinking: max out Section 80C (₹1.5L), 80D health insurance, HRA, NPS 80CCD(1B extra ₹50K).
- SIP discipline is non-negotiable: start a ₹500/month SIP today rather than waiting for the "right time".
- Emergency fund = 6 months of expenses in a liquid mutual fund or high-interest savings account.
- Never mix insurance and investment: term insurance only (cover = 10–15× annual income), separate ELSS for tax saving.
- Goal-based investing: separate SIP folios for each goal (child's education, home down payment, retirement).
- Indian context: Sensex/Nifty long-term CAGR ~12%, inflation ~6%, real return ~6%.
- New vs Old Tax Regime: analyse which is better based on deductions available.

Your task: Provide an India-specific financial advisory using rupee amounts and Indian instruments.
Format your report with these exact sections:
1. **Tax Optimization Plan** — Which regime (new/old) is better? Which 80C instruments to use? Estimated tax saved in ₹.
2. **SIP Roadmap** — Specific SIP amounts, fund categories (large cap, ELSS, debt), and goal mapping.
3. **Emergency Fund Status** — How many months covered? Recommended target in ₹. Where to park it.
4. **Insurance Audit** — Term cover needed vs. existing. Any LIC endowment plans to surrender?
5. **Goal-Based Portfolio** — Map each financial goal to a specific investment instrument and timeline.

Use ₹ amounts throughout. Reference Indian instruments (PPF, NPS, ELSS, Zerodha, Groww). Be practical and warm."""
}

# ==========================================
# 2. State Definition
# ==========================================
class GraphState(TypedDict):
    transactions:      List[Dict[str, Any]]
    extracted_data:    Dict[str, Any]
    advisory_report:   str
    critique_feedback: str
    revision_count:    int
    user_preference:   str   # buffett | fire | kiyosaki | sethi | indian_expert
    is_flawed:         bool
    currency:          str   # INR | USD
    knowledge_context: str


# ==========================================
# 3. Rule-Based Fallback Report
# ==========================================
def _rule_based_report(persona: str, summary: dict, metrics: dict) -> str:
    """Rich fallback report when the LLM is unavailable."""
    income       = metrics.get("income", 0)
    expenses     = metrics.get("expenses", 0)
    savings      = metrics.get("savings", 0)
    savings_rate = metrics.get("savings_rate", 0)
    top_expense  = metrics.get("top_expense", "N/A")
    fi_number    = expenses * 25 * 12  # annualized

    if persona == "buffett":
        return f"""### The Moat Assessment
Your financial position shows a {savings_rate:.1f}% savings rate. Buffett would say you have a narrow moat — defensible, but not yet a fortress. Your largest outflow is **{top_expense}** at ${abs(summary.get(top_expense, 0)):,.0f} this period.

### Capital Allocation Grade: {"B" if savings_rate >= 20 else "C" if savings_rate >= 10 else "D"}
{"You are saving meaningfully, but Buffett allocates capital to where it compounds hardest — examine whether your savings are parked in productive assets or sitting in low-yield accounts." if savings_rate >= 20 else "Capital is being consumed faster than it is being deployed for growth. This is the pattern of financial stagnation."}

### The Compounding Opportunity
At ${savings:,.0f} saved per period, invested in a broad index fund averaging 10% annually:
- In 10 years: ~${savings * 12 * 17.5:,.0f}
- In 20 years: ~${savings * 12 * 57.3:,.0f}
The earlier you start, the more violently compounding works in your favour.

### Red Flags
{"No critical red flags detected. Maintain discipline." if savings_rate >= 25 else f"Discretionary spending is competing with your compounding engine. Every dollar spent on {top_expense} today costs you 10x in 20 years at 10% annual returns."}

### The 5-Year Blueprint
1. Increase savings rate to 30%+ by cutting the top discretionary category
2. Automate investment contributions on payday — remove human decision from equation
3. Build a 6-month emergency fund before deploying capital to equities
4. Invest 80% of savings in low-cost index funds (expense ratio < 0.1%)
5. Review and eliminate every subscription and recurring charge annually"""

    elif persona == "fire":
        years_to_fi = None
        if savings_rate > 0:
            # Simplified FI calculation
            years_to_fi = round((100 - savings_rate) / savings_rate * 0.83, 1)
        return f"""### FI Number & Current Trajectory
- **Monthly expenses:** ${expenses:,.0f}
- **Annual expenses:** ${expenses * 12:,.0f}
- **FI Number (25× rule):** ${fi_number:,.0f}
- **Current savings rate:** {savings_rate:.1f}%
- **Estimated years to FI:** {f"{years_to_fi} years" if years_to_fi else "Cannot calculate — savings rate too low"}

{"🟢 You are on a F.I.R.E. trajectory." if savings_rate >= 40 else "🔴 You are NOT on a F.I.R.E. trajectory at this savings rate."}

### Savings Rate Analysis
Current: **{savings_rate:.1f}%** | F.I.R.E. target: **50–70%** | Gap: **{max(0, 50 - savings_rate):.1f}%**
To close this gap, you need to either increase income or cut ${max(0, (0.5 - savings_rate/100) * income):,.0f}/period in expenses.

### The Expense Autopsy
{chr(10).join(f"- **{cat}**: ${abs(amt):,.0f} — {'✅ Necessary' if cat in ['Essential Living', 'Income'] else '⚠️ Examine closely'}" for cat, amt in summary.items())}

### Acceleration Levers
1. Eliminate all discretionary spending above baseline — saves ${abs(summary.get('Discretionary', 0)):,.0f}/period
2. Meal prep to cut food spend by 60% — compound effect over 10 years is enormous
3. Negotiate rent or relocate to a lower cost-of-living area — housing is the single largest FI lever

### 30-60-90 Day Action Plan
- **30 days:** Track every dollar. Cancel unused subscriptions. Set up auto-invest.
- **60 days:** Hit {min(savings_rate + 10, 70):.0f}% savings rate. Renegotiate bills.
- **90 days:** Open index fund account. Deploy first lump sum. Calculate updated FI date."""

    elif persona == "kiyosaki":
        passive_gap = expenses  # need passive income to cover expenses
        return f"""### Asset vs. Liability Audit
{chr(10).join(f"- **{cat}**: ${abs(amt):,.0f} — {'🟢 INCOME (Asset)' if amt > 0 else '🔴 LIABILITY (Outflow)'}" for cat, amt in summary.items())}

Total assets generating income: **${income:,.0f}/period**
Total liabilities consuming cashflow: **${expenses:,.0f}/period**
Net cashflow: **${savings:,.0f}/period** {"✅" if savings > 0 else "❌ NEGATIVE CASHFLOW"}

### Cashflow Quadrant Position
Based on your income structure, you appear to be operating as an **E (Employee)**. The goal is to move capital toward the **I (Investor)** quadrant where money works for you.

### The Passive Income Gap
To achieve financial freedom, your passive income must exceed ${expenses:,.0f}/period.
At a conservative 6% yield, you need an asset base of **${passive_gap * 12 / 0.06:,.0f}** generating income for you.

### Asset Acquisition Roadmap
1. Start with dividend-paying index funds — immediate passive income, low barrier
2. At ${savings * 12 * 2:,.0f} in liquid savings, consider your first real estate investment
3. Build a side income stream that earns without your direct time (digital, licensing, rental)
4. Every new asset should generate cash immediately — no speculative holds

### Rich Dad's Wake-Up Call
{"You have positive cashflow — now the question is: are you deploying it into assets or letting it sit?" if savings > 0 else "You are spending more than you earn. This is the definition of the Rat Race. Stop buying liabilities. Build assets first."}
The middle class buys liabilities thinking they are assets. Become financially literate first, wealthy second."""

    elif persona == "sethi":
        ccy = "₹" if metrics.get("currency") == "INR" else "$"
        guilt_free = max(0, income * 0.25)
        return f"""### Rich Life Audit
Your spending data reveals your actual priorities. With {savings_rate:.1f}% savings rate, you are {"building toward your Rich Life" if savings_rate >= 20 else "spending reactively rather than intentionally"}.
Top spending category: **{top_expense}** ({ccy}{abs(summary.get(top_expense, 0)):,.0f}/period) — does this bring you genuine joy?

### Automation Blueprint
1. Open a separate high-yield savings account (target: 10% of income = {ccy}{income*0.1:,.0f}/period)
2. Set up auto-transfer on payday: {ccy}{income*0.1:,.0f} → savings, {ccy}{income*0.05:,.0f} → investments
3. Auto-pay all fixed bills via standing instruction
4. Remaining balance = guilt-free spending. No tracking required.

### The Big Wins Analysis
- **Housing**: If rent > 30% of income, this is your #1 lever — not cutting coffee
- **Income**: Negotiate salary or add one freelance client — worth more than 10 years of frugality
- **Subscriptions**: Audit and cancel anything unused — saves {ccy}{abs(summary.get('Subscriptions', summary.get('Discretionary', 0))) * 0.5:,.0f}/period

### Guilt-Free Spending Budget
After automating savings and investments: **{ccy}{guilt_free:,.0f}/period** is yours to spend without guilt.
Spend this on experiences, food, hobbies — whatever makes YOUR Rich Life rich.

### 30-Day Action Plan
- **Week 1**: Open savings account. Set up auto-transfer for {ccy}{income*0.1:,.0f}.
- **Week 2**: Cancel 2 subscriptions you haven't used in 30 days.
- **Week 3**: Schedule salary negotiation or identify one income-boosting opportunity.
- **Week 4**: Automate investment contribution (even {ccy}500 to start). Celebrate — you're done!"""

    else:  # indian_expert
        ccy = "₹"
        tax_saving_80c = min(income * 0.12, 150000)  # rough estimate
        sip_amount = max(500, round(savings * 0.6, -2))
        emergency_target = expenses * 6
        return f"""### Tax Optimization Plan
Estimated Section 80C investment needed: **₹{tax_saving_80c:,.0f}** (cap: ₹1,50,000)
Recommended instruments: ELSS mutual fund (tax saving + wealth creation), PPF (safe, tax-free returns)
With Old Tax Regime + full 80C: estimated tax saving of ₹{tax_saving_80c * 0.20:,.0f}–₹{tax_saving_80c * 0.30:,.0f}/year

### SIP Roadmap
Start a monthly SIP of **₹{sip_amount:,.0f}** immediately.
- 60% in Large Cap / Nifty 50 Index Fund (stability)
- 30% in ELSS (tax saving under 80C)
- 10% in Liquid Fund (emergency buffer)
At 12% CAGR: ₹{sip_amount:,.0f}/month becomes ~₹{sip_amount * 12 * 17.5:,.0f} in 10 years.

### Emergency Fund Status
Target: **₹{emergency_target:,.0f}** (6 months of ₹{expenses:,.0f} expenses)
Park in: Paytm Money Liquid Fund, Zerodha Coin liquid overnight fund, or FD with sweep facility.
{"✅ On track if you have this amount liquid." if savings >= emergency_target / 12 else f"⚠️ At current savings rate, you need {emergency_target / max(savings, 1):.0f} months to build this fund."}

### Insurance Audit
Term insurance needed: ₹{income * 150:,.0f} (15× annual income of ₹{income * 12:,.0f})
Health insurance: ₹5–10 lakh floater for family. Premium qualifies for 80D deduction.
Action: If you have LIC endowment/money-back policies, consider surrendering and reinvesting in ELSS + Term.

### Goal-Based Portfolio
Map each goal to a dedicated SIP:
- Emergency Fund → Liquid Fund (target: ₹{emergency_target:,.0f} in 12 months)
- Short-term goals (1–3 years) → Debt mutual funds / RD
- Long-term goals (5+ years) → Equity SIP in Nifty 50 index fund
- Retirement → NPS Tier-1 (extra ₹50,000 deduction under 80CCD(1B)) + PPF"""


# ==========================================
# 4. Node Implementations
# ==========================================
def extraction_node(state: GraphState) -> GraphState:
    print("Executing: extraction_node")
    transactions = state.get("transactions", [])
    status = "success" if transactions else "failed_validation"
    return {"extracted_data": {"status": status, "data": transactions}}


def analytics_node(state: GraphState) -> GraphState:
    print("Executing: analytics_node")
    transactions = state.get("transactions", [])
    if not transactions:
        return state

    df = pd.DataFrame(transactions)
    summary = df.groupby("category")["amount"].sum().to_dict()

    # Richer metrics
    income   = sum(v for v in summary.values() if v > 0)
    expenses = sum(abs(v) for v in summary.values() if v < 0)
    savings  = income - expenses
    savings_rate = (savings / income * 100) if income > 0 else 0
    top_expense = max(
        ((abs(v), k) for k, v in summary.items() if v < 0),
        default=(0, "N/A")
    )[1]

    extracted_data = state.get("extracted_data", {})
    extracted_data.update({
        "summary": summary,
        "metrics": {
            "income":       round(income, 2),
            "expenses":     round(expenses, 2),
            "savings":      round(savings, 2),
            "savings_rate": round(savings_rate, 1),
            "top_expense":  top_expense,
            "currency":     state.get("currency", "USD"),
        }
    })
    print(f"Analytics: income={income:.0f} expenses={expenses:.0f} savings={savings:.0f} rate={savings_rate:.1f}%")
    return {"extracted_data": extracted_data}


def advisory_node(state: GraphState) -> GraphState:
    print("Executing: advisory_node")
    pref    = state.get("user_preference", "buffett")
    data    = state.get("extracted_data", {})
    summary = data.get("summary", {})
    metrics = data.get("metrics", {})
    critique_feedback = state.get("critique_feedback", "")
    revision = state.get("revision_count", 0)

    # Build a rich human message with full context
    summary_lines = "\n".join(
        f"  {cat}: ${amt:+,.2f}" for cat, amt in sorted(summary.items())
    )
    human_msg = f"""TRANSACTION SUMMARY (period totals):
{summary_lines}

KEY METRICS:
  Total Income:    ${metrics.get('income', 0):,.2f}
  Total Expenses:  ${metrics.get('expenses', 0):,.2f}
  Net Savings:     ${metrics.get('savings', 0):,.2f}
  Savings Rate:    {metrics.get('savings_rate', 0):.1f}%
  Top Expense:     {metrics.get('top_expense', 'N/A')}
"""
    if critique_feedback and revision > 0:
        human_msg += f"\nCRITIQUE FROM PREVIOUS DRAFT (revision {revision}):\n{critique_feedback}\nAddress all critique points in this revision."

    system_prompt = PERSONA_PROMPTS.get(pref, PERSONA_PROMPTS["buffett"])
    knowledge_context = state.get("knowledge_context", "")
    if knowledge_context:
        system_prompt += f"\n\nAdditionally, incorporate these financial principles extracted from the user's uploaded book/article into your advice:\n{knowledge_context}"

    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{context}")
        ])
        chain  = prompt | llm
        result = chain.invoke({"context": human_msg})
        report = result.content.strip()
        print(f"Advisory generated ({len(report)} chars, revision {revision})")
    except Exception as e:
        print(f"[Advisory] LLM error ({type(e).__name__}: {e}), using rule-based fallback.")
        report = _rule_based_report(pref, summary, metrics)

    return {"advisory_report": report}


def critique_node(state: GraphState) -> GraphState:
    print("Executing: critique_node")
    pref   = state.get("user_preference", "buffett")
    report = state.get("advisory_report", "")

    critique_system = f"""You are a senior financial editorial director at a top-tier wealth management firm.
Your job: evaluate whether this advisory report meets publication standards.

Evaluation criteria (score each 1–5):
1. Persona fidelity — does it sound authentically like {pref}?
2. Specificity — does it use the actual numbers provided, not generic statements?
3. Actionability — are the recommendations concrete and immediately executable?
4. Structure — are all required sections present and well-formed?
5. Depth — does it go beyond surface observations to real insights?

Reply with ONLY a valid JSON object in this exact format:
{{"is_flawed": true/false, "score": 1-25, "feedback": "specific critique if flawed, or PASS if score >= 20"}}

A report is flawed if score < 20. Be rigorous."""

    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", critique_system),
            ("human", "Report to evaluate:\n\n{report}")
        ])
        chain    = prompt | llm
        response = chain.invoke({"report": report})
        raw      = response.content.strip()

        match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
        if match:
            parsed   = json.loads(match.group())
            is_flawed = bool(parsed.get("is_flawed", False))
            score     = parsed.get("score", 20)
            feedback  = parsed.get("feedback", "")
            print(f"Critique: score={score}/25 flawed={is_flawed} | {feedback[:80]}")
        else:
            is_flawed = False
            feedback  = ""
            print("Critique: could not parse JSON — passing report.")
    except Exception as e:
        print(f"[Critique] LLM error ({type(e).__name__}), passing report as-is.")
        is_flawed = False
        feedback  = ""

    return {
        "revision_count":    state.get("revision_count", 0) + 1,
        "is_flawed":         is_flawed,
        "critique_feedback": feedback,
    }


# ==========================================
# 5. Conditional Edges
# ==========================================
MAX_REVISIONS = 2   # allow up to 2 LLM revision passes

def advisory_condition(state: GraphState) -> str:
    count     = state.get("revision_count", 0)
    is_flawed = state.get("is_flawed", False)

    if count >= MAX_REVISIONS:
        print(f"Critique: revision cap reached ({count}). Finalising.")
        return "end"
    if is_flawed:
        print(f"Critique: report flawed, routing back for revision {count + 1}.")
        return "advisory"
    print("Critique: report passed quality gate.")
    return "end"


# ==========================================
# 6. Graph Construction
# ==========================================
workflow = StateGraph(GraphState)

workflow.add_node("extraction", extraction_node)
workflow.add_node("analytics",  analytics_node)
workflow.add_node("advisory",   advisory_node)
workflow.add_node("critique",   critique_node)

workflow.set_entry_point("extraction")
workflow.add_edge("extraction", "analytics")
workflow.add_edge("analytics",  "advisory")
workflow.add_edge("advisory",   "critique")

workflow.add_conditional_edges(
    "critique",
    advisory_condition,
    {"advisory": "advisory", "end": END}
)

orchestrator_graph = workflow.compile(checkpointer=checkpointer)
