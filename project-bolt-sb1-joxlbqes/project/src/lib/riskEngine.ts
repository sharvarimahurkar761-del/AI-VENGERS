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
  await delay(420, 120);
  const customer = findCustomer(userId);
  if (!customer) throw new Error(`unknown user ${userId}`);
  const raw = computeRawFeatureValues(customer);
  // signed SHAP-style values: positive increases risk
  const attributions: Attribution[] = FEATURE_SPECS.map((spec) => {
    const composite = raw[spec.feature];
    const signed = spec.highIncreasesRisk ? composite * 0.9 : -(composite * 0.6);
    return {
      feature: spec.feature,
      label: spec.label,
      value: +signed.toFixed(4),
      contribution: 0,
      direction: signed >= 0 ? 'increases' : 'decreases',
    };
  });
  const totalAbs = attributions.reduce((s, a) => s + Math.abs(a.value), 0) || 1;
  attributions.forEach((a) => (a.contribution = +(Math.abs(a.value) / totalAbs).toFixed(3)));
  const risk = clamp(0.18 + attributions.reduce((s, a) => s + Math.max(0, a.value), 0));
  attributions.sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
  return {
    user_id: userId,
    risk_score: +risk.toFixed(3),
    risk_band: band(risk),
    attributions,
    model_version: RISK_MODEL_VERSION,
    timestamp: new Date().toISOString(),
  };
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
