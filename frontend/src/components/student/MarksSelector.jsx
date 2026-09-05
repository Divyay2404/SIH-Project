import React from 'react';
import { Award } from 'lucide-react';

export default function MarksSelector({ selectedMarks, setSelectedMarks }) {
  const markOptions = [
    { marks: 2, label: '2 Marks', desc: 'Definition Scale (<50 words)' },
    { marks: 5, label: '5 Marks', desc: 'Concept Scale (Bullet Points)' },
    { marks: 10, label: '10 Marks', desc: 'Essay Scale (Full Algorithm & Proofs)' }
  ];

  return (
    <div className="flex flex-col sm:flex-row items-center gap-2 p-2 bg-slate-900/90 rounded-xl border border-slate-800">
      <div className="flex items-center gap-1.5 px-3 py-1 text-xs font-semibold text-slate-400">
        <Award className="w-4 h-4 text-amber-400" />
        <span>Exam Marks Scale:</span>
      </div>
      <div className="grid grid-cols-3 gap-1.5 w-full sm:w-auto">
        {markOptions.map((opt) => (
          <button
            key={opt.marks}
            onClick={() => setSelectedMarks(opt.marks)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all text-center ${
              selectedMarks === opt.marks
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm shadow-amber-500/10'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
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
