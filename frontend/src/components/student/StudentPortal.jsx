import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Target, 
  HelpCircle, 
  ShieldAlert, 
  Sparkles, 
  Columns, 
  Maximize2, 
  Minimize2, 
  GripVertical, 
  FileText, 
  MessageSquare, 
  RotateCcw,
  CheckCircle2,
  ChevronRight,
  ChevronDown,
  Trash2,
  UploadCloud,
  FileUp,
  AlertCircle,
  Loader2,
  BookOpen,
  X,
  FileCheck
} from 'lucide-react';
import MarksSelector from './MarksSelector';
import PdfViewer from './PdfViewer';
import DiagnosticQuiz from './DiagnosticQuiz';
import { apiUrl } from '../../config/api';

export default function StudentPortal({
  activeDocument: propActiveDoc,
  setActiveDocument: propSetActiveDoc,
  availableDocuments: propAvailDocs,
  setAvailableDocuments: propSetAvailDocs
}) {
  const [selectedMarks, setSelectedMarks] = useState(5);
  const [selectedPage, setSelectedPage] = useState(1);
  const [activeCitation, setActiveCitation] = useState(null);
  const [localActiveDocument, setLocalActiveDocument] = useState(null);
  const [localAvailableDocuments, setLocalAvailableDocuments] = useState([]);

  const activeDocument = propActiveDoc !== undefined ? propActiveDoc : localActiveDocument;
  const setActiveDocument = propSetActiveDoc || setLocalActiveDocument;
  const availableDocuments = propAvailDocs !== undefined ? propAvailDocs : localAvailableDocuments;
  const setAvailableDocuments = propSetAvailDocs || setLocalAvailableDocuments;

  const [activeDocumentId, setActiveDocumentId] = useState(activeDocument?.document_id || null);

  useEffect(() => {
    if (activeDocument?.document_id && activeDocument.document_id !== activeDocumentId) {
      setActiveDocumentId(activeDocument.document_id);
    }
  }, [activeDocument?.document_id, activeDocumentId]);

  const [inputQuery, setInputQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadPhase, setUploadPhase] = useState("");
  const [uploadError, setUploadError] = useState(null);
  const [isQuizOpen, setIsQuizOpen] = useState(false);
  const [isDraggingFile, setIsDraggingFile] = useState(false);

  // Split-Screen Layout State
  const [layoutMode, setLayoutMode] = useState('split');
  const [splitRatio, setSplitRatio] = useState(58);
  const [isDragging, setIsDragging] = useState(false);
  const [mobileTab, setMobileTab] = useState('chat');
  const [citationNotification, setCitationNotification] = useState(null);

  const containerRef = useRef(null);
  const pdfContainerRef = useRef(null);
  const chatMessagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const [messages, setMessages] = useState([]);

  // Fetch available documents from backend
  const fetchDocuments = useCallback(async () => {
    try {
      const res = await fetch(apiUrl('/api/documents'));
      if (res.ok && res.headers.get('content-type')?.includes('application/json')) {
        const data = await res.json();
        if (Array.isArray(data.documents)) {
          setAvailableDocuments(data.documents);
        }
      }
    } catch (err) {
      console.warn('Could not retrieve available documents:', err.message);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Auto-scroll chat feed to latest message
  useEffect(() => {
    chatMessagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Resizable split drag handlers
  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleTouchStart = () => {
    setIsDragging(true);
  };

  useEffect(() => {
    const handleMove = (clientX) => {
      if (!isDragging || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const newRatio = ((clientX - rect.left) / rect.width) * 100;
      if (newRatio >= 25 && newRatio <= 75) {
        setSplitRatio(Math.round(newRatio));
      }
    };

    const handleMouseMove = (e) => handleMove(e.clientX);
    const handleTouchMove = (e) => {
      if (e.touches && e.touches[0]) {
        handleMove(e.touches[0].clientX);
      }
    };

    const handleEnd = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleEnd);
      window.addEventListener('touchmove', handleTouchMove);
      window.addEventListener('touchend', handleEnd);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleEnd);
      window.removeEventListener('touchmove', handleTouchMove);
      window.removeEventListener('touchend', handleEnd);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isDragging]);

  const resetSplitRatio = () => {
    setSplitRatio(58);
    setLayoutMode('split');
  };

  // Upload PDF Handler
  const handleFileUpload = async (file) => {
    if (!file) return;

    const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    if (!isPdf) {
      setUploadError('Invalid file format. Student Portal supports PDF course materials only (.pdf).');
      return;
    }

    if (file.size === 0) {
      setUploadError('The uploaded PDF file is empty (0 bytes). Please upload a valid document.');
      return;
    }

    setUploading(true);
    setUploadError(null);
    setUploadPhase('Uploading PDF to gateway...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      setUploadPhase('Processing PDF with PyMuPDF & OCR, indexing vectors...');
      let res;
      try {
        res = await fetch(apiUrl('/api/ingest'), {
          method: 'POST',
          body: formData
        });
      } catch (netErr) {
        throw new Error('Backend service unreachable. Please ensure the FastAPI server is running.');
      }

      const contentType = res.headers.get('content-type') || '';
      const isJson = contentType.includes('application/json');

      if (!res.ok) {
        let errorMsg = `Server error HTTP ${res.status}`;
        if (isJson) {
          try {
            const errorPayload = await res.json();
            errorMsg = errorPayload.detail || errorPayload.message || errorMsg;
          } catch (_) {}
        }
        if (res.status === 404) {
          errorMsg = 'Ingestion endpoint not found (HTTP 404). Please check backend deployment and VITE_API_BASE_URL.';
        } else if ([502, 503, 504].includes(res.status)) {
          errorMsg = `Gateway error (HTTP ${res.status}). Ingestion service temporarily unavailable.`;
        }
        throw new Error(errorMsg);
      }

      if (!isJson) {
        throw new Error('Unexpected response format received from ingestion gateway.');
      }

      const data = await res.json();
      if (!data.document_id) {
        throw new Error('Ingestion completed but did not return a valid document_id.');
      }

      const newDoc = {
        document_id: data.document_id,
        title: data.title || file.name.replace('.pdf', ''),
        filename: data.filename || file.name,
        pages_count: data.pages_processed || (data.pages ? data.pages.length : 1),
        chunks_count: data.chunks_extracted || 0,
        indexing_confirmed: Boolean(data.indexing_confirmed),
        summary: data.summary || '',
        important_concepts: data.important_concepts || [],
        sections: data.sections || [],
        pages: data.pages || [],
        sourceUrl: URL.createObjectURL(file)
      };

      setActiveDocument(newDoc);
      setActiveDocumentId(data.document_id);
      setSelectedPage(1);
      setActiveCitation(null);
      setMessages([
        {
          sender: 'bot',
          marks: selectedMarks,
          abstain: false,
          text: `📚 **Active Document Loaded**: **${newDoc.title}** (${newDoc.filename})\n\n• **Pages Processed**: ${newDoc.pages_count}\n• **Indexed Chunks**: ${newDoc.chunks_count} chunks verified in Vector DB\n\nAsk any question based specifically on this uploaded document. Select 2, 5, or 10 marks to scale the answer depth!`,
          citation: null
        }
      ]);

      // Refresh documents list
      fetchDocuments();
    } catch (err) {
      setUploadError(err.message || 'PDF ingestion failed.');
    } finally {
      setUploading(false);
      setUploadPhase('');
    }
  };

  // Switch Active Document
  const handleSelectDocument = async (docId) => {
    if (!docId || docId === activeDocumentId) return;
    setLoading(true);
    try {
      const res = await fetch(apiUrl(`/api/document/${encodeURIComponent(docId)}`));
      if (res.ok && res.headers.get('content-type')?.includes('application/json')) {
        const data = await res.json();
        const switchedDoc = {
          document_id: data.document_id,
          title: data.title,
          filename: data.filename,
          pages_count: data.pages_count,
          chunks_count: data.chunks_count,
          indexing_confirmed: data.indexing_confirmed,
          summary: data.summary,
          sections: data.sections,
          important_concepts: data.important_concepts,
          pages: data.pages || [],
          sourceUrl: apiUrl(`/api/document/${encodeURIComponent(data.document_id)}/pdf`)
        };
        setActiveDocument(switchedDoc);
        setActiveDocumentId(data.document_id);
        setSelectedPage(1);
        setActiveCitation(null);
        setMessages([
          {
            sender: 'bot',
            marks: selectedMarks,
            abstain: false,
            text: `🔄 **Active Document Switched**: **${switchedDoc.title}** (${switchedDoc.filename})\n\nPrevious context cleared. Q&A retrieval is now strictly restricted to this document.`,
            citation: null
          }
        ]);
      }
    } catch (err) {
      console.error('Failed to load document metadata:', err);
    } finally {
      setLoading(false);
    }
  };

  // Load Isolated Sample BST Demo
  const handleLoadDemo = async () => {
    setUploading(true);
    setUploadError(null);
    setUploadPhase('Loading sample Binary Search Tree demo module...');
    try {
      const res = await fetch(apiUrl('/api/demo/load'), { method: 'POST' });
      if (!res.ok) {
        throw new Error(`Demo load failed with HTTP ${res.status}`);
      }
      const data = await res.json();
      const demoDoc = {
        document_id: data.document_id,
        title: data.title,
        filename: data.filename,
        pages_count: data.pages_processed || 4,
        chunks_count: data.chunks_extracted || 4,
        indexing_confirmed: true,
        summary: data.summary,
        important_concepts: data.important_concepts || [],
        sections: data.sections || [],
        pages: data.pages || [],
        sourceUrl: apiUrl(`/api/document/${encodeURIComponent(data.document_id)}/pdf`)
      };
      setActiveDocument(demoDoc);
      setActiveDocumentId(data.document_id);
      setSelectedPage(1);
      setActiveCitation(null);
      setMessages([
        {
          sender: 'bot',
          marks: selectedMarks,
          abstain: false,
          text: `🌲 **Sample BST Demo Loaded**: **${demoDoc.title}** (${demoDoc.filename})\n\n• **Pages Processed**: ${demoDoc.pages_count}\n• **Demo Chunks**: 4 BST textbook sections indexed\n\nYou can now ask questions about Binary Search Tree properties, 3-case deletion, or asymptotic bounds!`,
          citation: null
        }
      ]);
      fetchDocuments();
    } catch (err) {
      setUploadError(err.message || 'Failed to load demo data.');
    } finally {
      setUploading(false);
      setUploadPhase('');
    }
  };

  // Handle Query Submission strictly scoped to activeDocumentId
  const handleSendQuery = async (queryText = inputQuery) => {
    if (!queryText || !queryText.trim()) return;

    if (!activeDocumentId) {
      setUploadError('Please upload or select a study document before asking questions.');
      return;
    }
    
    const userMsg = { sender: 'user', text: queryText };
    setMessages(prev => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const res = await fetch(apiUrl('/api/query'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: queryText,
          marks: selectedMarks,
          document_id: activeDocumentId
        })
      });

      const contentType = res.headers.get('content-type') || '';
      const isJson = contentType.includes('application/json');

      if (res.ok && isJson) {
        const data = await res.json();
        const botMsg = {
          sender: 'bot',
          marks: data.marks || selectedMarks,
          abstain: data.abstain,
          text: data.answer,
          citation: data.citation
        };
        setMessages(prev => [...prev, botMsg]);
        if (data.citation) {
          handleCitationClick(data.citation, false);
        }
      } else {
        let errorMsg = `Server error HTTP ${res.status}`;
        if (isJson) {
          try {
            const errData = await res.json();
            errorMsg = errData.detail || errData.message || errorMsg;
          } catch (_) {}
        }
        setMessages(prev => [
          ...prev,
          {
            sender: 'bot',
            marks: selectedMarks,
            abstain: true,
            text: `❌ **Error**: ${errorMsg}`,
            citation: null
          }
        ]);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          sender: 'bot',
          marks: selectedMarks,
          abstain: true,
          text: `❌ **Connection Failure**: Unable to reach backend RAG query endpoint (${err.message}).`,
          citation: null
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Clicking a citation badge scrolls PDF viewer to exact page and triggers coordinate highlight
  const handleCitationClick = (citation, userInitiated = true) => {
    if (!citation) return;
    setActiveCitation({ ...citation, triggerTimestamp: Date.now() });
    setSelectedPage(citation.page_number);

    if (layoutMode === 'chat') {
      setLayoutMode('split');
    }

    setMobileTab('pdf');

    if (userInitiated) {
      setCitationNotification(`Highlighted citation on Page ${citation.page_number}`);
      setTimeout(() => setCitationNotification(null), 3000);
    }

    setTimeout(() => {
      if (pdfContainerRef.current) {
        pdfContainerRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);
  };

  const clearChatHistory = () => {
    setMessages([]);
    setActiveCitation(null);
  };

  return (
    <div ref={containerRef} className="space-y-4">
      {/* Hidden File Input for PDF Upload */}
      <input
        ref={fileInputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={(e) => {
          if (e.target.files && e.target.files[0]) {
            handleFileUpload(e.target.files[0]);
            e.target.value = '';
          }
        }}
      />

      {/* Workspace Top Navigation & Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 glass-panel rounded-2xl border border-slate-800 shadow-md">
        {/* Left: Marks Selector, Document Switcher & Upload Trigger */}
        <div className="flex flex-wrap items-center gap-3">
          <MarksSelector selectedMarks={selectedMarks} setSelectedMarks={setSelectedMarks} />

          {/* Upload New Document Button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold shadow-md shadow-indigo-500/20 disabled:opacity-50 transition-all duration-150"
            title="Upload any course or syllabus PDF"
          >
            {uploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Ingesting PDF...</span>
              </>
            ) : (
              <>
                <UploadCloud className="w-4 h-4" />
                <span>Upload PDF</span>
              </>
            )}
          </button>

          {/* Document Switcher Dropdown */}
          {availableDocuments.length > 0 && (
            <div className="flex items-center gap-1.5 bg-slate-900/90 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs">
              <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
              <select
                value={activeDocumentId || ''}
                onChange={(e) => handleSelectDocument(e.target.value)}
                className="bg-transparent text-slate-200 text-xs font-medium focus:outline-none cursor-pointer max-w-[180px] truncate"
                title="Switch active study document"
              >
                <option value="" disabled>Select Study Document</option>
                {availableDocuments.map((doc) => (
                  <option key={doc.document_id} value={doc.document_id} className="bg-slate-900 text-slate-200">
                    {doc.title || doc.filename}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Diagnostic Quiz Button */}
          <button
            onClick={() => setIsQuizOpen(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-300 border border-amber-500/30 hover:border-amber-500/60 text-xs font-semibold shadow-lg shadow-amber-500/10 transition-all duration-150"
          >
            <HelpCircle className="w-4 h-4 text-amber-400" />
            <span className="hidden sm:inline">Take Diagnostic Quiz</span>
            <span className="sm:hidden">Quiz</span>
          </button>
        </div>

        {/* Right: Split Layout Controls */}
        <div className="flex items-center gap-2">
          {/* Preset Width Ratios */}
          <div className="hidden xl:flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800 text-[11px] font-semibold text-slate-400">
            <span className="px-2 text-[10px] text-slate-400">Split:</span>
            <button
              onClick={() => { setLayoutMode('split'); setSplitRatio(50); }}
              className={`px-2 py-1 rounded-lg transition-all ${
                layoutMode === 'split' && splitRatio === 50
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'hover:text-slate-200 hover:bg-slate-800'
              }`}
              title="50% Chat / 50% PDF"
            >
              50:50
            </button>
            <button
              onClick={() => { setLayoutMode('split'); setSplitRatio(58); }}
              className={`px-2 py-1 rounded-lg transition-all ${
                layoutMode === 'split' && splitRatio === 58
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'hover:text-slate-200 hover:bg-slate-800'
              }`}
              title="Default 58% Chat / 42% PDF"
            >
              60:40
            </button>
            <button
              onClick={() => { setLayoutMode('split'); setSplitRatio(70); }}
              className={`px-2 py-1 rounded-lg transition-all ${
                layoutMode === 'split' && splitRatio === 70
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'hover:text-slate-200 hover:bg-slate-800'
              }`}
              title="70% Chat / 30% PDF"
            >
              70:30
            </button>
            <button
              onClick={resetSplitRatio}
              className="p-1 rounded-lg hover:text-slate-200 hover:bg-slate-800 text-slate-400"
              title="Reset to default split"
            >
              <RotateCcw className="w-3 h-3" />
            </button>
          </div>

          {/* Toggleable Layout Mode Switcher */}
          <div className="flex items-center bg-slate-900/90 p-1 rounded-xl border border-slate-800 shadow-sm">
            <button
              onClick={() => setLayoutMode('split')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                layoutMode === 'split'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
              }`}
              title="Split View (Side-by-Side)"
            >
              <Columns className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Split Screen</span>
            </button>

            <button
              onClick={() => setLayoutMode('chat')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                layoutMode === 'chat'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
              }`}
              title="Focus on Chat Assistant (100% width)"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Chat Focus</span>
            </button>

            <button
              onClick={() => setLayoutMode('pdf')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                layoutMode === 'pdf'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
              }`}
              title="Focus on Document / PDF Viewer (100% width)"
            >
              <FileText className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Document Focus</span>
            </button>
          </div>
        </div>
      </div>

      {/* Upload Progress & Error Notification */}
      {uploading && (
        <div className="flex items-center gap-3 px-4 py-3 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-indigo-300 text-xs font-medium animate-fadeIn">
          <Loader2 className="w-4 h-4 animate-spin text-indigo-400 shrink-0" />
          <span>{uploadPhase}</span>
        </div>
      )}

      {uploadError && (
        <div className="flex items-center justify-between gap-3 px-4 py-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs font-medium animate-fadeIn">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{uploadError}</span>
          </div>
          <button
            onClick={() => setUploadError(null)}
            className="text-rose-400 hover:text-rose-200 p-1"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Active Document Status Indicator */}
      {activeDocument && (
        <div className="flex items-center justify-between px-4 py-2 bg-slate-900/90 border border-slate-800 rounded-xl text-xs">
          <div className="flex items-center gap-2 truncate">
            <FileCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <span className="text-slate-400">Active Document:</span>
            <span className="font-semibold text-slate-200 truncate">{activeDocument.title}</span>
            <span className="text-slate-500 font-mono text-[11px]">({activeDocument.filename})</span>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px]">
              {activeDocument.pages_count} Pages
            </span>
            <span className="flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Vector DB Indexed</span>
            </span>
          </div>
        </div>
      )}

      {/* Mobile Tab Switcher */}
      <div className="lg:hidden flex items-center p-1 bg-slate-900/90 rounded-xl border border-slate-800 shadow-sm">
        <button
          onClick={() => setMobileTab('chat')}
          className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-semibold transition-all ${
            mobileTab === 'chat'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          <span>Chat Assistant ({messages.length})</span>
        </button>

        <button
          onClick={() => setMobileTab('pdf')}
          className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-semibold transition-all ${
            mobileTab === 'pdf'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>PDF Viewer & Evidence</span>
          {activeCitation && (
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
            </span>
          )}
        </button>
      </div>

      {/* Citation Toast Notification */}
      {citationNotification && (
        <div className="flex items-center justify-between px-4 py-2 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-300 text-xs font-medium animate-fadeIn">
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-amber-400 animate-pulse" />
            <span>{citationNotification}</span>
          </div>
          <span className="text-[10px] text-amber-400/80">Coordinate Bounding Box Active</span>
        </div>
      )}

      {/* Main Split-Screen Workspace Container */}
      <div className="relative flex flex-col lg:flex-row items-stretch gap-0 w-full min-h-[640px]">
        {/* Left Column: Chat Assistant & Controls */}
        <div
          style={{
            width: layoutMode === 'split' ? `${splitRatio}%` : layoutMode === 'chat' ? '100%' : '0%'
          }}
          className={`${
            layoutMode === 'pdf' ? 'hidden' : 'flex flex-col'
          } ${
            mobileTab !== 'chat' ? 'hidden lg:flex' : 'flex'
          } ${
            isDragging ? 'transition-none select-none' : 'transition-[width] duration-150'
          } min-w-[280px] space-y-4`}
        >
          {/* Chat Console Panel */}
          <div className="glass-panel rounded-2xl h-[720px] flex flex-col overflow-hidden border border-slate-800 shadow-xl">
            {/* Console Header */}
            <div className="px-4 py-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-indigo-400" />
                <span className="font-semibold text-slate-200">Grounded Research & Q&A Assistant</span>
                <span className="px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 font-mono text-[10px]">
                  {selectedMarks}-Mark Mode
                </span>
              </div>

              <div className="flex items-center gap-2">
                {messages.length > 0 && (
                  <button
                    onClick={clearChatHistory}
                    className="text-slate-400 hover:text-slate-300 p-1 rounded-lg hover:bg-slate-800 transition-colors"
                    title="Clear Chat Messages"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}

                <button
                  onClick={() => setLayoutMode(layoutMode === 'chat' ? 'split' : 'chat')}
                  className="hidden lg:flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-200 px-2 py-1 rounded-lg hover:bg-slate-800 transition-colors"
                  title={layoutMode === 'chat' ? 'Restore Split View' : 'Maximize Chat'}
                >
                  {layoutMode === 'chat' ? (
                    <>
                      <Minimize2 className="w-3.5 h-3.5" />
                      <span>Split</span>
                    </>
                  ) : (
                    <>
                      <Maximize2 className="w-3.5 h-3.5" />
                      <span>Expand</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Messages Feed */}
            <div className="flex-1 p-4 overflow-y-auto space-y-4">
              {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500">
                  <FileText className="w-12 h-12 text-slate-700 mb-3" />
                  <p className="text-sm font-semibold text-slate-300">
                    {activeDocumentId
                      ? "Ask any question from this document"
                      : "No study material selected. Upload a PDF to start studying."}
                  </p>
                  <p className="text-xs text-slate-500 mt-1 max-w-xs leading-relaxed">
                    {activeDocumentId
                      ? `Answers are strictly grounded in ${activeDocument?.title || 'the active document'} and scaled according to ${selectedMarks} marks.`
                      : "Upload any course syllabus or textbook PDF to begin marks-aware Q&A and coordinate-grounded citation inspection."}
                  </p>

                  {!activeDocumentId && (
                    <>
                      <div
                        onDragOver={(e) => {
                          e.preventDefault();
                          setIsDraggingFile(true);
                        }}
                        onDragLeave={() => setIsDraggingFile(false)}
                        onDrop={(e) => {
                          e.preventDefault();
                          setIsDraggingFile(false);
                          if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                            handleFileUpload(e.dataTransfer.files[0]);
                          }
                        }}
                        onClick={() => fileInputRef.current?.click()}
                        className={`mt-6 w-full max-w-sm p-6 rounded-2xl border-2 border-dashed transition-all cursor-pointer flex flex-col items-center justify-center gap-3 ${
                          isDraggingFile
                            ? 'border-indigo-500 bg-indigo-500/10'
                            : 'border-slate-700 hover:border-indigo-500/60 bg-slate-900/60 hover:bg-slate-900'
                        }`}
                      >
                        <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                          <UploadCloud className="w-5 h-5" />
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-slate-200">
                            Click to browse or drop course PDF here
                          </p>
                          <p className="text-[11px] text-slate-500 mt-0.5">
                            Accepts selectable, scanned, or mixed PDFs
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 mt-4">
                        <span className="text-[11px] text-slate-500">or</span>
                        <button
                          onClick={handleLoadDemo}
                          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-semibold transition-all cursor-pointer shadow-sm"
                        >
                          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                          <span>Load Sample BST Demo</span>
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                messages.map((msg, idx) => (
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
                      className={`max-w-[88%] rounded-2xl p-4 text-xs leading-relaxed shadow-sm ${
                        msg.sender === 'user'
                          ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-br-none'
                          : msg.abstain
                          ? 'bg-rose-500/10 border border-rose-500/30 text-rose-200 rounded-bl-none'
                          : 'bg-slate-900/90 border border-slate-800 text-slate-200 rounded-bl-none'
                      }`}
                    >
                      {/* Answer Body */}
                      <div className="whitespace-pre-wrap font-sans">{msg.text}</div>

                      {/* Interactive Citation Badge Link */}
                      {msg.sender === 'bot' && msg.citation && (
                        <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                          <button
                            onClick={() => handleCitationClick(msg.citation)}
                            className={`flex items-center justify-between gap-2 px-3 py-2 rounded-xl text-[11px] font-semibold transition-all duration-150 border ${
                              activeCitation && activeCitation.page_number === msg.citation.page_number
                                ? 'bg-amber-500/20 border-amber-500/60 text-amber-200 shadow-md shadow-amber-500/10'
                                : 'bg-amber-500/10 border-amber-500/30 text-amber-300 hover:bg-amber-500/20 hover:border-amber-500/50'
                            }`}
                            title="Click to scroll PDF viewer to exact page & highlight bounding box"
                          >
                            <div className="flex items-center gap-1.5">
                              <Target className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
                              <span>Source Citation: Page {msg.citation.page_number}</span>
                            </div>
                            <div className="flex items-center gap-1 text-[10px] text-amber-400/90 font-mono">
                              <span>Highlight Bbox</span>
                              <ChevronRight className="w-3.5 h-3.5" />
                            </div>
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
                ))
              )}

              {loading && (
                <div className="flex gap-2 items-center text-xs text-indigo-400 animate-pulse p-2">
                  <Bot className="w-4 h-4 animate-spin" />
                  <span>Searching active document & formatting {selectedMarks}-mark schema...</span>
                </div>
              )}
              <div ref={chatMessagesEndRef} />
            </div>

            {/* Input Bar */}
            <div className="p-3 bg-slate-900 border-t border-slate-800 flex items-center gap-2">
              <input
                type="text"
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendQuery()}
                placeholder={
                  activeDocumentId
                    ? `Ask any question from ${activeDocument?.title || 'active document'}...`
                    : "Upload a PDF first to ask grounded questions..."
                }
                disabled={!activeDocumentId || loading}
                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 disabled:opacity-50 transition-colors"
              />
              <button
                onClick={() => handleSendQuery()}
                disabled={!activeDocumentId || loading || !inputQuery.trim()}
                className="p-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg shadow-indigo-600/30 transition-all duration-150 disabled:opacity-50 cursor-pointer"
                title="Send Question"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Resizable Draggable Divider */}
        {layoutMode === 'split' && (
          <div
            onMouseDown={handleMouseDown}
            onTouchStart={handleTouchStart}
            onDoubleClick={resetSplitRatio}
            className="hidden lg:flex items-center justify-center w-3 mx-1 cursor-col-resize group select-none relative z-20 hover:w-4 transition-all"
            title="Drag to resize split layout (Double-click to reset 60:40)"
          >
            <div className={`w-1 h-full rounded-full transition-all duration-150 ${
              isDragging
                ? 'bg-indigo-500 shadow-lg shadow-indigo-500/50 scale-x-150'
                : 'bg-slate-800 group-hover:bg-indigo-500/60'
            } flex items-center justify-center`}>
              <div className="p-1 rounded-full bg-slate-900 border border-slate-700 text-slate-400 group-hover:text-indigo-300 shadow-md">
                <GripVertical className="w-3.5 h-3.5" />
              </div>
            </div>

            {isDragging && (
              <div className="absolute top-4 bg-indigo-600 text-white text-[10px] font-mono px-2 py-1 rounded shadow-xl pointer-events-none whitespace-nowrap z-50">
                Chat: {splitRatio}% | Doc: {100 - splitRatio}%
              </div>
            )}
          </div>
        )}

        {/* Right Column: Split-Screen PDF Viewer */}
        <div
          ref={pdfContainerRef}
          style={{
            width: layoutMode === 'split' ? `${100 - splitRatio}%` : layoutMode === 'pdf' ? '100%' : '0%'
          }}
          className={`${
            layoutMode === 'chat' ? 'hidden' : 'flex flex-col'
          } ${
            mobileTab !== 'pdf' ? 'hidden lg:flex' : 'flex'
          } ${
            isDragging ? 'transition-none select-none' : 'transition-[width] duration-150'
          } min-w-[280px] relative`}
        >
          {layoutMode === 'pdf' && (
            <div className="mb-2 flex items-center justify-between px-4 py-2 bg-slate-900/90 border border-slate-800 rounded-xl text-xs">
              <span className="text-slate-400 font-medium">Document Fullscreen Mode</span>
              <button
                onClick={() => setLayoutMode('split')}
                className="flex items-center gap-1.5 text-indigo-400 hover:text-indigo-300 font-semibold"
              >
                <Columns className="w-3.5 h-3.5" />
                <span>Restore Split View</span>
              </button>
            </div>
          )}

          <PdfViewer
            activeDocument={activeDocument}
            activeCitation={activeCitation}
            setActiveCitation={setActiveCitation}
            selectedPage={selectedPage}
            setSelectedPage={setSelectedPage}
            onUploadClick={() => fileInputRef.current?.click()}
            onLoadDemo={handleLoadDemo}
          />
        </div>
      </div>

      {/* Diagnostic Quiz Modal */}
      <DiagnosticQuiz
        isOpen={isQuizOpen}
        onClose={() => setIsQuizOpen(false)}
        activeDocument={activeDocument}
        onLoadDemo={handleLoadDemo}
        onUploadClick={() => fileInputRef.current?.click()}
      />
    </div>
  );
}
