import { useState } from 'react';
import { Cpu, Gauge, FileText, Server, Zap, Activity, ToggleLeft, ToggleRight, Check, AlertTriangle } from 'lucide-react';
import { RISK_MODEL_VERSION } from '@/lib/riskEngine';
import { KNOWLEDGE_MODEL_VERSION } from '@/lib/knowledgeAssistant';
import { POLICY_MODEL_VERSION } from '@/lib/actionPolicy';
import { Card, SectionTitle } from '@/components/ui/Card';

interface ServiceStatus {
  key: string;
  name: string;
  endpoint: string;
  method: string;
  model: string;
  latencyMs: number;
  healthy: boolean;
  mode: 'mock' | 'live';
  icon: typeof Gauge;
  accent: string;
  desc: string;
}

const SERVICES: ServiceStatus[] = [
  {
    key: 'risk',
    name: 'Risk & Behavior Engine',
    endpoint: '/risk/score/{user_id}',
    method: 'GET',
    model: RISK_MODEL_VERSION,
    latencyMs: 420,
    healthy: true,
    mode: 'mock',
    icon: Gauge,
    accent: 'text-pulse-300',
    desc: 'PyTorch churn model + SHAP explainability. Scores 0..1 risk and returns signed attributions.',
  },
  {
    key: 'knowledge',
    name: 'Knowledge Assistant',
    endpoint: '/knowledge/respond',
    method: 'POST',
    model: KNOWLEDGE_MODEL_VERSION,
    latencyMs: 520,
    healthy: true,
    mode: 'mock',
    icon: FileText,
    accent: 'text-sky-300',
    desc: 'RAG + fine-tuned LLM (LoRA/QLoRA). Grounds responses in company docs with retrieval confidence.',
  },
  {
    key: 'policy',
    name: 'Action Policy & Feedback Loop',
    endpoint: '/policy/decide · /policy/outcome · /policy/retrain · /policy/aggregate',
    method: 'POST/GET',
    model: POLICY_MODEL_VERSION,
    latencyMs: 360,
    healthy: true,
    mode: 'live',
    icon: Cpu,
    accent: 'text-emerald-300',
    desc: 'Picks 1 of 4 actions from the dominant risk driver. Logs outcomes, retrains, aggregates root causes.',
  },
  {
    key: 'orchestrator',
    name: 'Application Orchestrator',
    endpoint: '/analyze (internal)',
    method: '—',
    model: 'orchestrator v0.4',
    latencyMs: 1300,
    healthy: true,
    mode: 'live',
    icon: Server,
    accent: 'text-violet-300',
    desc: 'FastAPI backend sequencing P1 → P2 → P3 → persistence and exposing results to the dashboard.',
  },
];

