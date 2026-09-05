import React, { useState, useEffect } from 'react';
import { BarChart3, AlertCircle, TrendingDown, Layers, PieChart } from 'lucide-react';

export default function WeaknessHeatmap() {
  const [heatmapData, setHeatmapData] = useState({
    overall_readiness: 72,
    topic_heatmap: [
      { topic: "BST Concept & Properties", mastery: 88, error_type: "None", status: "Mastered" },
      { topic: "BST Insertion Algorithm", mastery: 78, error_type: "Careless Error", status: "Good" },
      { topic: "BST Deletion (Two Children)", mastery: 42, error_type: "Conceptual Gap", status: "Critical Gap" },
      { topic: "Time & Space Complexity", mastery: 68, error_type: "Terminology Confusion", status: "Needs Review" }
    ],
    class_error_distribution: {
      "Conceptual Gap": 45,
      "Process Mistake": 25,
      "Terminology Confusion": 20,
      "Careless Error": 10
    }
  });

  useEffect(() => {
    fetch('/api/readiness')
      .then(res => res.json())
      .then(data => setHeatmapData(data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-semibold">Cohort Class Readiness Score</span>
            <BarChart3 className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{heatmapData.overall_readiness}%</span>
            <span className="text-xs text-emerald-400 font-semibold">+4.2% this week</span>
          </div>
          <div className="w-full h-1.5 bg-slate-800 rounded-full mt-3 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 rounded-full"
              style={{ width: `${heatmapData.overall_readiness}%` }}
            ></div>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-semibold">Top Diagnostic Bottleneck</span>
            <AlertCircle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-bold text-rose-300">BST Deletion (Case 3)</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            45% of students exhibit a <span className="text-rose-400 font-semibold">Conceptual Gap</span> in In-Order Successor swapping.
          </p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-semibold">Active Rescue Missions</span>
            <TrendingDown className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-amber-300">18</span>
            <span className="text-xs text-slate-400">students assigned</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Targeted analogies served for Binary Tree hierarchy.
          </p>
        </div>
      </div>

      {/* Class Concept Heatmap Grid */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        <h3 className="text-sm font-bold text-slate-100 mb-4 flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-400" />
          <span>Curriculum Mastery & Concept Weakness Heatmap</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {heatmapData.topic_heatmap.map((item, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-xl border transition-all ${
                item.mastery >= 80
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-200'
                  : item.mastery >= 65
                  ? 'bg-indigo-500/10 border-indigo-500/30 text-indigo-200'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-200'
              }`}
            >
              <div className="flex items-center justify-between text-xs font-semibold mb-2">
                <span>{item.topic}</span>
                <span className="font-mono text-sm">{item.mastery}%</span>
              </div>
              <div className="flex items-center justify-between text-[11px] opacity-80">
                <span>Error: {item.error_type}</span>
                <span className="px-2 py-0.5 rounded bg-slate-900/60 font-medium">
                  {item.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
