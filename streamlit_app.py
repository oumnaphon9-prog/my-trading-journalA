import React, { useState, useMemo, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area,
  PieChart, Pie, Cell 
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Activity, Wallet, 
  Calendar as CalendarIcon, ArrowUpRight, ArrowDownRight, Plus,
  Filter, X, Save, Database, Loader2, Target, CheckCircle2, AlertCircle, 
  DollarSign, ShieldAlert, Zap, Brain, Calculator, Info, History, Trash2
} from 'lucide-react';

// --- CONFIGURATION ---
const GOOGLE_SHEET_API_URL = "https://script.google.com/macros/s/AKfycbzfkmozOhWspXIQWodh6IuH4d1IiTuxeN9oAk0T-lRoKWXeXIU8pbfu3vfKuvH5Igg/exec"; 
const STARTING_BALANCE = 100;

const App = () => {
  const [trades, setTrades] = useState([]);
  const [filter, setFilter] = useState('All');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCalcOpen, setIsCalcOpen] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSync, setLastSync] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');

  // Calculator State
  const [calcData, setCalcData] = useState({
    riskPercent: 2,
    stopLossPips: 20,
    pipValue: 10 
  });
  
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    pair: '',
    type: 'Buy',
    entry: '',
    exit: '',
    pnlUsd: '',
    psychology: 'Neutral', 
    notes: ''
  });

  // Load Data
  useEffect(() => {
    const savedTrades = localStorage.getItem('forex_journal_100usd_v2');
    if (savedTrades) setTrades(JSON.parse(savedTrades));
    const savedSync = localStorage.getItem('last_sync_time');
    if (savedSync) setLastSync(savedSync);
  }, []);

  // Save Data
  useEffect(() => {
    localStorage.setItem('forex_journal_100usd_v2', JSON.stringify(trades));
  }, [trades]);

  const stats = useMemo(() => {
    const totalTrades = trades.length;
    const wins = trades.filter(t => t.status === 'Win').length;
    const winRate = totalTrades > 0 ? ((wins / totalTrades) * 100).toFixed(1) : 0;
    const netProfit = trades.reduce((acc, curr) => acc + curr.pnl, 0);
    const currentBalance = STARTING_BALANCE + netProfit;
    const totalGrowth = ((netProfit / STARTING_BALANCE) * 100).toFixed(1);

    // Risk Limits (15% Daily, 30% Drawdown)
    const dailyLossLimit = (currentBalance * 0.15).toFixed(2);
    const maxDrawdownLimit = (currentBalance * 0.30).toFixed(2);
    const stopTradingLimit = (currentBalance * 0.50).toFixed(2);

    return { 
      totalTrades, winRate, netProfit, currentBalance, totalGrowth, wins, 
      losses: totalTrades - wins,
      limits: { daily: dailyLossLimit, drawdown: maxDrawdownLimit, stop: stopTradingLimit }
    };
  }, [trades]);

  const dailyPnL = useMemo(() => {
    const map = {};
    trades.forEach(t => {
      map[t.date] = (map[t.date] || 0) + t.pnl;
    });
    return map;
  }, [trades]);

  const chartData = useMemo(() => {
    let balance = STARTING_BALANCE;
    const data = [{ name: 'Start', balance: STARTING_BALANCE }];
    const sortedTrades = [...trades].reverse();
    sortedTrades.forEach((t, index) => {
      balance += t.pnl;
      data.push({ name: `T${index + 1}`, balance: Math.round(balance * 100) / 100 });
    });
    return data;
  }, [trades]);

  const calculatedLot = useMemo(() => {
    const riskAmount = (stats.currentBalance * (calcData.riskPercent / 100));
    const lotSize = riskAmount / (calcData.stopLossPips * (calcData.pipValue / 1));
    return isFinite(lotSize) ? lotSize.toFixed(2) : "0.00";
  }, [calcData, stats.currentBalance]);

  const addTrade = (e) => {
    e.preventDefault();
    const pnlValue = parseFloat(formData.pnlUsd);
    if (isNaN(pnlValue)) return;

    const newTrade = {
      id: Date.now(),
      ...formData,
      pnl: Math.round(pnlValue * 100) / 100,
      status: pnlValue >= 0 ? 'Win' : 'Loss'
    };

    setTrades([newTrade, ...trades]);
    setIsModalOpen(false);
    setFormData({ 
      date: new Date().toISOString().split('T')[0], pair: '', type: 'Buy', entry: '', exit: '', pnlUsd: '', psychology: 'Neutral', notes: '' 
    });
  };

  const deleteTrade = (id) => {
    if (window.confirm('ต้องการลบรายการนี้ใช่หรือไม่?')) {
      setTrades(trades.filter(t => t.id !== id));
    }
  };

  const syncWithGoogleSheets = async () => {
    if (!GOOGLE_SHEET_API_URL) return;
    setIsSyncing(true);
    try {
      await fetch(GOOGLE_SHEET_API_URL, {
        method: 'POST', mode: 'no-cors', cache: 'no-cache',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(trades)
      });
      const now = new Date().toLocaleString();
      setLastSync(now);
      localStorage.setItem('last_sync_time', now);
    } catch (e) { 
      console.error(e);
      alert("Sync Failed. Please check your API URL.");
    }
    finally { setIsSyncing(false); }
  };

  const filteredTrades = trades.filter(t => filter === 'All' || t.status === filter);

  const renderCalendar = () => {
    const days = [];
    const now = new Date();
    for(let i = 0; i < 28; i++) {
      const d = new Date();
      d.setDate(now.getDate() - i);
      const dateStr = d.toISOString().split('T')[0];
      const pnl = dailyPnL[dateStr] || 0;
      days.push({ date: dateStr, pnl });
    }
    return days;
  };

  return (
    <div className="min-h-screen bg-[#050505] text-slate-200 font-sans p-4 md:p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <TrendingUp size={24} className="text-white" />
            </div>
            <h1 className="text-3xl font-black text-white tracking-tight uppercase">
              $100 <span className="text-indigo-500">Challenge</span>
            </h1>
          </div>
          <div className="flex gap-6 mt-4">
            <button onClick={() => setActiveTab('dashboard')} className={`text-[11px] font-black uppercase tracking-[0.2em] transition-all ${activeTab === 'dashboard' ? 'text-indigo-400 border-b-2 border-indigo-400 pb-1' : 'text-slate-600 hover:text-slate-400'}`}>Dashboard</button>
            <button onClick={() => setActiveTab('calendar')} className={`text-[11px] font-black uppercase tracking-[0.2em] transition-all ${activeTab === 'calendar' ? 'text-indigo-400 border-b-2 border-indigo-400 pb-1' : 'text-slate-600 hover:text-slate-400'}`}>History Calendar</button>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button onClick={() => setIsCalcOpen(true)} className="flex items-center justify-center w-11 h-11 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-2xl border border-slate-800 transition-all">
            <Calculator size={20} />
          </button>
          <button onClick={syncWithGoogleSheets} disabled={isSyncing || trades.length === 0} className={`flex items-center justify-center w-11 h-11 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-2xl border border-slate-800 transition-all ${isSyncing ? 'opacity-50' : ''}`}>
            {isSyncing ? <Loader2 className="animate-spin" size={20} /> : <Database size={20} />}
          </button>
          <button onClick={() => setIsModalOpen(true)} className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-2xl shadow-xl shadow-indigo-500/20 text-sm font-black uppercase tracking-widest transition-all hover:-translate-y-1">
            <Plus size={20} /> New Log
          </button>
        </div>
      </div>

      {activeTab === 'dashboard' ? (
        <>
          {/* Main Stats Row */}
          <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-slate-900/40 border border-slate-800/50 p-6 rounded-3xl backdrop-blur-sm">
                <p className="text-slate-500 text-[10px] font-black uppercase tracking-widest mb-1">Equity</p>
                <h3 className="text-3xl font-black text-white">${stats.currentBalance.toLocaleString()}</h3>
                <p className={`text-[10px] font-bold mt-1 ${stats.netProfit >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                   {stats.netProfit >= 0 ? '▲' : '▼'} {stats.totalGrowth}% Total Growth
                </p>
            </div>
            <div className="bg-slate-900/40 border border-slate-800/50 p-6 rounded-3xl backdrop-blur-sm">
                <p className="text-slate-500 text-[10px] font-black uppercase tracking-widest mb-1">Win Rate</p>
                <h3 className="text-3xl font-black text-white">{stats.winRate}%</h3>
                <p className="text-slate-500 text-[10px] font-bold mt-1">{stats.wins} Wins / {stats.losses} Losses</p>
            </div>
            <div className="bg-slate-900/40 border border-orange-500/10 p-6 rounded-3xl backdrop-blur-sm">
                <p className="text-orange-500/70 text-[10px] font-black uppercase tracking-widest mb-1">Max Daily Loss</p>
                <h3 className="text-3xl font-black text-orange-500">-${stats.limits.daily}</h3>
                <p className="text-slate-500 text-[10px] font-bold mt-1">15% of current equity</p>
            </div>
            <div className="bg-slate-900/40 border border-rose-500/10 p-6 rounded-3xl backdrop-blur-sm">
                <p className="text-rose-500/70 text-[10px] font-black uppercase tracking-widest mb-1">Stop Trading</p>
                <h3 className="text-3xl font-black text-rose-500">-${stats.limits.stop}</h3>
                <p className="text-slate-500 text-[10px] font-bold mt-1">Critical drawdown limit</p>
            </div>
          </div>

          {/* Chart Section */}
          <div className="max-w-7xl mx-auto mb-8">
            <div className="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-8 overflow-hidden relative">
              <div className="flex items-center justify-between mb-8 relative z-10">
                <h2 className="text-xs font-black text-white uppercase tracking-[0.3em] flex items-center gap-2">
                  <Activity size={16} className="text-indigo-500" /> Performance Curve
                </h2>
                <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Starting: $100.00</div>
              </div>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="colorBal" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" strokeOpacity={0.5} />
                    <XAxis dataKey="name" hide />
                    <YAxis stroke="#475569" fontSize={10} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v}`} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '16px', fontSize: '12px' }}
                      itemStyle={{ color: '#818cf8', fontWeight: 'bold' }}
                    />
                    <Area type="monotone" dataKey="balance" stroke="#6366f1" strokeWidth={4} fill="url(#colorBal)" animationDuration={2000} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Trade List */}
          <div className="max-w-7xl mx-auto">
             <div className="flex items-center justify-between mb-6 px-2">
                <h2 className="text-xs font-black text-white uppercase tracking-[0.3em] flex items-center gap-2">
                  <History size={16} className="text-indigo-500" /> Recent Logs
                </h2>
                <div className="flex bg-slate-900/50 p-1 rounded-xl border border-slate-800">
                  {['All', 'Win', 'Loss'].map(t => (
                    <button key={t} onClick={() => setFilter(t)} className={`px-4 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all ${filter === t ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}>{t}</button>
                  ))}
                </div>
             </div>
             
             <div className="grid grid-cols-1 gap-4">
                {filteredTrades.map((trade) => (
                  <div key={trade.id} className="group bg-slate-900/40 border border-slate-800 hover:border-indigo-500/30 p-5 rounded-3xl transition-all flex flex-col md:flex-row md:items-center justify-between gap-4">
                     <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center font-black text-xs ${trade.status === 'Win' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
                           {trade.status === 'Win' ? <ArrowUpRight size={24}/> : <ArrowDownRight size={24}/>}
                        </div>
                        <div>
                           <div className="flex items-center gap-2">
                              <span className="font-black text-white uppercase tracking-wider">{trade.pair}</span>
                              <span className={`text-[9px] font-black px-2 py-0.5 rounded uppercase ${trade.type === 'Buy' ? 'bg-indigo-500/20 text-indigo-400' : 'bg-orange-500/20 text-orange-400'}`}>{trade.type}</span>
                           </div>
                           <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">{trade.date} · Mood: {trade.psychology}</p>
                        </div>
                     </div>
                     
                     <div className="flex items-center justify-between md:justify-end gap-10">
                        <div className="text-right hidden md:block">
                           <p className="text-slate-500 text-[9px] font-black uppercase tracking-widest">Entry/Exit</p>
                           <p className="text-xs font-mono text-slate-300">{trade.entry || '0.00'} → {trade.exit || '0.00'}</p>
                        </div>
                        <div className="text-right">
                           <p className="text-slate-500 text-[9px] font-black uppercase tracking-widest">Profit/Loss</p>
                           <p className={`text-xl font-black ${trade.pnl >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                             {trade.pnl >= 0 ? '+' : ''}${Math.abs(trade.pnl).toFixed(2)}
                           </p>
                        </div>
                        <button onClick={() => deleteTrade(trade.id)} className="text-slate-700 hover:text-rose-500 transition-colors p-2">
                           <Trash2 size={18} />
                        </button>
                     </div>
                  </div>
                ))}
                
                {filteredTrades.length === 0 && (
                  <div className="py-20 text-center bg-slate-900/20 border border-dashed border-slate-800 rounded-[2.5rem]">
                      <div className="inline-flex w-16 h-16 bg-slate-900 rounded-full items-center justify-center mb-4 text-slate-700">
                        <History size={32} />
                      </div>
                      <p className="text-xs text-slate-600 font-black uppercase tracking-[0.2em]">No data available</p>
                  </div>
                )}
             </div>
          </div>
        </>
      ) : (
        /* Calendar View */
        <div className="max-w-7xl mx-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-10">
            <h2 className="text-xs font-black text-white uppercase tracking-[0.3em] flex items-center gap-2 mb-10">
              <CalendarIcon size={18} className="text-indigo-400" /> 28-Day Log History
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-6">
              {renderCalendar().map((day, i) => (
                <div key={i} className={`aspect-square rounded-[2rem] p-5 flex flex-col justify-between border transition-all hover:scale-105 ${
                  day.pnl > 0 ? 'bg-emerald-500/10 border-emerald-500/20 shadow-lg shadow-emerald-500/5' : 
                  day.pnl < 0 ? 'bg-rose-500/10 border-rose-500/20 shadow-lg shadow-rose-500/5' : 
                  'bg-black/40 border-slate-800 opacity-40'
                }`}>
                  <span className="text-[10px] text-slate-500 font-black uppercase">{day.date.split('-').slice(1).reverse().join('/')}</span>
                  <div className="mt-auto">
                    <span className={`text-lg font-black block ${day.pnl > 0 ? 'text-emerald-400' : day.pnl < 0 ? 'text-rose-400' : 'text-slate-700'}`}>
                      {day.pnl === 0 ? '$0' : (day.pnl > 0 ? `+$${day.pnl.toFixed(1)}` : `-$${Math.abs(day.pnl).toFixed(1)}`)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Lot Calculator Modal */}
      {isCalcOpen && (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-xl flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-[3rem] w-full max-w-sm overflow-hidden shadow-2xl relative">
             <div className="p-8 pb-4 flex justify-between items-center">
                <h3 className="font-black uppercase tracking-[0.2em] text-[10px] text-indigo-400">Risk Manager</h3>
                <button onClick={() => setIsCalcOpen(false)} className="text-slate-500 hover:text-white transition-colors"><X size={24}/></button>
             </div>
             <div className="p-8 pt-0 space-y-6">
                <div className="bg-indigo-600 p-8 rounded-[2.5rem] text-center shadow-xl shadow-indigo-500/20">
                   <p className="text-[10px] font-black text-indigo-200 uppercase tracking-[0.2em] mb-2">Recommended Lot Size</p>
                   <h2 className="text-6xl font-black text-white">{calculatedLot}</h2>
                   <p className="text-indigo-200 text-xs font-bold mt-2">LOTS</p>
                </div>
                <div className="space-y-5">
                   <div className="space-y-2">
                     <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Risk Amount (%)</label>
                     <input type="number" value={calcData.riskPercent} onChange={(e)=>setCalcData({...calcData, riskPercent: e.target.value})} className="w-full bg-black/60 border border-slate-800 rounded-2xl p-4 text-white outline-none focus:border-indigo-500 text-sm font-bold" />
                   </div>
                   <div className="space-y-2">
                     <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Stop Loss (Pips)</label>
                     <input type="number" value={calcData.stopLossPips} onChange={(e)=>setCalcData({...calcData, stopLossPips: e.target.value})} className="w-full bg-black/60 border border-slate-800 rounded-2xl p-4 text-white outline-none focus:border-indigo-500 text-sm font-bold" />
                   </div>
                </div>
                <div className="p-4 bg-slate-800/50 rounded-2xl border border-slate-800 flex gap-3">
                   <Info size={16} className="text-indigo-400 shrink-0" />
                   <p className="text-[10px] text-slate-400 leading-relaxed font-medium">คำนวณจากทุนปัจจุบัน (${stats.currentBalance}) เพื่อรักษาความเสี่ยงตามแผนที่วางไว้</p>
                </div>
             </div>
          </div>
        </div>
      )}

      {/* Trade Log Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-xl flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-[3rem] w-full max-w-lg overflow-hidden shadow-2xl">
            <div className="p-8 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
              <h3 className="text-xl font-black text-white tracking-widest uppercase">New Performance Log</h3>
              <button onClick={() => setIsModalOpen(false)} className="bg-slate-800 p-2 rounded-xl text-slate-400 hover:text-white transition-all"><X size={20} /></button>
            </div>
            <form onSubmit={addTrade} className="p-8 space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                   <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Date</label>
                   <input type="date" value={formData.date} onChange={(e) => setFormData({...formData, date: e.target.value})} className="w-full bg-black/60 border border-slate-800 rounded-2xl text-white p-4 outline-none text-sm focus:border-indigo-500" />
                </div>
                <div className="space-y-2">
                   <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Asset</label>
                   <input type="text" placeholder="XAUUSD" required value={formData.pair} onChange={(e) => setFormData({...formData, pair: e.target.value})} className="w-full bg-black/60 border border-slate-800 rounded-2xl text-white p-4 outline-none uppercase text-sm font-black focus:border-indigo-500" />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Order Type</label>
                <div className="flex gap-2 p-1.5 bg-black/60 rounded-2xl border border-slate-800">
                  {['Buy', 'Sell'].map(s => (
                    <button key={s} type="button" onClick={() => setFormData({...formData, type: s})} className={`flex-1 py-3 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] transition-all ${formData.type === s ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-600 hover:text-slate-400'}`}>{s}</button>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Net PnL (USD)</label>
                <input type="number" step="any" placeholder="0.00" required value={formData.pnlUsd} onChange={(e) => setFormData({...formData, pnlUsd: e.target.value})} className={`w-full bg-black/60 border border-slate-800 rounded-2xl p-5 outline-none text-3xl font-black text-center focus:border-indigo-500 ${parseFloat(formData.pnlUsd) >= 0 ? 'text-emerald-500' : 'text-rose-500'}`} />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Entry Price</label>
                  <input type="number" step="any" placeholder="0.0000" value={formData.entry} onChange={(e) => setFormData({...formData, entry: e.target.value})} className="w-full bg-black/60 border border-slate-800 rounded-2xl text-white p-4 text-xs outline-none" />
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Exit Price</label>
                  <input type="number" step="any" placeholder="0.0000" value={formData.exit} onChange={(e) => setFormData({...formData, exit: e.target.value})} className="w-full bg-black/60 border border-slate-800 rounded-2xl text-white p-4 text-xs outline-none" />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Psychology</label>
                <div className="grid grid-cols-5 gap-2">
                  {['Calm', 'Neutral', 'Greed', 'Fear', 'Rush'].map(emo => (
                    <button key={emo} type="button" onClick={() => setFormData({...formData, psychology: emo})} className={`py-2 rounded-xl text-[8px] font-black border transition-all uppercase tracking-tighter ${formData.psychology === emo ? 'bg-indigo-500 border-indigo-500 text-white shadow-lg shadow-indigo-500/20' : 'border-slate-800 text-slate-600 hover:border-slate-700'}`}>
                      {emo}
                    </button>
                  ))}
                </div>
              </div>

              <button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-black py-5 rounded-[1.5rem] shadow-2xl shadow-indigo-500/20 uppercase tracking-[0.3em] text-xs transition-all hover:-translate-y-1 mt-4">
                Confirm Log Entry
              </button>
            </form>
          </div>
        </div>
      )}
      
      {/* Footer Info */}
      <div className="max-w-7xl mx-auto mt-12 mb-8 flex flex-col md:flex-row justify-between items-center opacity-30 gap-4">
         <p className="text-[10px] font-black uppercase tracking-widest italic">Disciplined trading leads to freedom.</p>
         <div className="flex gap-4 items-center">
            {lastSync && <p className="text-[9px] font-bold uppercase tracking-widest">Last Sync: {lastSync}</p>}
            <p className="text-[9px] font-bold uppercase tracking-widest">v2.4 Pro Edition</p>
         </div>
      </div>
    </div>
  );
};

export default App;
