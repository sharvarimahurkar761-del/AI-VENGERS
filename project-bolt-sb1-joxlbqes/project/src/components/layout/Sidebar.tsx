import { Activity, LayoutDashboard, Users, Repeat, HeartPulse, Brain, Network, Target } from 'lucide-react';
import { cn } from '@/lib/cn';

export type ViewKey = 'dashboard' | 'think' | 'customers' | 'outcomes' | 'health' | 'neural' | 'reinforcement';

const NAV: { key: ViewKey; label: string; icon: typeof Activity; hint: string }[] = [
  { key: 'dashboard', label: 'Overview', icon: LayoutDashboard, hint: 'KPIs & risk mix' },
  { key: 'think', label: 'See the AI Think', icon: Brain, hint: 'Live analysis' },
  { key: 'customers', label: 'Customers', icon: Users, hint: 'At-risk roster' },
  { key: 'outcomes', label: 'Feedback Loop', icon: Repeat, hint: 'Outcomes & retrain' },
  { key: 'health', label: 'System Health', icon: HeartPulse, hint: 'Service status' },
  { key: 'neural', label: 'Neural', icon: Network, hint: 'RL Policy' },
  { key: 'reinforcement', label: 'Reinforcement', icon: Target, hint: 'RL Policy' },
];

export function Sidebar({
  view,
  onNavigate,
}: {
  view: ViewKey;
  onNavigate: (v: ViewKey) => void;
}) {
  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-white/5 bg-ink-950/80 px-3 py-5 lg:flex">
      <div className="flex items-center gap-2.5 px-3">
        <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-pulse-400 to-pulse-600 shadow-[0_0_22px_-4px_rgba(34,211,238,0.8)]">
          <Activity size={18} className="text-ink-950" />
          <span className="absolute inset-0 rounded-xl animate-pulseGlow" />
        </div>
        <div className="leading-tight">
          <div className="font-display text-base font-semibold text-slate-50">PulseIQ</div>
          <div className="text-[10px] uppercase tracking-[0.18em] text-pulse-400/70">Frontier 2026</div>
        </div>
      </div>

      <nav className="mt-7 flex flex-1 flex-col gap-1">
        {NAV.map((item) => {
          const active = view === item.key;
          const Icon = item.icon;
          return (
            <button
              key={item.key}
              onClick={() => onNavigate(item.key)}
              className={cn(
                'group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-left transition-all',
                active ? 'bg-pulse-500/10 text-slate-50' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
              )}
            >
              {active && (
                <span className="absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-pulse-400" />
              )}
              <Icon size={18} className={active ? 'text-pulse-300' : 'text-slate-500 group-hover:text-slate-300'} />
              <div className="flex flex-col">
                <span className="text-sm font-medium">{item.label}</span>
                <span className="text-[10px] text-slate-500">{item.hint}</span>
              </div>
            </button>
          );
        })}
      </nav>

      <div className="mt-3 rounded-xl border border-white/5 bg-ink-900/60 p-3">
        <div className="flex items-center gap-2 text-[11px] text-slate-400">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
          Orchestrator online
        </div>
        <div className="mt-1.5 text-[10px] text-slate-600">3 services · mock mode</div>
      </div>
    </aside>
  );
}

export function MobileNav({ view, onNavigate }: { view: ViewKey; onNavigate: (v: ViewKey) => void }) {
  return (
    <div className="sticky top-0 z-30 flex items-center gap-1 overflow-x-auto border-b border-white/5 bg-ink-950/90 px-2 py-2 backdrop-blur-xl lg:hidden">
      <div className="flex items-center gap-2 px-2">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-pulse-400 to-pulse-600">
          <Activity size={14} className="text-ink-950" />
        </div>
        <span className="font-display text-sm font-semibold text-slate-50">PulseIQ</span>
      </div>
      {NAV.map((item) => {
        const active = view === item.key;
        const Icon = item.icon;
        return (
          <button
            key={item.key}
            onClick={() => onNavigate(item.key)}
            className={cn(
              'flex shrink-0 items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs transition-colors',
              active ? 'bg-pulse-500/15 text-pulse-200' : 'text-slate-400'
            )}
          >
            <Icon size={14} />
            {item.label}
          </button>
        );
      })}
    </div>
  );
}
