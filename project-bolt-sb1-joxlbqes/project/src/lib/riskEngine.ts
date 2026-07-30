import type { Attribution, Customer, RiskBand, RiskScoreResponse } from './types';
import { findCustomer } from './customers';

// ---- P1 — Risk & Behavior Engine (mock) ----
// Real implementation: PyTorch churn model + SHAP. Mock reproduces the
// published schema: GET /risk/score/{user_id} → {risk_score, attributions[],
// model_version, timestamp}.

export const RISK_MODEL_VERSION = 'churn-xgb-v2.4.1';

// Feature metadata: label + which signals feed it + base weight.
interface FeatureSpec {
  feature: string;
  label: string;
  // map a customer signal key -> weight in this feature
  from: { key: string; weight: number }[];
  // when the composite signal is HIGH, this feature INCREASES risk
  highIncreasesRisk: boolean;
}

const FEATURE_SPECS: FeatureSpec[] = [
  {
    feature: 'onboarding_confusion',
    label: 'Onboarding confusion',
    from: [
      { key: 'onboarding_progress', weight: 0.7 },
      { key: 'feature_adoption', weight: 0.3 },
    ],
    highIncreasesRisk: true,
  },
  {
    feature: 'repeated_failures',
    label: 'Repeated failures',
    from: [
      { key: 'support_tickets', weight: 0.65 },
      { key: 'login_frequency', weight: 0.35 },
    ],
    highIncreasesRisk: true,
  },
  {
    feature: 'pricing_concern',
    label: 'Pricing concern',
    from: [
      { key: 'billing_anomaly', weight: 0.6 },
      { key: 'feature_adoption', weight: 0.4 },
    ],
    highIncreasesRisk: true,
  },
  {
    feature: 'sentiment_decline',
    label: 'Sentiment decline',
    from: [
      { key: 'sentiment_score', weight: 0.8 },
      { key: 'support_tickets', weight: 0.2 },
    ],
    highIncreasesRisk: false, // high sentiment score DECREASES risk
  },
  {
    feature: 'engagement_drop',
    label: 'Engagement drop',
    from: [
      { key: 'login_frequency', weight: 0.55 },
      { key: 'feature_adoption', weight: 0.45 },
    ],
    highIncreasesRisk: true,
  },
];

function clamp(n: number, min = 0, max = 1) {
  return Math.max(min, Math.min(max, n));
}

function band(score: number): RiskBand {
  if (score >= 0.75) return 'critical';
  if (score >= 0.55) return 'high';
  if (score >= 0.35) return 'moderate';
  return 'low';
}

export async function getRiskScore(userId: string): Promise<RiskScoreResponse> {
  const customer = findCustomer(userId);
  if (!customer) throw new Error(`unknown user ${userId}`);

  // Map our UI signals to the SHAP endpoint schema
  const sig = Object.fromEntries(customer.signals.map((s) => [s.key, s.value]));
  
  // Create a plausible RiskRequest from the customer signals
  const requestBody = {
    usage_decline: 1 - (sig['login_frequency'] ?? 0.5),
    tickets_last30: Math.round((sig['support_tickets'] ?? 0) * 10),
    negative_sentiment: 1 - (sig['sentiment_score'] ?? 0.5),
    feature_dropout: 1 - (sig['feature_adoption'] ?? 0.5),
    active_days: Math.round((sig['login_frequency'] ?? 0.5) * 30),
    support_delay: (sig['support_tickets'] ?? 0) * 24,
    payment_delay: (sig['billing_anomaly'] ?? 0) * 30,
  };

  try {
    const res = await fetch('http://localhost:8000/shap/risk/score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });

    if (!res.ok) throw new Error(`SHAP API returned ${res.status}`);
    
    const data = await res.json();
    
    // Map SHAP response format to our frontend RiskScoreResponse
    const rawAttributions = data.attributions || [];
    const totalAbs = rawAttributions.reduce((s: number, a: any) => s + Math.abs(a.impact), 0) || 1;
    
    const attributions: Attribution[] = rawAttributions.map((a: any) => ({
      feature: a.feature,
      label: a.feature.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()),
      value: a.impact,
      contribution: +(Math.abs(a.impact) / totalAbs).toFixed(3),
      direction: a.impact >= 0 ? 'increases' : 'decreases',
    }));
    
    attributions.sort((a, b) => Math.abs(b.value) - Math.abs(a.value));

    return {
      user_id: userId,
      risk_score: +(data.risk_score || 0).toFixed(3),
      risk_band: band(data.risk_score || 0),
      attributions,
      model_version: data.model_version || RISK_MODEL_VERSION,
      timestamp: data.timestamp || new Date().toISOString(),
    };
  } catch (err) {
    console.error("Failed to call SHAP API:", err);
    // Fallback to avoid breaking UI if server isn't running
    return {
      user_id: userId,
      risk_score: 0.5,
      risk_band: 'moderate',
      attributions: [{ feature: 'api_error', label: 'API Unavailable', value: 0.5, contribution: 1, direction: 'increases' }],
      model_version: "unknown",
      timestamp: new Date().toISOString(),
    };
  }
}

function computeRawFeatureValues(customer: Customer): Record<string, number> {
  const sig = Object.fromEntries(customer.signals.map((s) => [s.key, s.value]));
  const out: Record<string, number> = {};
  for (const spec of FEATURE_SPECS) {
    let v = 0;
    for (const src of spec.from) v += (sig[src.key] ?? 0) * src.weight;
    out[spec.feature] = clamp(v);
  }
  return out;
}

export function topAttribution(resp: RiskScoreResponse): Attribution {
  return resp.attributions[0];
}

function delay(ms: number, jitter = 0) {
  const wait = ms + Math.random() * jitter;
  return new Promise<void>((r) => setTimeout(r, wait));
}
