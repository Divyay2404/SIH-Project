// Fixed PDF viewer loading and error handling
// Fixed PDF viewer loading and error handling
import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  FileText,
  RefreshCw,
  UploadCloud
} from 'lucide-react';

/**
 * PdfViewer component displays the uploaded PDF or its extracted text.
 * It shows a loading overlay while the PDF is being prepared,
 * provides a clear error state with retry/upload actions, and
 * falls back to extracted text when native preview is unavailable.
 */
export default function PdfViewer({
  activeDocument = null,
  activeCitation = null,
  setActiveCitation,
  selectedPage = 1,
  setSelectedPage,
  onUploadClick
}) {
  const [viewerState, setViewerState] = useState('ready'); // 'ready' | 'loading' | 'failed'
  const [showExtractedText, setShowExtractedText] = useState(false);
  const pages = activeDocument?.pages || [];
  const totalPages = activeDocument ? (activeDocument.pages_count || pages.length || 1) : 0;

  const currentPage = useMemo(
    () => pages.find(page => page.page === selectedPage) || pages[0] || null,
    [pages, selectedPage]
  );

  const isPdf = activeDocument?.filename?.toLowerCase().endsWith('.pdf');
  const canUseNativePreview = Boolean(isPdf && activeDocument?.sourceUrl && !showExtractedText);
  const citationOnCurrentPage = activeCitation?.page_number === selectedPage;
  const paragraphs = currentPage?.paragraphs || currentPage?.chunks?.map(chunk => chunk.text) || [];

  // Reset extracted view and set loading state when document changes
  useEffect(() => {
    setShowExtractedText(false);
    if (activeDocument?.sourceUrl && isPdf) {
      setViewerState('loading');
    } else {
      setViewerState('ready');
    }
  }, [activeDocument?.document_id, activeDocument?.sourceUrl, isPdf]);

  if (!activeDocument) {
    return (
      <div className="glass-panel rounded-2xl flex flex-col h-[720px] items-center justify-center p-8 border border-slate-800 shadow-2xl bg-slate-950/80 text-center">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
          <FileText className="w-8 h-8" />
        </div>
        <h3 className="text-base font-bold text-slate-100 mb-2">No study material selected</h3>
        <p className="text-xs text-slate-400 max-w-sm leading-relaxed mb-6">
          Upload a course PDF to inspect the original pages and ask grounded questions.
        </p>
        {onUploadClick && (
          <button onClick={onUploadClick} className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-semibold">
            <UploadCloud className="w-4 h-4" />
            <span>Upload Course PDF</span>
          </button>
        )}
      </div>
    );
  }

  const goToPage = page => setSelectedPage?.(Math.max(1, Math.min(totalPages, page)));
  const retryNativePreview = () => {
    setShowExtractedText(false);
    setViewerState('loading');
  };

  return (
    <div className="glass-panel rounded-2xl flex flex-col h-[720px] overflow-hidden border border-slate-800 shadow-2xl bg-slate-950/80">
      {/* Header with filename and navigation */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 bg-slate-900/95 border-b border-slate-800 text-xs">
        <div className="flex min-w-0 items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <FileText className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <p className="font-semibold text-slate-200 truncate max-w-[220px]" title={activeDocument.filename}>{activeDocument.filename}</p>
            <p className="text-[10px] text-slate-400">Page {selectedPage} of {totalPages} · {canUseNativePreview ? 'Original PDF' : 'Extracted text'}</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={() => goToPage(selectedPage - 1)} disabled={selectedPage <= 1} className="p-1 rounded-lg text-slate-300 hover:bg-slate-800 disabled:opacity-40" title="Previous page"><ChevronLeft className="w-4 h-4" /></button>
          <span className="font-mono text-slate-300 px-1">{selectedPage}/{totalPages}</span>
          <button onClick={() => goToPage(selectedPage + 1)} disabled={selectedPage >= totalPages} className="p-1 rounded-lg text-slate-300 hover:bg-slate-800 disabled:opacity-40" title="Next page"><ChevronRight className="w-4 h-4" /></button>
        </div>
      </div>

      {/* Citation badge */}
      {citationOnCurrentPage && activeCitation && (
        <div className="mx-4 mt-3 flex items-start justify-between gap-3 rounded-xl border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-xs text-amber-100">
          <span><strong>Chat evidence on this page:</strong> {activeCitation.snippet}</span>
          <button onClick={() => setActiveCitation?.(null)} className="shrink-0 text-amber-300 hover:text-white">Clear</button>
        </div>
      )}

      {/* Main viewer area */}
      <div className="relative flex-1 overflow-auto bg-slate-950 p-4 sm:p-6">
        {/* Loading overlay */}
        {viewerState === 'loading' && (
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-3 bg-slate-950/90 text-slate-300 text-sm">
            <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
            <span>Preparing the original PDF…</span>
          </div>
        )}

        {/* Error overlay */}
        {viewerState === 'failed' && (
          <div className="absolute inset-0 z-20 flex items-center justify-center bg-slate-950/90 p-6">
            <div className="max-w-md rounded-2xl border border-red-500/40 bg-slate-900 p-5 text-center shadow-2xl">
              <AlertCircle className="w-7 h-7 text-red-400 mx-auto mb-3" />
              <h3 className="font-semibold text-white">The original PDF could not be displayed</h3>
              <p className="mt-2 text-sm text-slate-300">You can continue studying from extracted text, retry the preview, or upload the file again.</p>
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                <button onClick={() => { setShowExtractedText(true); setViewerState('ready'); }} className="px-3 py-2 rounded-lg bg-indigo-600 text-white text-sm font-semibold">Show extracted text</button>
                <button onClick={retryNativePreview} className="px-3 py-2 rounded-lg border border-slate-600 text-slate-200 text-sm">Retry</button>
                {onUploadClick && <button onClick={onUploadClick} className="px-3 py-2 rounded-lg border border-slate-600 text-slate-200 text-sm">Upload again</button>}
              </div>
            </div>
          </div>
        )}

        {/* Viewer content */}
        {viewerState !== 'failed' && (
          canUseNativePreview ? (
            <iframe
              key={`${activeDocument.sourceUrl}-${selectedPage}-${viewerState}`}
              src={`${activeDocument.sourceUrl}#page=${selectedPage}`}
              title={`Original PDF: ${activeDocument.filename}`}
              className="w-full h-full min-h-[590px] rounded-xl bg-white border border-slate-700"
              onLoad={() => setViewerState('ready')}
              onError={() => setViewerState('failed')}
            />
          ) : (
            <article className="mx-auto max-w-3xl min-h-[560px] rounded-xl border border-slate-700 bg-white p-6 sm:p-10 shadow-2xl">
              <p className="text-xs uppercase tracking-wider text-indigo-600 font-bold mb-3">Page {selectedPage}</p>
              <h3 className="text-slate-900 text-xl sm:text-2xl font-bold mb-6">{currentPage?.title || activeDocument.title}</h3>
              {paragraphs.length > 0 ? paragraphs.map((paragraph, idx) => (
                <p key={`${selectedPage}-${idx}`} className="text-slate-700 leading-relaxed mb-5 whitespace-pre-wrap">{paragraph}</p>
              )) : (
                <div className="text-slate-600 space-y-3">
                  <p>No readable text was extracted for this page.</p>
                  <p className="text-sm">Try another page or upload a text-based PDF. Scanned pages require OCR support on the backend.</p>
                </div>
              )}
              {isPdf && activeDocument.sourceUrl && showExtractedText && (
                <button onClick={retryNativePreview} className="mt-4 flex items-center gap-2 text-sm text-indigo-700 hover:text-indigo-900 font-semibold">
                  <RefreshCw className="w-4 h-4" /> Retry original PDF preview
                </button>
              )}
            </article>
          )
        )}
      </div>
    </div>
  );
}
