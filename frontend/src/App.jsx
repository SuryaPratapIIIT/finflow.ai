import React, { useState, useEffect, useRef } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  BarChart, Bar, Cell 
} from 'recharts';
import { 
  LayoutDashboard, TerminalSquare, AlertCircle, Plus, X, Bot, 
  Loader2, Sparkles, Pencil, Trash2, Download, Play, Square, Settings,
  Database, FileCode2, Volume2, Save
} from 'lucide-react';

// --- SIDEBAR COMPONENT ---
function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'dashboard', label: 'Analytics Dashboard', icon: LayoutDashboard },
    { id: 'studio', label: 'AI Agent Studio', icon: TerminalSquare },
  ];

  return (
    <div className="w-64 bg-[#131b2f] border-r border-slate-800 flex flex-col h-full">
      <div className="p-6">
        <h1 className="text-2xl font-bold tracking-wide text-white flex items-center gap-2">
          FinFlow AI
          <span className="text-xs bg-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded-full border border-indigo-500/30">Beta</span>
        </h1>
        <p className="text-slate-500 text-xs mt-2 uppercase tracking-wider font-semibold">Autonomous Collections</p>
      </div>
      
      <nav className="flex-1 px-4 space-y-2 mt-4">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-sm font-medium ${
                isActive 
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20' 
                  : 'text-slate-400 hover:bg-[#1a233a] hover:text-slate-200'
              }`}
            >
              <Icon className={`h-5 w-5 ${isActive ? 'text-white' : 'text-slate-500'}`} />
              {item.label}
            </button>
          )
        })}
      </nav>

      <div className="p-6">
        <div className="bg-[#0b0f19] rounded-xl p-4 border border-slate-800">
          <div className="flex items-center gap-2 mb-2">
            <Database className="h-4 w-4 text-emerald-400" />
            <span className="text-xs font-semibold text-slate-300">ChromaDB Status</span>
          </div>
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>RAG Vectors</span>
            <span className="text-emerald-500">Connected</span>
          </div>
        </div>
      </div>
    </div>
  );
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// --- AI STUDIO VIEW ---
function AIStudioView() {
  const [activeAgent, setActiveAgent] = useState('finance_agent_v1');
  const [promptContent, setPromptContent] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPrompt(activeAgent);
  }, [activeAgent]);

  const fetchPrompt = async (agentName) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/prompts/${agentName}`);
      if (res.ok) {
        const data = await res.json();
        setPromptContent(data.content);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/prompts/${activeAgent}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: promptContent })
      });
      if (res.ok) {
        alert("Agent configuration updated successfully!");
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <header className="mb-8">
        <h2 className="text-2xl font-bold text-white">AI Agent Studio</h2>
        <p className="text-slate-400 text-sm mt-1">Configure LangGraph system prompts and RAG instructions</p>
      </header>

      <div className="flex gap-6 flex-1 h-0">
        {/* Agent Selector */}
        <div className="w-64 space-y-2">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4 px-2">Active Agents</div>
          {[
            { id: 'finance_agent_v1', name: 'Finance Agent (Drafter)', icon: FileCode2 },
            { id: 'reflection_agent_v1', name: 'Reflection Agent (Critic)', icon: Settings },
            { id: 'editor_agent_email_v1', name: 'Email Editor Agent', icon: FileCode2 },
            { id: 'editor_agent_voice_v1', name: 'Voice Script Agent', icon: Volume2 }
          ].map(agent => (
            <button
              key={agent.id}
              onClick={() => setActiveAgent(agent.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl border text-sm font-medium transition-all ${
                activeAgent === agent.id
                  ? 'bg-[#1a233a] border-indigo-500 text-indigo-400'
                  : 'bg-transparent border-transparent text-slate-400 hover:bg-[#131b2f]'
              }`}
            >
              <agent.icon className="h-4 w-4" />
              {agent.name}
            </button>
          ))}
        </div>

        {/* Editor Area */}
        <div className="flex-1 flex flex-col bg-[#131b2f] rounded-2xl border border-slate-800 shadow-xl overflow-hidden">
          <div className="border-b border-slate-800 p-4 flex items-center justify-between bg-[#0f172a]">
            <div className="flex items-center gap-2">
              <TerminalSquare className="h-5 w-5 text-indigo-400" />
              <span className="font-mono text-sm text-slate-300">{activeAgent}.yaml</span>
            </div>
            <button 
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
            >
              {isSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              Deploy to Agent
            </button>
          </div>
          <div className="flex-1 p-4 relative">
            {loading ? (
              <div className="absolute inset-0 flex items-center justify-center">
                <Loader2 className="h-8 w-8 text-indigo-500 animate-spin" />
              </div>
            ) : (
              <textarea
                value={promptContent}
                onChange={(e) => setPromptContent(e.target.value)}
                className="w-full h-full bg-[#0b0f19] text-slate-300 font-mono text-sm p-6 rounded-xl border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none resize-none"
                spellCheck="false"
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


// --- LIVE REASONING TERMINAL COMPONENT ---
function AIReasoningTerminal({ invoiceId, onClose }) {
  const [logs, setLogs] = useState([]);
  const messages = [
    `> Initializing LangGraph Orchestrator for Invoice #${invoiceId}...`,
    `> Fetching customer profile and payment history...`,
    `> Connecting to ChromaDB (RAG)...`,
    `> RAG: Retrieved 3 relevant company policies.`,
    `> Analyzing overdue duration and customer reliability...`,
    `> Detected Tone requirement based on policy...`,
    `> [Finance Agent] Drafting initial communications...`,
    `> [Reflection Agent] Reviewing draft against policies...`,
    `> Groundedness score computed. Modifying draft...`,
    `> Generating Final Email and Voice Scripts...`,
    `> Saving JSON artifacts to storage...`,
    `> Agent workflow complete! Pipeline closed.`
  ];

  useEffect(() => {
    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex < messages.length) {
        setLogs(prev => [...prev, messages[currentIndex]]);
        currentIndex++;
      } else {
        clearInterval(interval);
      }
    }, 600); // Add a new log every 600ms to simulate reasoning

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-[#0b0f19]/90 backdrop-blur-md p-4">
      <div className="w-full max-w-3xl bg-[#0f172a] rounded-2xl border border-slate-700 shadow-2xl overflow-hidden flex flex-col h-[500px]">
        <div className="bg-[#1e293b] p-4 flex items-center justify-between border-b border-slate-700">
          <div className="flex items-center gap-3">
            <Bot className="h-5 w-5 text-indigo-400 animate-pulse" />
            <h3 className="text-white font-semibold">Live AI Orchestration Stream</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="flex-1 p-6 font-mono text-sm overflow-y-auto bg-black text-emerald-400 space-y-2">
          {logs.map((log, idx) => (
            <div key={idx} className="opacity-0 animate-[fadeIn_0.3s_ease-in_forwards]">
              {log}
            </div>
          ))}
          <div className="flex items-center gap-2 mt-4 text-slate-500">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Awaiting subprocess exit...</span>
          </div>
        </div>
      </div>
    </div>
  );
}


// --- MAIN DASHBOARD VIEW ---
function DashboardView() {
  const [dsoData, setDsoData] = useState([]);
  const [overdueData, setOverdueData] = useState([]);
  const [logs, setLogs] = useState([]);
  const [pendingInvoices, setPendingInvoices] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [runningAgentId, setRunningAgentId] = useState(null);
  const [showTerminal, setShowTerminal] = useState(null);
  const [selectedLogs, setSelectedLogs] = useState([]);
  const [editingLog, setEditingLog] = useState(null);
  const [editDraftContent, setEditDraftContent] = useState("");
  const [playingLogId, setPlayingLogId] = useState(null);
  
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ customer_id: '', amount: '', due_date: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchData = async () => {
    try {
      const [dsoRes, overdueRes, logsRes, custRes, pendingRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/metrics/dso`),
        fetch(`${API_BASE_URL}/api/metrics/top-overdue`),
        fetch(`${API_BASE_URL}/api/logs`),
        fetch(`${API_BASE_URL}/api/customers`),
        fetch(`${API_BASE_URL}/api/invoices/pending`)
      ]);
      const dso = await dsoRes.json();
      const overdue = await overdueRes.json();
      const logsData = await logsRes.json();
      const custData = await custRes.json();
      const pendingData = await pendingRes.json();
      setDsoData(dso.data || []);
      setOverdueData(overdue.data || []);
      setLogs(logsData.data || []);
      setCustomers(custData.data || []);
      setPendingInvoices(pendingData.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddInvoice = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/invoices`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_id: parseInt(formData.customer_id),
          amount: parseFloat(formData.amount),
          due_date: formData.due_date,
          status: 'overdue'
        })
      });
      if (response.ok) {
        setShowModal(false);
        setFormData({ customer_id: '', amount: '', due_date: '' });
        await fetchData(); 
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTriggerAI = async (invoiceId) => {
    setRunningAgentId(invoiceId);
    setShowTerminal(invoiceId); // Show the live reasoning terminal!
    try {
      await fetch(`${API_BASE_URL}/api/orchestrate/${invoiceId}`, { method: 'POST' });
      await fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setRunningAgentId(null);
      setTimeout(() => setShowTerminal(null), 1500); // Close terminal shortly after completion
    }
  };

  const handleDeleteLog = async (filename) => {
    if (!window.confirm("Are you sure you want to delete this AI log?")) return;
    try {
      await fetch(`${API_BASE_URL}/api/logs/${filename}`, { method: 'DELETE' });
      await fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSaveEdit = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/logs/${editingLog.filename}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft: editDraftContent })
      });
      if (response.ok) {
        setEditingLog(null);
        await fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Browser TTS Voice simulation
  const handlePlayVoice = (log) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel(); // Stop anything playing
      
      if (playingLogId === log.id) {
        setPlayingLogId(null);
        return;
      }
      
      setPlayingLogId(log.id);
      
      const msg = new SpeechSynthesisUtterance();
      msg.text = log.draft;
      msg.rate = 0.9; 
      msg.pitch = 1;
      
      msg.onend = () => {
        setPlayingLogId(null);
      };
      
      window.speechSynthesis.speak(msg);
    } else {
      alert("Text-to-speech not supported in this browser.");
    }
  };

  if (loading) return <div className="flex h-full items-center justify-center text-xl text-indigo-400">Loading Dashboard...</div>;

  return (
    <>
      <header className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">Collections Overview</h2>
          <p className="text-slate-400 text-sm mt-1">Real-time metrics and autonomous actions</p>
        </div>
        <button onClick={() => setShowModal(true)} className="flex items-center gap-2 rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-lg hover:bg-indigo-500 transition-colors w-fit">
          <Plus className="h-4 w-4" /> Add Invoice
        </button>
      </header>

      {showTerminal && <AIReasoningTerminal invoiceId={showTerminal} onClose={() => setShowTerminal(null)} />}

      <div className="mb-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 rounded-2xl border border-slate-800 bg-[#131b2f] p-6 shadow-xl relative overflow-hidden">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="text-sm font-medium text-slate-400">DSO Trend</h3>
              <div className="flex items-center gap-3 mt-1">
                <span className="text-3xl font-bold text-white">
                  {dsoData.length > 0 ? dsoData[dsoData.length - 1].avg_days_late.toFixed(1) : '0'} Days
                </span>
                <span className="flex items-center bg-emerald-500/10 text-emerald-400 text-xs font-semibold px-2 py-1 rounded">▼ 12.5%</span>
              </div>
            </div>
          </div>
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={dsoData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorDSO" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                <XAxis dataKey="month" stroke="#64748b" tickLine={false} axisLine={false} tick={{fontSize: 12}} dy={10} />
                <YAxis stroke="#64748b" tickLine={false} axisLine={false} tick={{fontSize: 12}} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }} itemStyle={{ color: '#818cf8' }} />
                <Area type="monotone" dataKey="avg_days_late" stroke="#818cf8" strokeWidth={3} fillOpacity={1} fill="url(#colorDSO)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-[#131b2f] p-6 shadow-xl flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-white">Pending Outreach</h3>
            <span className="bg-indigo-500/20 text-indigo-400 text-xs font-medium px-2 py-1 rounded border border-indigo-500/30">AI Action</span>
          </div>
          <div className="flex-1 overflow-y-auto pr-2 space-y-4">
            {pendingInvoices.length > 0 ? pendingInvoices.map((invoice) => (
              <div key={invoice.id} className="group relative flex items-center justify-between rounded-xl border border-slate-800 bg-[#1a233a] p-4 transition-colors hover:border-slate-700">
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-800 text-slate-400">
                    <Bot className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-sm text-slate-200">{invoice.name}</p>
                    <p className="text-xs text-slate-500">{invoice.days_overdue} days late</p>
                  </div>
                </div>
                <button 
                  onClick={() => handleTriggerAI(invoice.id)}
                  disabled={runningAgentId === invoice.id}
                  className="flex h-8 items-center gap-2 rounded bg-indigo-600 px-3 text-xs font-medium text-white transition-colors hover:bg-indigo-500 disabled:opacity-50"
                >
                  {runningAgentId === invoice.id ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <><Sparkles className="h-3.5 w-3.5" /> Run</>}
                </button>
              </div>
            )) : <div className="flex h-full items-center justify-center text-slate-500 text-sm">No pending invoices.</div>}
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-[#131b2f] p-6 shadow-xl">
        <div className="mb-6 flex items-center justify-between">
          <h3 className="text-lg font-bold text-white">Agent Output Logs</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead>
              <tr className="border-b border-slate-800 text-slate-500">
                <th className="pb-3 font-medium px-4">Invoice</th>
                <th className="pb-3 font-medium px-4">Agent Tone</th>
                <th className="pb-3 font-medium px-4">Score</th>
                <th className="pb-3 font-medium px-4">Draft Extract</th>
                <th className="pb-3 font-medium px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {logs.length > 0 ? logs.map((log, idx) => {
                let badgeColors = { bg: "bg-slate-800", dot: "bg-slate-500", text: "text-slate-300" };
                if (log.tone === "Gentle") badgeColors = { bg: "bg-emerald-500/10", dot: "bg-emerald-500", text: "text-emerald-400" };
                if (log.tone === "Firm") badgeColors = { bg: "bg-amber-500/10", dot: "bg-amber-500", text: "text-amber-400" };
                if (log.tone === "Escalation") badgeColors = { bg: "bg-rose-500/10", dot: "bg-rose-500", text: "text-rose-400" };

                return (
                  <tr key={idx} className="border-b border-slate-800/50 hover:bg-[#1a233a] transition-colors">
                    <td className="px-4 py-4 font-semibold text-slate-200">#{log.id}</td>
                    <td className="px-4 py-4">
                      <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${badgeColors.bg} border border-slate-800`}>
                        <div className={`h-1.5 w-1.5 rounded-full ${badgeColors.dot}`} />
                        <span className={badgeColors.text}>{log.tone}</span>
                      </span>
                    </td>
                    <td className="px-4 py-4"><span className="text-emerald-400 font-semibold">{log.score}/5</span></td>
                    <td className="px-4 py-4 text-slate-400 max-w-xs truncate">{log.draft}</td>
                    <td className="px-4 py-4 text-right">
                      <div className="flex justify-end gap-3 text-slate-500">
                        <button onClick={() => handlePlayVoice(log)} className="hover:text-emerald-400 transition-colors" title={playingLogId === log.id ? "Stop Voice" : "Simulate Voice Call"}>
                          {playingLogId === log.id ? <Square className="h-4 w-4 fill-current" /> : <Play className="h-4 w-4" />}
                        </button>
                        <button onClick={() => {setEditingLog(log); setEditDraftContent(log.draft)}} className="hover:text-indigo-400 transition-colors" title="Edit Draft"><Pencil className="h-4 w-4" /></button>
                        <button onClick={() => handleDeleteLog(log.filename)} className="hover:text-rose-400 transition-colors" title="Delete Log"><Trash2 className="h-4 w-4" /></button>
                      </div>
                    </td>
                  </tr>
                )
              }) : (
                <tr><td colSpan="5" className="py-8 text-center text-slate-500">No agent logs found. Trigger the AI above!</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-[70] flex items-center justify-center bg-[#0b0f19]/80 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-[#131b2f] p-6 shadow-2xl">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">New Invoice</h2>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white transition-colors"><X className="h-5 w-5" /></button>
            </div>
            <form onSubmit={handleAddInvoice} className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-400">Customer</label>
                <select required value={formData.customer_id} onChange={e => setFormData({...formData, customer_id: e.target.value})} className="w-full rounded-lg border border-slate-700 bg-[#0f172a] px-3 py-2 text-slate-200 outline-none">
                  <option value="">Select a customer...</option>
                  {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-400">Amount ($)</label>
                <input type="number" step="0.01" required value={formData.amount} onChange={e => setFormData({...formData, amount: e.target.value})} className="w-full rounded-lg border border-slate-700 bg-[#0f172a] px-3 py-2 text-slate-200 outline-none" placeholder="1500.50" />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-400">Due Date</label>
                <input type="date" required value={formData.due_date} onChange={e => setFormData({...formData, due_date: e.target.value})} className="w-full rounded-lg border border-slate-700 bg-[#0f172a] px-3 py-2 text-slate-200 outline-none" />
              </div>
              <div className="pt-2">
                <button type="submit" disabled={isSubmitting} className="w-full rounded-lg bg-indigo-600 py-2.5 text-sm font-medium text-white shadow-lg hover:bg-indigo-500 transition-colors disabled:opacity-50">
                  {isSubmitting ? 'Creating...' : 'Create Invoice'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {editingLog && (
        <div className="fixed inset-0 z-[70] flex items-center justify-center bg-[#0b0f19]/80 backdrop-blur-sm">
          <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-[#131b2f] p-6 shadow-2xl">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <Pencil className="h-5 w-5 text-indigo-400" /> Edit AI Draft
                </h2>
                <p className="text-sm text-slate-400 mt-1">Invoice #{editingLog.id} • {editingLog.tone} Tone</p>
              </div>
              <button onClick={() => setEditingLog(null)} className="text-slate-400 hover:text-white transition-colors"><X className="h-5 w-5" /></button>
            </div>
            <div className="space-y-4">
              <textarea value={editDraftContent} onChange={e => setEditDraftContent(e.target.value)} className="w-full h-64 rounded-lg border border-slate-700 bg-[#0f172a] p-4 text-slate-200 outline-none font-mono text-sm leading-relaxed" />
              <div className="flex justify-end gap-3 pt-4">
                <button onClick={() => setEditingLog(null)} className="rounded-lg px-4 py-2.5 text-sm font-medium text-slate-300 hover:bg-slate-800 transition-colors">Cancel</button>
                <button onClick={handleSaveEdit} className="rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-medium text-white shadow-lg hover:bg-indigo-500 transition-colors">Save Changes</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// --- APP ROOT ---
export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  return (
    <div className="flex h-screen bg-[#0b0f19] text-slate-200 overflow-hidden font-sans">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="flex-1 overflow-y-auto p-4 md:p-8">
        {activeTab === 'dashboard' && <DashboardView />}
        {activeTab === 'studio' && <AIStudioView />}
      </main>
    </div>
  );
}
