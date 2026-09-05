import React from 'react';
import { BookOpen, GraduationCap, ShieldCheck, Cpu, LayoutDashboard } from 'lucide-react';

export default function Header({ activeTab, setActiveTab }) {
  return (
    <header className="glass-panel sticky top-0 z-50 px-6 py-4 mb-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Brand & SIH Metadata */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <Cpu className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
                StudyCopilot & StudyForge
              </h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                SIH 2026 PROTOTYPE
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Unified Hybrid Adaptive Learning OS | Team <span className="text-indigo-400 font-semibold">Tech_Warriors</span>
            </p>
          </div>
        </div>

        {/* User View Mode Tabs */}
        <div className="flex items-center p-1 bg-slate-900/80 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('student')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'student'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <GraduationCap className="w-4 h-4" />
            <span>Student Learning Twin</span>
          </button>

          <button
            onClick={() => setActiveTab('educator')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'educator'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            <span>Educator Console</span>
          </button>
        </div>

        {/* Security & Evidence Gate Badge */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
          <ShieldCheck className="w-4 h-4" />
          <span>Evidence-or-Abstain Gated</span>
        </div>
      </div>
    </header>
  );
}
