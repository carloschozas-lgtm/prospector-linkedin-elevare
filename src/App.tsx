import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  History, 
  Search, 
  Settings, 
  Bell, 
  ChevronRight, 
  ArrowLeft, 
  HelpCircle, 
  CheckCircle2, 
  Copy, 
  AlertCircle,
  Send,
  Users,
  Rocket,
  Building2,
  Cpu,
  MoreVertical,
  Plus
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { CampaignType, AnalysisResult, HistoryItem, Stats } from './types';
import { analyzeProfile } from './services/geminiService';

// --- Components ---

const NavItem = ({ icon: Icon, label, active, onClick }: { icon: any, label: string, active: boolean, onClick: () => void }) => (
  <button 
    onClick={onClick}
    className={`flex flex-1 flex-col items-center justify-center gap-1 py-2 transition-colors ${active ? 'text-primary' : 'text-slate-400 dark:text-slate-500'}`}
  >
    <Icon size={24} className={active ? 'fill-primary/20' : ''} />
    <p className="text-[10px] font-bold uppercase tracking-wider">{label}</p>
  </button>
);

const Header = ({ title, showBack, onBack }: { title: string, showBack?: boolean, onBack?: () => void }) => (
  <header className="sticky top-0 z-10 flex items-center bg-background-light dark:bg-background-dark p-4 border-b border-slate-200 dark:border-slate-800 justify-between">
    <div className="flex size-10 items-center justify-center text-slate-600 dark:text-slate-400">
      {showBack && <button onClick={onBack}><ArrowLeft size={24} /></button>}
    </div>
    <h1 className="text-lg font-bold leading-tight tracking-tight flex-1 text-center font-display">{title}</h1>
    <div className="flex w-10 items-center justify-end">
      <button className="text-slate-600 dark:text-slate-400">
        <HelpCircle size={20} />
      </button>
    </div>
  </header>
);

// --- Pages ---

