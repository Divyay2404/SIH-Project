import React, { useState } from 'react';
import { HelpCircle, CheckCircle, Lightbulb, ShieldAlert, RefreshCw, X } from 'lucide-react';

export default function DiagnosticQuiz({ isOpen, onClose }) {
  const [selectedOption, setSelectedOption] = useState(null);
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const quizData = {
    question: "When deleting a BST node with two children, which node is substituted in its place to preserve the search invariant?",
    options: [
      { id: 0, text: "In-Order Successor (Smallest key in right subtree)", isCorrect: true },
      { id: 1, text: "Pre-Order Traversal Root Node", isCorrect: false },
      { id: 2, text: "Right-most Leaf Node in Left Subtree without updating parent pointers", isCorrect: false },
      { id: 3, text: "Any random child node", isCorrect: false }
    ]
  };

  const handleDiagnose = async () => {
    if (selectedOption === null) return;
    setLoading(true);
    try {
      const res = await fetch('/api/diagnose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: 'q_bst_del_01',
          selected_option: selectedOption,
          topic_id: 'bst_deletion'
        })
      });
      const data = await res.json();
      setDiagnosis(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-xl rounded-2xl border border-slate-700 p-6 relative shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-5">
          <div className="p-2.5 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
            <HelpCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">Adaptive Diagnostic Assessment</h3>
            <p className="text-xs text-slate-400">Error Taxonomy & Concept Gap Analyzer</p>
          </div>
        </div>

        {/* Question text */}
        <div className="p-4 bg-slate-900/90 rounded-xl border border-slate-800 mb-5 text-xs sm:text-sm font-medium text-slate-200 leading-relaxed shadow-inner">
          {quizData.question}
        </div>

        {/* Option list */}
        <div className="space-y-2.5 mb-6">
          {quizData.options.map((opt) => (
            <button
              key={opt.id}
              onClick={() => {
                setSelectedOption(opt.id);
                setDiagnosis(null);
              }}
              className={`w-full p-4 rounded-xl text-xs text-left font-medium transition-all duration-150 flex items-center justify-between border ${
                selectedOption === opt.id
                  ? 'bg-indigo-600/20 text-indigo-200 border-indigo-500 shadow-md shadow-indigo-500/10'
                  : 'bg-slate-900/60 text-slate-300 border-slate-800 hover:border-slate-700 hover:bg-slate-800/60'
              }`}
            >
              <span>{opt.text}</span>
              {selectedOption === opt.id && <div className="w-2.5 h-2.5 rounded-full bg-indigo-500 shadow-sm shadow-indigo-500"></div>}
            </button>
          ))}
        </div>

        {!diagnosis ? (
          <button
            onClick={handleDiagnose}
            disabled={selectedOption === null || loading}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 font-semibold text-xs text-white shadow-lg shadow-indigo-600/30 transition-all duration-200 disabled:opacity-50"
          >
            {loading ? "Analyzing Concept Fingerprint..." : "Submit Answer for Diagnosis"}
          </button>
        ) : (
          <div className="space-y-4">
            {diagnosis.is_correct ? (
              <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-300 text-xs flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold block text-sm">Concept Mastered!</span>
                  <p className="mt-1">Your readiness score updated to 88%. You demonstrate strong mastery of BST successor substitution.</p>
                </div>
              </div>
            ) : (
              <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-amber-400 text-xs font-bold">
                  <ShieldAlert className="w-4 h-4" />
                  <span>DIAGNOSIS: {diagnosis.error_title}</span>
                </div>
                <p className="text-xs text-slate-300">{diagnosis.explanation}</p>

                {diagnosis.rescue_mission && (
                  <div className="p-3.5 bg-slate-900/90 rounded-lg border border-amber-500/40 text-xs space-y-2">
                    <div className="flex items-center gap-1.5 text-amber-300 font-semibold">
                      <Lightbulb className="w-4 h-4 text-amber-400 animate-pulse" />
                      <span>{diagnosis.rescue_mission.title}</span>
                    </div>
                    <p className="text-slate-300 italic leading-relaxed">{diagnosis.rescue_mission.analogy}</p>
                  </div>
                )}
              </div>
            )}

            <button
              onClick={() => {
                setDiagnosis(null);
                setSelectedOption(null);
              }}
              className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 flex items-center justify-center gap-2 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Try Another Diagnostic Question</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
