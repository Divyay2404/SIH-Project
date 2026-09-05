import React from 'react';
import { SlidersHorizontal } from 'lucide-react';

export default function MarksSelector({ selectedMarks, setSelectedMarks }) {
  const markOptions = [
    { marks: 2, label: '2 Marks', desc: 'Concise Definition Scale' },
    { marks: 5, label: '5 Marks', desc: 'Concept Breakdown Scale' },
    { marks: 10, label: '10 Marks', desc: 'Comprehensive Essay & Proofs' }
  ];

  return (
    <div className="flex flex-col sm:flex-row items-center gap-2 p-2 bg-slate-900/90 rounded-xl border border-slate-800 shadow-sm">
      <div className="flex items-center gap-1.5 px-3 py-1 text-xs font-semibold text-slate-400">
        <SlidersHorizontal className="w-3.5 h-3.5 text-indigo-400" />
        <span>Answer Depth Scale:</span>
      </div>
      <div className="grid grid-cols-3 gap-1.5 w-full sm:w-auto">
        {markOptions.map((opt) => (
          <button
            key={opt.marks}
            onClick={() => setSelectedMarks(opt.marks)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 ${
              selectedMarks === opt.marks
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/25 border border-indigo-400/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 border border-transparent'
            }`}
            title={opt.desc}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}
