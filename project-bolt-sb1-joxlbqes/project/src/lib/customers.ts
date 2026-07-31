import type { Customer, CustomerSignal } from './types';

// Deterministic pseudo-random per id so risk scores are stable across reloads.
function hash(str: string): number {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0) / 4294967295;
}

const tiers: Customer['tier'][] = ['Starter', 'Growth', 'Enterprise'];

function signal(key: string, label: string, raw: number, display: string): CustomerSignal {
  return { key, label, value: Math.max(0, Math.min(1, raw)), display };
}

function buildSignals(id: string): CustomerSignal[] {
  const r = hash(id);
  const r2 = hash(id + 'x');
  const r3 = hash(id + 'y');
  const r4 = hash(id + 'z');
  const r5 = hash(id + 'w');
  const r6 = hash(id + 'q');
  const loginDrop = Math.round(r * 60);
  const tickets = Math.round(r2 * 8);
  const sentiment = +(0.2 + r3 * 0.8).toFixed(2);
  const featureUse = Math.round((1 - r4) * 100);
  const billingFlag = r5 > 0.78 ? 1 : 0;
  const onboardingSteps = Math.round((1 - r6) * 6);
  return [
    signal('login_frequency', 'Login frequency', 1 - r, `${60 - loginDrop}% vs 30d`),
    signal('support_tickets', 'Support tickets', r2, `${tickets} open`),
    signal('sentiment_score', 'Sentiment score', sentiment, `${sentiment.toFixed(2)}`),
    signal('feature_adoption', 'Feature adoption', 1 - r4, `${featureUse}%`),
    signal('billing_anomaly', 'Billing anomaly', billingFlag, billingFlag ? 'flagged' : 'clean'),
    signal('onboarding_progress', 'Onboarding progress', 1 - onboardingSteps / 6, `${onboardingSteps}/6 steps`),
  ];
}

export const customers: Customer[] = [
  ['c_001', 'Maya Chen', 'Northwind Robotics', 'maya@northwind.io'],
  ['c_002', 'Diego Alvarez', 'Lumen Health', 'diego@lumenhealth.com'],
  ['c_003', 'Priya Nair', 'Atlas Freight', 'priya@atlasfreight.co'],
  ['c_004', 'Sam Okafor', 'Brightwave Media', 'sam@brightwave.tv'],
  ['c_005', 'Hana Kobayashi', 'Vertex Labs', 'hana@vertexlabs.ai'],
  ['c_006', 'Lucas Pereira', 'Cedar & Co', 'lucas@cedarco.com'],
  ['c_007', 'Aaliyah Brooks', 'Skyline Energy', 'aaliyah@skyline.energy'],
  ['c_008', 'Theo Müller', 'Quantum Gear', 'theo@quantumgear.de'],
  ['c_009', 'Ines Garcia', 'Harbor Pay', 'ines@harborpay.io'],
  ['c_010', 'Ravi Shankar', 'Nimbus Cloud', 'ravi@nimbus.cloud'],
  ['c_011', 'Greta Lindholm', 'Polar Foods', 'greta@polarfoods.se'],
  ['c_012', 'Omar Haddad', 'Sable Logistics', 'omar@sablelog.com'],
].map(([id, name, company, email]) => {
  const r = hash(id + 'tier');
  const tier = tiers[Math.floor(r * 3)];
  const planValue = tier === 'Enterprise' ? 12000 : tier === 'Growth' ? 4500 : 990;
  return {
    id,
    name,
    company,
    email: email as string,
    tier,
    plan_value: planValue,
    avatarHue: Math.floor(hash(id + 'hue') * 280),
    signals: buildSignals(id),
    joinedDays: 40 + Math.floor(hash(id + 'j') * 700),
    lastActiveDays: Math.floor(hash(id + 'a') * 12),
  } as Customer;
});

export function findCustomer(id: string): Customer | undefined {
  return customers.find((c) => c.id === id);
}
