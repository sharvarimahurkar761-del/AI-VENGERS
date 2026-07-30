import { useState } from 'react';
import { Sidebar, MobileNav, type ViewKey } from '@/components/layout/Sidebar';
import { Topbar } from '@/components/layout/Topbar';
import { DashboardView } from '@/components/views/DashboardView';
import { ThinkView } from '@/components/views/ThinkView';
import { CustomersView } from '@/components/views/CustomersView';
import { OutcomesView } from '@/components/views/OutcomesView';
import { HealthView } from '@/components/views/HealthView';
import { NeuralView } from '@/components/views/NeuralView';
import { ReinforcementView } from '@/components/views/ReinforcementView';

const META: Record<ViewKey, { title: string; subtitle: string }> = {
  dashboard: { title: 'Overview', subtitle: 'Customer intelligence across your book of business' },
  think: { title: 'See the AI Think', subtitle: 'Watch the orchestrator reason across three subsystems' },
  customers: { title: 'Customers', subtitle: 'Every account, scored for churn risk and explained' },
  outcomes: { title: 'Feedback Loop', subtitle: 'Outcomes, root-cause aggregation, and policy retraining' },
  health: { title: 'System Health', subtitle: 'Subsystem status, endpoints, and mock/live configuration' },
  neural: { title: 'Neural Network', subtitle: 'Neural network policy visualization' },
  reinforcement: { title: 'Reinforcement Learning', subtitle: 'Learned from 2,400 past interventions' },
};

function App() {
  const [view, setView] = useState<ViewKey>('dashboard');
  const [analyzeId, setAnalyzeId] = useState<string | undefined>(undefined);
  const [busy, setBusy] = useState(false);

  function navigate(v: ViewKey) {
    setView(v);
  }

  function analyzeCustomer(id: string) {
    setAnalyzeId(id);
    setView('think');
  }

  const meta = META[view];

  return (
    <div className="flex min-h-screen w-full bg-ink-950">
      {/* Ambient background glow */}
      <div className="pointer-events-none fixed inset-0 z-0">
        <div className="absolute left-1/4 top-0 h-[400px] w-[600px] rounded-full bg-pulse-600/10 blur-[120px]" />
        <div className="absolute bottom-0 right-1/4 h-[300px] w-[500px] rounded-full bg-violet-600/5 blur-[120px]" />
      </div>

      <Sidebar view={view} onNavigate={navigate} />

      <div className="relative z-10 flex min-w-0 flex-1 flex-col">
        <MobileNav view={view} onNavigate={navigate} />
        <div className="w-full flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <Topbar title={meta.title} subtitle={meta.subtitle} busy={busy} />
          <main className="mt-6">
            {view === 'dashboard' && <DashboardView onNavigate={navigate} />}
            {view === 'think' && <ThinkView initialCustomerId={analyzeId} />}
            {view === 'customers' && (
              <CustomersView onNavigate={navigate} onAnalyze={analyzeCustomer} />
            )}
            {view === 'outcomes' && <OutcomesView />}
            {view === 'health' && <HealthView />}
            {view === 'neural' && <NeuralView />}
            {view === 'reinforcement' && <ReinforcementView />}
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;