const Dashboard = ({ onAnalyze }: { onAnalyze: () => void }) => {
  const [stats, setStats] = useState<Stats>({ total: 0, matches: 0, sent: 0 });
  const [recent, setRecent] = useState<HistoryItem[]>([]);

  useEffect(() => {
    fetch('/api/stats').then(res => res.json()).then(setStats);
    fetch('/api/history').then(res => res.json()).then(data => setRecent(data.slice(0, 3)));
  }, []);

  return (
    <div className="space-y-6 p-4 pb-24">
      <section className="space-y-4">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Performance Summary</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2 flex flex-col justify-between rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#192b33] p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-lg bg-blue-500/10 text-blue-500">
                <Users size={20} />
              </div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Total Profiles Analyzed</p>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-3xl font-bold">{stats.total}</span>
              <span className="text-xs font-medium text-emerald-500 flex items-center">
                <ChevronRight size={12} className="-rotate-90" /> 12%
              </span>
            </div>
          </div>
          <div className="flex flex-col justify-between rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#192b33] p-5 shadow-sm">
            <div className="flex items-center gap-2">
              <div className="flex size-8 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-500">
                <CheckCircle2 size={16} />
              </div>
              <p className="text-xs font-medium text-slate-500 dark:text-slate-400">ICP Matches</p>
            </div>
            <p className="mt-3 text-2xl font-bold">{stats.matches}</p>
          </div>
          <div className="flex flex-col justify-between rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#192b33] p-5 shadow-sm">
            <div className="flex items-center gap-2">
              <div className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Send size={16} />
              </div>
              <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Messages Sent</p>
            </div>
            <p className="mt-3 text-2xl font-bold">{stats.sent}</p>
          </div>
        </div>
      </section>

      <section className="pt-4">
        <button 
          onClick={onAnalyze}
          className="w-full flex items-center justify-center gap-2 rounded-xl bg-primary py-4 px-6 text-white font-bold shadow-lg shadow-primary/20 hover:bg-primary/90 transition-colors"
        >
          <Search size={20} />
          Analyze New Profile
        </button>
      </section>

      <section className="space-y-4">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Recent Prospecting</h3>
        <div className="space-y-3">
          {recent.map(item => (
            <div key={item.id} className="flex items-center gap-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#192b33] p-4">
              <div className="size-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                <Users size={24} />
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-bold truncate">{item.name}</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 truncate">{item.role} at {item.company}</p>
              </div>
              <div className="text-right">
                <span className={`inline-flex rounded-full px-2 py-1 text-[10px] font-bold ${item.match_score >= 80 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'}`}>
                  {item.match_score}% Match
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

const Analyzer = ({ onComplete }: { onComplete: () => void }) => {
  const [campaign, setCampaign] = useState<CampaignType>('CRM');
  const [profileData, setProfileData] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const handleAnalyze = async () => {
    if (!profileData.trim()) return;
    setLoading(true);
    try {
      const res = await analyzeProfile(profileData, campaign);
      setResult(res);
      await fetch('/api/history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...res, campaign })
      });
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (result) {
      navigator.clipboard.writeText(result.message);
    }
  };

  return (
    <div className="p-4 pb-24 space-y-6">
      <section className="space-y-4">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Campaña Activa</label>
          <div className="flex gap-2">
            {(['CRM', 'CORFO'] as CampaignType[]).map(c => (
              <button
                key={c}
                onClick={() => setCampaign(c)}
                className={`flex-1 py-2 rounded-lg border text-sm font-bold transition-all ${campaign === c ? 'bg-primary border-primary text-white' : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400'}`}
              >
                {c === 'CRM' ? 'Campaña CRM' : 'Campaña CORFO'}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-slate-700 dark:text-slate-300">LinkedIn Profile Data</label>
          <textarea 
            value={profileData}
            onChange={(e) => setProfileData(e.target.value)}
            className="w-full resize-none rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#192b33] p-4 text-base focus:border-primary focus:ring-1 focus:ring-primary outline-none min-h-[160px]"
            placeholder="Pega aquí la sección 'Acerca de', experiencia o información del perfil..."
          />
        </div>

        <button 
          onClick={handleAnalyze}
          disabled={loading || !profileData.trim()}
          className="w-full flex items-center justify-center gap-2 rounded-xl bg-primary py-4 px-6 text-white font-bold shadow-lg shadow-primary/20 hover:bg-primary/90 transition-colors disabled:opacity-50"
        >
          {loading ? (
            <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
          ) : (
            <>
              <BarChart3 size={20} />
              Analyze Prospect
            </>
          )}
        </button>
      </section>

      {result && (
        <motion.section 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Analysis Results</h3>
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border ${result.match_score >= 80 ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800' : 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800'}`}>
              <CheckCircle2 size={14} className="mr-1" />
              {result.match_score >= 80 ? 'ICP MATCH' : 'POTENTIAL MATCH'}
            </span>
          </div>

          <div className="bg-white dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-2 text-primary">
                <AlertCircle size={20} />
                <h4 className="text-sm font-bold font-display">Detected Pain Point</h4>
              </div>
              <p className="text-slate-700 dark:text-slate-300 text-base leading-relaxed">
                {result.pain_point}
              </p>
            </div>

            <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
              <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-2">Context Summary</h4>
              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                {result.summary}
              </p>
            </div>

            <div className="bg-slate-50 dark:bg-slate-900/50 rounded-xl p-4 relative border border-slate-100 dark:border-slate-800/50">
              <div className="flex justify-between items-start mb-3">
                <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">Suggested Message</h4>
                <button 
                  onClick={copyToClipboard}
                  className="text-primary hover:bg-primary/10 p-1 rounded-lg transition-colors"
                >
                  <Copy size={16} />
                </button>
              </div>
              <p className="text-slate-800 dark:text-slate-200 text-sm leading-relaxed italic">
                "{result.message}"
              </p>
              <div className="mt-2 text-[10px] text-slate-400 text-right">
                {result.message.length} / 300 caracteres
              </div>
            </div>
          </div>
        </motion.section>
      )}
    </div>
  );
};

const HistoryPage = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [filter, setFilter] = useState('All');

  useEffect(() => {
    fetch('/api/history').then(res => res.json()).then(setHistory);
  }, []);

  const updateStatus = async (id: number, status: string) => {
    await fetch(`/api/history/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    setHistory(history.map(item => item.id === id ? { ...item, status: status as any } : item));
  };

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-4">
        <div className="flex w-full items-center rounded-xl bg-slate-100 dark:bg-primary/10 px-4 h-12 border border-transparent focus-within:border-primary/50 transition-all">
          <Search size={20} className="text-slate-500 dark:text-slate-400 mr-2" />
          <input 
            className="w-full bg-transparent border-none focus:ring-0 text-slate-900 dark:text-slate-100 placeholder:text-slate-500 dark:placeholder:text-slate-400 text-sm font-medium" 
            placeholder="Search LinkedIn profiles or companies" 
          />
        </div>
      </div>

      <div className="flex gap-3 px-4 pb-4 overflow-x-auto no-scrollbar">
        {['All', 'High Match', 'Sent'].map(f => (
          <button 
            key={f}
            onClick={() => setFilter(f)}
            className={`flex h-9 shrink-0 items-center justify-center gap-x-2 rounded-full px-4 text-xs font-semibold transition-all ${filter === f ? 'bg-primary text-white shadow-sm shadow-primary/20' : 'bg-slate-100 dark:bg-primary/10 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-primary/20'}`}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto px-4 space-y-3 pb-24">
        {history.filter(item => {
          if (filter === 'High Match') return item.match_score >= 80;
          if (filter === 'Sent') return item.status === 'Sent';
          return true;
        }).map(item => (
          <div key={item.id} className="flex items-center gap-4 bg-white dark:bg-primary/5 p-4 rounded-xl border border-slate-100 dark:border-primary/10 shadow-sm">
            <div className="relative">
              <div className="size-14 rounded-lg bg-primary/10 flex items-center justify-center text-primary border border-slate-200 dark:border-primary/20">
                {item.campaign === 'CRM' ? <Building2 size={24} /> : <Rocket size={24} />}
              </div>
              <div className="absolute -bottom-1 -right-1 bg-white dark:bg-background-dark p-0.5 rounded-md shadow-sm">
                <div className="size-5 bg-slate-100 dark:bg-primary/20 rounded flex items-center justify-center">
                  {item.campaign === 'CRM' ? <Cpu size={12} className="text-primary" /> : <Rocket size={12} className="text-primary" />}
                </div>
              </div>
            </div>
            <div className="flex flex-col flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p className="text-slate-900 dark:text-slate-100 text-base font-bold truncate">{item.name}</p>
                <span className={`flex items-center justify-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${item.match_score >= 80 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'}`}>
                  {item.match_score >= 80 ? 'High Match' : 'Medium Match'}
                </span>
              </div>
              <p className="text-slate-500 dark:text-slate-400 text-xs font-medium mt-0.5">{item.role} @ {item.company}</p>
              <div className="flex items-center justify-between mt-2">
                <p className="text-slate-400 dark:text-slate-500 text-[11px] font-normal uppercase tracking-wide">
                  {new Date(item.created_at).toLocaleDateString('es-CL', { month: 'short', day: 'numeric' })}
                </p>
                <button 
                  onClick={() => updateStatus(item.id, item.status === 'Sent' ? 'Not Contacted' : 'Sent')}
                  className={`flex items-center gap-1 px-1.5 py-0.5 rounded transition-colors ${item.status === 'Sent' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-slate-500/10 text-slate-500'}`}
                >
                  <CheckCircle2 size={14} className={item.status === 'Sent' ? 'fill-emerald-500/20' : ''} />
                  <span className="text-[10px] font-bold uppercase">{item.status}</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// --- Main App ---

export default function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'analyze' | 'history' | 'settings'>('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard onAnalyze={() => setActiveTab('analyze')} />;
      case 'analyze':
        return <Analyzer onComplete={() => setActiveTab('history')} />;
      case 'history':
        return <HistoryPage />;
      default:
        return <div className="p-4 text-center text-slate-500">Settings coming soon</div>;
    }
  };

  const getTitle = () => {
    switch (activeTab) {
      case 'dashboard': return 'SDR Campaign';
      case 'analyze': return 'Profile Analyzer';
      case 'history': return 'Analysis History';
      case 'settings': return 'Settings';
    }
  };

  return (
    <div className="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 antialiased min-h-screen flex flex-col max-w-[430px] mx-auto border-x border-slate-200 dark:border-slate-800 shadow-2xl">
      <Header 
        title={getTitle()} 
        showBack={activeTab !== 'dashboard'} 
        onBack={() => setActiveTab('dashboard')} 
      />
      
      <main className="flex-1 overflow-y-auto">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            transition={{ duration: 0.2 }}
            className="h-full"
          >
            {renderContent()}
          </motion.div>
        </AnimatePresence>
      </main>

      <nav className="fixed bottom-0 w-full max-w-[430px] bg-white dark:bg-[#192b33] border-t border-slate-200 dark:border-slate-800 px-4 pb-8 pt-2 z-20">
        <div className="flex gap-2">
          <NavItem icon={BarChart3} label="Dashboard" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
          <NavItem icon={Search} label="Analyze" active={activeTab === 'analyze'} onClick={() => setActiveTab('analyze')} />
          <NavItem icon={History} label="History" active={activeTab === 'history'} onClick={() => setActiveTab('history')} />
          <NavItem icon={Settings} label="Settings" active={activeTab === 'settings'} onClick={() => setActiveTab('settings')} />
        </div>
      </nav>

      {activeTab === 'history' && (
        <div className="fixed bottom-24 right-[calc(50%-215px+16px)] z-30">
          <button 
            onClick={() => setActiveTab('analyze')}
            className="flex items-center justify-center size-14 rounded-full bg-primary text-white shadow-lg shadow-primary/30 active:scale-95 transition-transform"
          >
            <Plus size={28} />
          </button>
        </div>
      )}
    </div>
  );
}