export function HealthView() {
  const [modes, setModes] = useState<Record<string, 'mock' | 'live'>>(
    Object.fromEntries(SERVICES.map((s) => [s.key, s.mode]))
  );

  function toggle(key: string) {
    setModes((m) => ({ ...m, [key]: m[key] === 'mock' ? 'live' : 'mock' }));
  }

  return (
    <div className="space-y-6">
      <SectionTitle
        eyebrow="System health"
        title="Subsystem status & endpoint map"
        desc="PulseIQ is three subsystems plus an orchestration layer. Mock/live toggles show how the frontend swaps endpoints with no interface changes."
      />

      {/* Architecture diagram */}
      <Card className="relative overflow-hidden p-6">
        <div className="absolute inset-0 grid-bg opacity-40" />
        <div className="relative">
          <h3 className="mb-1 flex items-center gap-2 font-display text-base font-semibold text-slate-100">
            <Activity size={16} className="text-pulse-300" /> Request flow
          </h3>
          <p className="text-xs text-slate-500">How a single customer analysis flows through the platform</p>

          <div className="mt-6 flex flex-col items-stretch gap-4 lg:flex-row lg:items-center">
            <FlowNode label="Customer" sub="selected in dashboard" icon={Server} hue="06b6d4" />
            <FlowArrow />
            <FlowNode label="Risk Engine" sub="score + SHAP" icon={Gauge} hue="06b6d4" tag="P1" />
            <FlowArrow />
            <FlowNode label="Knowledge" sub="RAG retrieval" icon={FileText} hue="0ea5e9" tag="P2" />
            <FlowArrow />
            <FlowNode label="Action Policy" sub="decide + log" icon={Cpu} hue="10b981" tag="P3" />
            <FlowArrow />
            <FlowNode label="Feedback Loop" sub="outcome → retrain" icon={Activity} hue="8b5cf6" />
          </div>
        </div>
      </Card>

      {/* Service cards */}
      <div className="grid gap-4 md:grid-cols-2">
        {SERVICES.map((s, i) => {
          const Icon = s.icon;
          const mode = modes[s.key];
          return (
            <Card key={s.key} className="relative overflow-hidden p-5 animate-fadeUp" >
              <div className="pointer-events-none absolute -right-10 -top-10 h-28 w-28 rounded-full bg-pulse-500/5 blur-2xl" />
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/5 bg-white/[0.03]">
                    <Icon size={18} className={s.accent} />
                  </div>
                  <div>
                    <h4 className="font-display text-sm font-semibold text-slate-100">{s.name}</h4>
                    <div className="mt-0.5 flex items-center gap-2 text-[11px] text-slate-500">
                      <span className="font-mono">{s.model}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="flex items-center gap-1 text-[11px] text-emerald-300">
                    <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" /> healthy
                  </span>
                </div>
              </div>

              <p className="mt-3 text-xs leading-relaxed text-slate-400">{s.desc}</p>

              <div className="mt-4 space-y-2 rounded-xl border border-white/5 bg-white/[0.02] p-3 font-mono text-[11px]">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">endpoint</span>
                  <span className="text-pulse-200">{s.endpoint}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">method</span>
                  <span className="text-slate-300">{s.method}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">p50 latency</span>
                  <span className="flex items-center gap-1 text-slate-300"><Zap size={10} className="text-amber-300" /> {s.latencyMs}ms</span>
                </div>
              </div>

              <div className="mt-4 flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs">
                  {mode === 'live' ? (
                    <span className="flex items-center gap-1.5 text-emerald-300"><Check size={13} /> Live endpoint</span>
                  ) : (
                    <span className="flex items-center gap-1.5 text-amber-300"><AlertTriangle size={13} /> Mock (schema-matched)</span>
                  )}
                </div>
                <button
                  onClick={() => toggle(s.key)}
                  className="flex items-center gap-1.5 text-xs text-slate-400 transition hover:text-slate-200"
                >
                  {mode === 'live' ? <ToggleRight size={22} className="text-emerald-400" /> : <ToggleLeft size={22} className="text-slate-500" />}
                </button>
              </div>
            </Card>
          );
        })}
      </div>

      <Card className="p-5">
        <h3 className="font-display text-base font-semibold text-slate-100">Integration notes</h3>
        <ul className="mt-3 space-y-2.5 text-sm text-slate-400">
          <li className="flex gap-2"><span className="text-pulse-400">•</span> P1 and P2 are mocked against their published schemas. Swapping to live endpoints requires only changing the base URL in the service modules — no interface changes.</li>
          <li className="flex gap-2"><span className="text-pulse-400">•</span> P3 (action policy) is the real, tested FastAPI service. It already runs against mocked P1/P2 outputs and is ready to consume live ones.</li>
          <li className="flex gap-2"><span className="text-pulse-400">•</span> The orchestrator sequences P1 → P2 → P3 and persists every decision to the feedback loop so retraining has labeled data.</li>
          <li className="flex gap-2"><span className="text-pulse-400">•</span> Action choice depends on <em>which</em> attribution drove the risk score — same score from <code className="rounded bg-white/5 px-1 text-pulse-200">onboarding_confusion</code> picks a tutorial, from <code className="rounded bg-white/5 px-1 text-pulse-200">repeated_failures</code> picks a human handoff.</li>
        </ul>
      </Card>
    </div>
  );
}

function FlowNode({ label, sub, icon: Icon, hue, tag }: { label: string; sub: string; icon: typeof Gauge; hue: string; tag?: string }) {
  return (
    <div className="relative flex flex-1 items-center gap-3 rounded-xl border border-white/5 bg-ink-900/60 p-3" style={{ boxShadow: `0 0 20px -10px #${hue}` }}>
      {tag && <span className="absolute -left-2 -top-2 rounded-md bg-ink-800 px-1.5 py-0.5 text-[9px] font-semibold text-pulse-300 ring-1 ring-white/10">{tag}</span>}
      <div className="flex h-8 w-8 items-center justify-center rounded-lg" style={{ background: `#${hue}22` }}>
        <Icon size={15} style={{ color: `#${hue}` }} />
      </div>
      <div>
        <div className="text-xs font-medium text-slate-200">{label}</div>
        <div className="text-[10px] text-slate-500">{sub}</div>
      </div>
    </div>
  );
}

function FlowArrow() {
  return (
    <div className="flex shrink-0 items-center justify-center lg:px-1">
      <svg width="28" height="14" viewBox="0 0 28 14" fill="none" className="text-pulse-400/60">
        <path d="M0 7 H22" stroke="currentColor" strokeWidth="1.5" strokeDasharray="3 3" className="animate-dash" />
        <path d="M22 3 L28 7 L22 11 Z" fill="currentColor" />
      </svg>
    </div>
  );
}
