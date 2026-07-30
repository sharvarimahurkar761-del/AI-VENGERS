import type { KnowledgeRequest, KnowledgeResponse, RetrievedDoc } from './types';

// ---- P2 — Knowledge Assistant (mock) ----
// Real implementation: RAG + fine-tuned LLM (LoRA/QLoRA) grounded in company
// docs. Mock reproduces the published schema:
// POST /knowledge/respond → {retrieved_docs[], grounded_response, confidence, model_version}.

export const KNOWLEDGE_MODEL_VERSION = 'pulse-llm-lora-v0.9.3';

interface DocEntry {
  id: string;
  title: string;
  source: string;
  body: string;
  // keywords that make this doc relevant to a root cause
  triggers: string[];
}

const CORPUS: DocEntry[] = [
  {
    id: 'doc_onboarding',
    title: 'Guided onboarding playbook',
    source: 'Success Ops Wiki / Onboarding',
    triggers: ['onboarding_confusion'],
    body: 'Customers who complete fewer than 3 of 6 onboarding steps within 14 days show 3.2x higher churn. The playbook prescribes a guided tutorial surfaced in-app on day 4 if progress stalls, plus a personalized kickoff call for Enterprise tier.',
  },
  {
    id: 'doc_tutorial_steps',
    title: 'Feature walkthrough: first 3 wins',
    source: 'Product Docs / Tutorials',
    triggers: ['onboarding_confusion', 'engagement_drop'],
    body: 'The "first 3 wins" walkthrough walks a new user through creating a project, inviting a teammate, and publishing a report. Completion correlates with 90-day retention +28%.',
  },
  {
    id: 'doc_support_escalation',
    title: 'Support escalation & human handoff policy',
    source: 'CS Handbook / Escalation',
    triggers: ['repeated_failures'],
    body: 'A customer with 3+ unresolved tickets in 14 days, or any P1 incident, must be escalated to a named CSM within one business day. Do not auto-resolve; schedule a live review.',
  },
  {
    id: 'doc_failures_rootcause',
    title: 'Common repeated-failure root causes',
    source: 'CS Handbook / Diagnostics',
    triggers: ['repeated_failures'],
    body: 'Repeated failures most often stem from misconfigured integrations (42%) or rate-limit misunderstanding (23%). A live session resolves 71% of these cases versus 19% for async nudge.',
  },
  {
    id: 'doc_pricing_plans',
    title: 'Plan comparison & downgrade guardrails',
    source: 'Pricing / Plans',
    triggers: ['pricing_concern'],
    body: 'Downgrade intent is frequently driven by underused seats. The incentive playbook offers a 15% loyalty credit or a tier-matched seat reduction before allowing a full downgrade.',
  },
  {
    id: 'doc_incentive_policy',
    title: 'Retention incentive authority matrix',
    source: 'Finance / Retention',
    triggers: ['pricing_concern'],
    body: 'CSMs may issue up to 15% loyalty credit on Growth and 10% on Enterprise without VP approval. Credits apply to the next renewal and require a 12-month commitment.',
  },
  {
    id: 'doc_sentiment_playbook',
    title: 'Sentiment recovery playbook',
    source: 'Success Ops Wiki / Sentiment',
    triggers: ['sentiment_decline'],
    body: 'When sentiment drops below 0.4, send a proactive check-in from the CSM within 48h. Pair with a short roadmap share to rebuild confidence. Avoid scripted nudges.',
  },
  {
    id: 'doc_nudge_templates',
    title: 'Proactive nudge templates',
    source: 'Lifecycle / Nudges',
    triggers: ['engagement_drop', 'sentiment_decline'],
    body: 'Proactive nudges work best when tied to a specific dormant feature and sent within 5 days of inactivity. Keep them to one CTA. Over-nudging (>3/week) increases unsubscribe risk.',
  },
  {
    id: 'doc_engagement_signals',
    title: 'Engagement signal thresholds',
    source: 'Data / Signal Catalog',
    triggers: ['engagement_drop'],
    body: 'Login frequency below 0.4 of the 30-day baseline, or feature adoption below 30%, triggers an engagement_drop signal. Both must persist for 7 days to be actionable.',
  },
];

