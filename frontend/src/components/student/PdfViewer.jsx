import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  FileText,
  RefreshCw,
  UploadCloud,
  Sparkles,
  Target,
  X
} from 'lucide-react';

/**
 * PdfViewer component displays the uploaded PDF or its extracted text.
 * Navigates native PDF preview to cited pages via URL fragment (#page=N),
 * renders real-time coordinate bounding box highlight overlays with glowing borders & crosshairs,
 * provides extracted text fallback with snippet highlighting,
 * and maintains resilient error recovery.
 */
export default function PdfViewer({
  activeDocument = null,
  activeCitation = null,
  setActiveCitation,
  selectedPage = 1,
  setSelectedPage,
  onUploadClick,
  onLoadDemo
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
  const citationOnCurrentPage = Boolean(activeCitation && activeCitation.page_number === selectedPage);
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

  // If loading takes too long, show error fallback
  useEffect(() => {
    if (viewerState !== 'loading') return;
    const timeout = setTimeout(() => setViewerState('failed'), 8000); // 8 s
    return () => clearTimeout(timeout);
  }, [viewerState]);

  // Calculate scaled bounding box coordinates for overlay
  const scaledBbox = useMemo(() => {
    if (!activeCitation?.bounding_box || !Array.isArray(activeCitation.bounding_box) || activeCitation.bounding_box.length < 4) {
      return null;
    }
    const [x0, y0, x1, y1] = activeCitation.bounding_box;
    const isNorm = (x0 <= 1.0 && x1 <= 1.0 && y0 <= 1.0 && y1 <= 1.0);
    const leftPercent = isNorm ? x0 * 100 : Math.max(2, Math.min(90, (x0 / 612) * 100));
    const topPercent = isNorm ? y0 * 100 : Math.max(4, Math.min(90, (y0 / 792) * 100));
    const widthPercent = isNorm
      ? Math.max(10, (x1 - x0) * 100)
      : Math.max(15, Math.min(100 - leftPercent, ((x1 - x0) / 612) * 100));
    const heightPercent = isNorm
      ? Math.max(6, (y1 - y0) * 100)
      : Math.max(6, Math.min(100 - topPercent, ((y1 - y0) / 792) * 100));

    return {
      left: `${leftPercent.toFixed(1)}%`,
      top: `${topPercent.toFixed(1)}%`,
      width: `${widthPercent.toFixed(1)}%`,
      height: `${heightPercent.toFixed(1)}%`,
      coords: [Math.round(x0), Math.round(y0), Math.round(x1), Math.round(y1)]
    };
  }, [activeCitation]);

  if (!activeDocument) {
    return (
      <div className="glass-panel rounded-2xl flex flex-col h-[720px] items-center justify-center p-8 border border-slate-800 shadow-2xl bg-slate-950/80 text-center">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
          <FileText className="w-8 h-8" />
        </div>
        <h3 className="text-base font-bold text-slate-100 mb-2">No study material selected</h3>
        <p className="text-xs text-slate-400 max-w-sm leading-relaxed mb-6">
          Upload any course notes, syllabus, or textbook PDF to inspect original pages and ask grounded questions.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3">
          {onUploadClick && (
            <button
              onClick={onUploadClick}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-semibold hover:from-indigo-500 hover:to-purple-500 transition-all cursor-pointer"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Upload Course PDF</span>
            </button>
          )}
          {onLoadDemo && (
            <button
              onClick={onLoadDemo}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-semibold transition-all cursor-pointer"
            >
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>Load Sample BST Demo</span>
            </button>
          )}
        </div>
      </div>
    );
  }

  const goToPage = page => setSelectedPage?.(Math.max(1, Math.min(totalPages, page)));
  const retryNativePreview = () => {
    setShowExtractedText(false);
    setViewerState('loading');
  };

  const nativeIframeUrl = activeDocument.sourceUrl
    ? `${activeDocument.sourceUrl}#page=${selectedPage}&zoom=100`
    : '';

  return (
    <div className="glass-panel rounded-2xl flex flex-col h-[720px] overflow-hidden border border-slate-800 shadow-2xl bg-slate-950/80">
      {/* Header with filename and navigation */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 bg-slate-900/95 border-b border-slate-800 text-xs">
        <div className="flex min-w-0 items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <FileText className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <p className="font-semibold text-slate-200 truncate max-w-[220px]" title={activeDocument.filename}>
              {activeDocument.filename}
            </p>
            <p className="text-[10px] text-slate-400">
              Page {selectedPage} of {totalPages} · Canvas Render Engine · {canUseNativePreview ? 'Original PDF' : 'Extracted text'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => goToPage(selectedPage - 1)}
            disabled={selectedPage <= 1}
            className="p-1 rounded-lg text-slate-300 hover:bg-slate-800 disabled:opacity-40 cursor-pointer"
            title="Previous page"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="font-mono text-slate-300 px-1">{selectedPage}/{totalPages}</span>
          <button
            onClick={() => goToPage(selectedPage + 1)}
            disabled={selectedPage >= totalPages}
            className="p-1 rounded-lg text-slate-300 hover:bg-slate-800 disabled:opacity-40 cursor-pointer"
            title="Next page"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Citation banner */}
      {citationOnCurrentPage && activeCitation && (
        <div className="mx-4 mt-3 flex items-start justify-between gap-3 rounded-xl border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-xs text-amber-100 animate-in fade-in duration-200">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-amber-300">Evidence:</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-200 border border-amber-500/30 font-mono">
                Citation Bbox [{activeCitation.bounding_box ? activeCitation.bounding_box.map(n => Math.round(n)).join(', ') : 'Active'}]
              </span>
            </div>
            <p className="leading-relaxed">{activeCitation.snippet}</p>
          </div>
          <button
            onClick={() => setActiveCitation?.(null)}
            className="shrink-0 text-amber-300 hover:text-white cursor-pointer"
            title="Dismiss citation highlight"
          >
            Clear
          </button>
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
              <p className="mt-2 text-sm text-slate-300">
                You can continue studying from extracted text, retry the preview, or upload the file again.
              </p>
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                <button
                  onClick={() => { setShowExtractedText(true); setViewerState('ready'); }}
                  className="px-3 py-2 rounded-lg bg-indigo-600 text-white text-sm font-semibold cursor-pointer"
                >
                  Show extracted text
                </button>
                <button
                  onClick={retryNativePreview}
                  className="px-3 py-2 rounded-lg border border-slate-600 text-slate-200 text-sm cursor-pointer"
                >
                  Retry
                </button>
                {onUploadClick && (
                  <button
                    onClick={onUploadClick}
                    className="px-3 py-2 rounded-lg border border-slate-600 text-slate-200 text-sm cursor-pointer"
                  >
                    Upload again
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Viewer content */}
        {viewerState !== 'failed' && (
          canUseNativePreview ? (
            <div className="relative w-full h-full min-h-[590px]">
              <iframe
                key={`${activeDocument.sourceUrl}-${selectedPage}-${viewerState}`}
                src={nativeIframeUrl}
                title={`Original PDF: ${activeDocument.filename}`}
                className="w-full h-full min-h-[590px] rounded-xl bg-white border border-slate-700 block"
                onLoad={() => setViewerState('ready')}
                onError={() => setViewerState('failed')}
              />

              {/* Precise Coordinate Bounding Box Overlay Highlight */}
              {citationOnCurrentPage && scaledBbox && (
                <div
                  className="absolute pointer-events-none z-30 transition-all duration-300 rounded-lg border-2 border-amber-500 bg-amber-500/20 shadow-[0_0_20px_rgba(245,158,11,0.5)]"
                  style={{
                    left: scaledBbox.left,
                    top: scaledBbox.top,
                    width: scaledBbox.width,
                    height: scaledBbox.height
                  }}
                >
                  {/* Corner Crosshairs */}
                  <div className="absolute -top-1 -left-1 w-2.5 h-2.5 border-t-2 border-l-2 border-amber-400" />
                  <div className="absolute -top-1 -right-1 w-2.5 h-2.5 border-t-2 border-r-2 border-amber-400" />
                  <div className="absolute -bottom-1 -left-1 w-2.5 h-2.5 border-b-2 border-l-2 border-amber-400" />
                  <div className="absolute -bottom-1 -right-1 w-2.5 h-2.5 border-b-2 border-r-2 border-amber-400" />

                  {/* Floating Coordinate HUD Badge */}
                  <div className="absolute -top-7 left-0 pointer-events-auto bg-gradient-to-r from-amber-600 to-orange-600 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-lg flex items-center gap-1.5 whitespace-nowrap">
                    <Target className="w-3 h-3 text-white" />
                    <span>Citation Bbox [{scaledBbox.coords.join(', ')}]</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setActiveCitation?.(null);
                      }}
                      className="hover:text-amber-200 ml-1 cursor-pointer"
                      title="Dismiss highlight"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <article className="relative mx-auto max-w-3xl min-h-[560px] rounded-xl border border-slate-700 bg-white p-6 sm:p-10 shadow-2xl">
              <p className="text-xs uppercase tracking-wider text-indigo-600 font-bold mb-3">Page {selectedPage}</p>
              <h3 className="text-slate-900 text-xl sm:text-2xl font-bold mb-6">
                {currentPage?.title || activeDocument.title}
              </h3>

              {/* Bounding box badge in extracted text view */}
              {citationOnCurrentPage && scaledBbox && (
                <div className="mb-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border border-amber-500 bg-amber-50 text-amber-900 text-xs font-semibold shadow-sm">
                  <Target className="w-4 h-4 text-amber-600" />
                  <span>Citation Evidence Highlight Active [{scaledBbox.coords.join(', ')}]</span>
                </div>
              )}

              {paragraphs.length > 0 ? paragraphs.map((paragraph, idx) => {
                const isCited = citationOnCurrentPage && activeCitation?.snippet && (
                  paragraph.toLowerCase().includes(activeCitation.snippet.toLowerCase().slice(0, 30)) ||
                  activeCitation.snippet.toLowerCase().includes(paragraph.toLowerCase().slice(0, 30))
                );

                return (
                  <p
                    key={`${selectedPage}-${idx}`}
                    className={`leading-relaxed mb-5 whitespace-pre-wrap rounded-lg transition-colors p-2.5 ${
                      isCited
                        ? 'bg-amber-100/80 text-amber-950 font-medium border-l-4 border-amber-500 shadow-sm'
                        : 'text-slate-700'
                    }`}
                  >
                    {paragraph}
                  </p>
                );
              }) : (
                <div className="text-slate-600 space-y-3">
                  <p>No readable text was extracted for this page.</p>
                  <p className="text-sm">
                    Try another page or upload a text-based PDF. Scanned pages require OCR support on the backend.
                  </p>
                </div>
              )}

              {isPdf && activeDocument.sourceUrl && showExtractedText && (
                <button
                  onClick={retryNativePreview}
                  className="mt-4 flex items-center gap-2 text-sm text-indigo-700 hover:text-indigo-900 font-semibold cursor-pointer"
                >
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
