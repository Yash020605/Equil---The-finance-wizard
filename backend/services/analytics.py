import json
import pandas as pd
import numpy as np
from langchain_core.tools import tool

@tool
def categorize_and_detect_anomalies(transactions_json: str) -> str:
    """
    Parses transactions, categorizes them into smart buckets (Investment, Essential Living, Discretionary),
    and flags anomalies based on unusual spending spikes using statistical deviation logic.
    """
    print("[Analytics Engine] Categorizing transactions and detecting anomalies...")
    try:
        # In a real scenario, we would parse transactions_json and build a pandas DataFrame
        # df = pd.DataFrame(json.loads(transactions_json))
        # df['category'] = df['description'].apply(categorization_model)
        # anomalies = df[df['amount'] > df['amount'].mean() + 2 * df['amount'].std()]
        
        # Mocking the statistical detection and categorization
        result = {
            "categories": {
                "Essential Living": 1500.0,
                "Discretionary Spend": 450.0,
                "Investment": 500.0
            },
            "anomalies_flagged": [
                {
                    "date": "2024-05-15", 
                    "amount": 400.0, 
                    "vendor": "Apple Store", 
                    "reason": "Sudden spike in discretionary spending; 3x above baseline."
                }
            ]
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error in categorization: {str(e)}"

@tool
def calculate_financial_health_and_predict(transactions_json: str, balances_json: str = "{}") -> str:
    """
    Calculates Financial Health Score (0-100) based on savings rate and debt-to-income indicators.
    Models/projects spending and savings trajectories 3 to 6 months into the future.
    """
    print("[Analytics Engine] Scoring financial health and forecasting models...")
    # Mocking advanced pandas/numpy projections
    # Future projection = current_trend * time_factor
    
    result = {
        "health_score": 78,
        "metrics": {
            "savings_rate": "20.4%",
            "debt_to_income": "32.1%"
        },
        "predictions_3_months": {
            "projected_savings_accrued": 1500.0,
            "projected_discretionary_burn": 1350.0
        }
    }
    return json.dumps(result, indent=2)

@tool
def track_financial_goals(cash_flow_trends_json: str, goals_json: str) -> str:
    """
    Maps current cash flow trends against user-defined goals (e.g., International Studies, Tech Hardware).
    Outputs actionable timelines based on trajectory data.
    """
    print("[Analytics Engine] Tracking milestones and projecting goal completion timelines...")
    
    result = [
        {
            "goal": "International Studies Corpus",
            "target": 20000,
            "status": "On Track",
            "timeline": "At current savings rates, your goal will be achieved in 14 months."
        },
        {
            "goal": "Tech Hardware Upgrade",
            "target": 2500,
            "status": "Accelerated",
            "timeline": "At current savings rates, your goal will be achieved in 2 months."
        }
    ]
    return json.dumps(result, indent=2)


# Expose analytics capabilities for the LangGraph orchestrator
ANALYTICS_TOOLS = [categorize_and_detect_anomalies, calculate_financial_health_and_predict, track_financial_goals]