function highlightTerms(text: string, terms: string[]): string[] {
  const found: string[] = [];
  const lower = text.toLowerCase();
  for (const t of terms) {
    const word = t.split('_')[0];
    if (lower.includes(word)) found.push(word);
  }
  return [...new Set(found)].slice(0, 4);
}

export async function knowledgeRespond(req: KnowledgeRequest): Promise<KnowledgeResponse> {
  await delay(520, 160);
  const query = req.query.toLowerCase();
  const topK = req.top_k ?? 3;

  // Score docs by trigger match + keyword overlap with the query
  const scored = CORPUS.map((d) => {
    let score = 0;
    for (const t of d.triggers) if (query.includes(t)) score += 0.5;
    const words = query.split(/[\s_]+/).filter((w) => w.length > 3);
    for (const w of words) if (d.body.toLowerCase().includes(w)) score += 0.12;
    if (query.includes('onboard') && d.triggers.includes('onboarding_confusion')) score += 0.4;
    if (query.includes('fail') && d.triggers.includes('repeated_failures')) score += 0.4;
    if (query.includes('pric') && d.triggers.includes('pricing_concern')) score += 0.4;
    if (query.includes('sentiment') && d.triggers.includes('sentiment_decline')) score += 0.4;
    if (query.includes('engag') && d.triggers.includes('engagement_drop')) score += 0.4;
    return { d, score: Math.min(1, score) };
  })
    .filter((s) => s.score > 0.05)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);

  const retrieved_docs: RetrievedDoc[] = scored.map((s, i) => ({
    id: s.d.id,
    title: s.d.title,
    source: s.d.source,
    snippet: s.d.body,
    relevance: +s.score.toFixed(2),
    highlights: highlightTerms(s.d.body, s.d.triggers),
  }));

  const confidence = retrieved_docs.length
    ? +Math.min(0.97, 0.55 + retrieved_docs[0].relevance * 0.4).toFixed(2)
    : 0.3;

  const grounded_response = composeResponse(req.query, retrieved_docs);

  return {
    retrieved_docs,
    grounded_response,
    confidence,
    model_version: KNOWLEDGE_MODEL_VERSION,
  };
}

function composeResponse(query: string, docs: RetrievedDoc[]): string {
  if (!docs.length) {
    return `No grounded documentation matched "${query}". I'd recommend a human review before taking action.`;
  }
  const top = docs[0];
  const actionMap: Record<string, string> = {
    doc_onboarding:
      'Surface the guided "first 3 wins" tutorial in-app and, for Enterprise tier, schedule a personalized kickoff call within 48 hours.',
    doc_tutorial_steps:
      'Trigger the in-app "first 3 wins" walkthrough focused on the three highest-retention actions.',
    doc_support_escalation:
      'Escalate to a named CSM within one business day. Do not auto-resolve — schedule a live review of the open tickets.',
    doc_failures_rootcause:
      'Book a live session to diagnose the likely integration misconfiguration or rate-limit misunderstanding; async nudges underperform here.',
    doc_pricing_plans:
      'Offer a 15% loyalty credit (Growth) or tier-matched seat reduction before allowing a full downgrade, gated on a 12-month commitment.',
    doc_incentive_policy:
      'Issue a retention credit within CSM authority (15% Growth / 10% Enterprise) tied to a 12-month renewal commitment.',
    doc_sentiment_playbook:
      'Send a proactive CSM check-in within 48h paired with a short roadmap share. Avoid scripted nudges.',
    doc_nudge_templates:
      'Send one proactive nudge tied to the specific dormant feature within 5 days of inactivity. One CTA only.',
    doc_engagement_signals:
      'Confirm the engagement drop has persisted 7 days, then send a single feature-tied proactive nudge.',
  };
  const rec = actionMap[top.id] ?? 'Review the top retrieved document with the responsible CSM.';
  return `Based on "${top.title}" (${top.source}), ${rec} This is grounded in our success documentation with ${Math.round(
    top.relevance * 100
  )}% retrieval confidence.`;
}

function delay(ms: number, jitter = 0) {
  const wait = ms + Math.random() * jitter;
  return new Promise<void>((r) => setTimeout(r, wait));
}
