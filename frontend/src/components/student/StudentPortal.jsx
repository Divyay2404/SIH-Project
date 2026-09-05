import React, { useState } from 'react';
import { Send, Bot, User, Target, HelpCircle, ShieldAlert, Sparkles } from 'lucide-react';
import MarksSelector from './MarksSelector';
import PdfViewer from './PdfViewer';
import DiagnosticQuiz from './DiagnosticQuiz';

export default function StudentPortal() {
  const [selectedMarks, setSelectedMarks] = useState(5);
  const [selectedPage, setSelectedPage] = useState(3);
  const [activeCitation, setActiveCitation] = useState({
    page_number: 3,
    bounding_box: [80.0, 200.0, 540.0, 380.0],
    snippet: "BST Deletion Algorithm has 3 cases..."
  });

  const [inputQuery, setInputQuery] = useState("Explain Binary Search Tree deletion algorithm");
  const [loading, setLoading] = useState(false);
  const [isQuizOpen, setIsQuizOpen] = useState(false);

  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      marks: 5,
      abstain: false,
      text: "**5-MARK ANSWER (Concept Scale)**\n\n**Overview**: BST Deletion removes a target node while maintaining the BST ordering invariant (`Left < Root < Right`).\n\n**Key Cases**:\n• **Case 1 (Leaf Node)**: Delete node directly by setting parent reference to NULL.\n• **Case 2 (Single Child)**: Replace node pointer directly with its child.\n• **Case 3 (Two Children)**: Substitute node key with its **In-Order Successor** (smallest key in right subtree), then recursively delete successor.\n\n**Process Flow**:\n`Delete node 50 -> Find min in right subtree (60) -> Replace 50 with 60 -> Delete original 60.`",
      citation: {
        page_number: 3,
        bounding_box: [80.0, 200.0, 540.0, 380.0],
        snippet: "BST Deletion Algorithm has 3 cases..."
      }
    }
  ]);

  const handleSendQuery = async (queryText = inputQuery) => {
    if (!queryText.trim()) return;
    
    const userMsg = { sender: 'user', text: queryText };
    setMessages(prev => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: queryText,
          marks: selectedMarks
        })
      });
      const data = await res.json();
      
      const botMsg = {
        sender: 'bot',
        marks: data.marks,
        abstain: data.abstain,
        text: data.answer,
        citation: data.citation
      };

      setMessages(prev => [...prev, botMsg]);

      if (data.citation) {
        setActiveCitation(data.citation);
        setSelectedPage(data.citation.page_number);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCitationClick = (citation) => {
    if (citation) {
      setActiveCitation(citation);
      setSelectedPage(citation.page_number);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      {/* Left Column: Chat Assistant & Controls (7 Cols) */}
      <div className="lg:col-span-7 space-y-4">
        {/* Top Controls: Marks Selector & Quiz Trigger */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <MarksSelector selectedMarks={selectedMarks} setSelectedMarks={setSelectedMarks} />
          
          <button
            onClick={() => setIsQuizOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-300 border border-amber-500/30 hover:border-amber-500/60 text-xs font-semibold shadow-lg shadow-amber-500/10 transition-all duration-150"
          >
            <HelpCircle className="w-4 h-4 text-amber-400" />
            <span>Take Diagnostic Quiz</span>
          </button>
        </div>

        {/* Chat Console Panel */}
        <div className="glass-panel rounded-2xl h-[620px] flex flex-col overflow-hidden border border-slate-800 shadow-xl">
          {/* Console Header */}
          <div className="px-4 py-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <Bot className="w-4 h-4 text-indigo-400" />
              <span className="font-semibold text-slate-200">Grounded Research & Q&A Assistant</span>
            </div>
            <span className="px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 font-mono text-[10px]">
              Grounded Model Active
            </span>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.sender === 'bot' && (
                  <div className="w-8 h-8 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0 shadow-sm">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed shadow-sm ${
                    msg.sender === 'user'
                      ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-br-none'
                      : msg.abstain
                      ? 'bg-rose-500/10 border border-rose-500/30 text-rose-200 rounded-bl-none'
                      : 'bg-slate-900/90 border border-slate-800 text-slate-200 rounded-bl-none'
                  }`}
                >
                  {/* Answer Body */}
                  <div className="whitespace-pre-wrap font-sans">{msg.text}</div>

                  {/* Citation Badge Link */}
                  {msg.sender === 'bot' && msg.citation && (
                    <div className="mt-3 pt-2.5 border-t border-slate-800 flex items-center justify-between">
                      <button
                        onClick={() => handleCitationClick(msg.citation)}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 hover:bg-amber-500/20 text-[11px] font-semibold transition-all duration-150"
                      >
                        <Target className="w-3.5 h-3.5" />
                        <span>Source Citation: Page {msg.citation.page_number} (Click to Highlight Bbox)</span>
                      </button>
                    </div>
                  )}

                  {/* Abstention Gate Warning */}
                  {msg.sender === 'bot' && msg.abstain && (
                    <div className="mt-2 text-[10px] text-rose-400 flex items-center gap-1 font-semibold">
                      <ShieldAlert className="w-3 h-3" />
                      <span>Security Gate: Non-hallucination abstention rule enforced</span>
                    </div>
                  )}
                </div>

                {msg.sender === 'user' && (
                  <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex gap-2 items-center text-xs text-indigo-400 animate-pulse p-2">
                <Bot className="w-4 h-4 animate-spin" />
                <span>Searching knowledge repository & applying {selectedMarks}-mark schema...</span>
              </div>
            )}
          </div>

          {/* Quick Prompts */}
          <div className="px-4 py-2.5 bg-slate-950/90 border-t border-slate-800 flex flex-wrap items-center gap-2">
            <span className="text-[10px] text-slate-400 font-semibold flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-indigo-400" /> Demo Prompts:
            </span>
            <button
              onClick={() => handleSendQuery("Explain BST deletion algorithm")}
              className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-[11px] text-slate-200 border border-slate-700 transition-colors"
            >
              BST Deletion (Grounded)
            </button>
            <button
              onClick={() => handleSendQuery("How do I bake a chocolate cake?")}
              className="px-2.5 py-1 rounded-lg bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/40 text-[11px] text-rose-300 transition-colors"
            >
              Off-Topic Query (Test Abstain)
            </button>
          </div>

          {/* Input Bar */}
          <div className="p-3 bg-slate-900 border-t border-slate-800 flex items-center gap-2">
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendQuery()}
              placeholder="Ask any question from your course syllabus..."
              className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
            <button
              onClick={() => handleSendQuery()}
              disabled={loading || !inputQuery.trim()}
              className="p-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg shadow-indigo-600/30 transition-all duration-150 disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Right Column: Split-Screen PDF Viewer (5 Cols) */}
      <div className="lg:col-span-5">
        <PdfViewer
          activeCitation={activeCitation}
          selectedPage={selectedPage}
          setSelectedPage={setSelectedPage}
        />
      </div>

      {/* Diagnostic Quiz Modal */}
      <DiagnosticQuiz isOpen={isQuizOpen} onClose={() => setIsQuizOpen(false)} />
    </div>
  );
}
