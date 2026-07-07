export interface Anomaly {
  transaction: string;
  amount: number;
  reason: string;
}

export interface FinancialHealth {
  score: number;
  savings_rate: number;
  debt_to_income: number;
  burn_rate_days: number;
}

export interface AnalyticsBundle {
  category_totals: Record<string, number>;
  anomalies: Anomaly[];
  health_score: FinancialHealth;
  cash_flow_projection: Record<string, number>;
}

export interface BackendResponse {
  status: string;
  message: string;
  multi_guru_advice: string;
  analytics_bundle: AnalyticsBundle;
}
