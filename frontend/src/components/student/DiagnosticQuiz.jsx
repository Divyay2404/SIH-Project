import React, { useState, useEffect } from 'react';
import { HelpCircle, CheckCircle, Lightbulb, ShieldAlert, RefreshCw, X, Loader2, FileText, Sparkles, UploadCloud } from 'lucide-react';
import { apiUrl } from '../../config/api';

export default function DiagnosticQuiz({ isOpen, onClose, activeDocument, onLoadDemo, onUploadClick }) {
  const [selectedOption, setSelectedOption] = useState(null);
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetchingQuiz, setFetchingQuiz] = useState(false);
  const [quizData, setQuizData] = useState(null);
  const [fetchError, setFetchError] = useState(null);

  useEffect(() => {
    if (!isOpen) {
      setSelectedOption(null);
      setDiagnosis(null);
      return;
    }

    const fetchQuestion = async () => {
      setFetchingQuiz(true);
      setFetchError(null);
      try {
        const queryParam = activeDocument?.document_id
          ? `?document_id=${encodeURIComponent(activeDocument.document_id)}`
          : '';
        const res = await fetch(apiUrl(`/api/quiz${queryParam}`));
        if (!res.ok) {
          throw new Error(`Failed to load quiz question (HTTP ${res.status})`);
        }
        const data = await res.json();
        setQuizData(data);
      } catch (err) {
        setFetchError(err.message || 'Could not fetch diagnostic question.');
      } finally {
        setFetchingQuiz(false);
      }
    };

    fetchQuestion();
  }, [isOpen, activeDocument?.document_id]);

  if (!isOpen) return null;

  const handleDiagnose = async () => {
    if (selectedOption === null || !quizData) return;
    setLoading(true);
    try {
      const topicIdentifier = quizData.topic
        ? quizData.topic.toLowerCase().replace(/[^a-z0-9_]/g, '_').slice(0, 30)
        : 'general';

      const res = await fetch(apiUrl('/api/diagnose'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: quizData.question_id || 'q_diagnostic_01',
          selected_option: selectedOption,
          topic_id: topicIdentifier
        })
      });
      if (res.ok && res.headers.get('content-type')?.includes('application/json')) {
        const data = await res.json();
        setDiagnosis(data);
      }
    } catch (err) {
      console.error('Quiz diagnosis error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-xl rounded-2xl border border-slate-700 p-6 relative shadow-2xl animate-in fade-in zoom-in-95 duration-200 bg-slate-950">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-5">
          <div className="p-2.5 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
            <HelpCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">Adaptive Diagnostic Assessment</h3>
            <p className="text-xs text-slate-400">
              {quizData?.topic ? `Topic Focus: ${quizData.topic}` : 'Error Taxonomy & Concept Gap Analyzer'}
            </p>
          </div>
        </div>

        {fetchingQuiz && (
          <div className="py-12 flex flex-col items-center justify-center gap-3 text-slate-400 text-xs">
            <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
            <span>Formulating topic assessment question...</span>
          </div>
        )}

        {fetchError && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs mb-5">
            <p className="font-semibold mb-1">Failed to load quiz:</p>
            <p>{fetchError}</p>
          </div>
        )}

        {!fetchingQuiz && !fetchError && quizData && (
          <>
            {quizData.is_empty ? (
              <div className="text-center py-8 space-y-4">
                <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mx-auto">
                  <FileText className="w-7 h-7" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-slate-200">No Active Study Document</h4>
                  <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                    Diagnostic assessments are generated dynamically from your active study material. Upload a PDF or load the sample demo module.
                  </p>
                </div>
                <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
                  {onUploadClick && (
                    <button
                      onClick={() => { onClose(); onUploadClick(); }}
                      className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md transition-colors cursor-pointer"
                    >
                      <UploadCloud className="w-4 h-4" />
                      <span>Upload Course PDF</span>
                    </button>
                  )}
                  {onLoadDemo && (
                    <button
                      onClick={async () => {
                        await onLoadDemo();
                        onClose();
                      }}
                      className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-semibold transition-colors cursor-pointer"
                    >
                      <Sparkles className="w-4 h-4 text-amber-400" />
                      <span>Load Sample BST Demo</span>
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <>
                {/* Question text */}
                <div className="p-4 bg-slate-900/90 rounded-xl border border-slate-800 mb-5 text-xs sm:text-sm font-medium text-slate-200 leading-relaxed shadow-inner">
                  {quizData.question_text}
                </div>

                {/* Option list */}
                <div className="space-y-2.5 mb-6">
                  {quizData.options && quizData.options.map((optionText, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setSelectedOption(idx);
                        setDiagnosis(null);
                      }}
                      className={`w-full p-4 rounded-xl text-xs text-left font-medium transition-all duration-150 flex items-center justify-between border cursor-pointer ${
                        selectedOption === idx
                          ? 'bg-indigo-600/20 text-indigo-200 border-indigo-500 shadow-md shadow-indigo-500/10'
                          : 'bg-slate-900/60 text-slate-300 border-slate-800 hover:border-slate-700 hover:bg-slate-800/60'
                      }`}
                    >
                      <span>{optionText}</span>
                      {selectedOption === idx && <div className="w-2.5 h-2.5 rounded-full bg-indigo-500 shadow-sm shadow-indigo-500"></div>}
                    </button>
                  ))}
                </div>

                {!diagnosis ? (
                  <button
                    onClick={handleDiagnose}
                    disabled={selectedOption === null || loading}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 font-semibold text-xs text-white shadow-lg shadow-indigo-600/30 transition-all duration-200 disabled:opacity-50 cursor-pointer"
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
                          <p className="mt-1">
                            {diagnosis.feedback || `Your readiness score updated to ${diagnosis.updated_readiness || 85}%. You demonstrate strong mastery of ${quizData.topic}.`}
                          </p>
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
                      className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 flex items-center justify-center gap-2 transition-colors cursor-pointer"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                      <span>Try Another Diagnostic Question</span>
                    </button>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
