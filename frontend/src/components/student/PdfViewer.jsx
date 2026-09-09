import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  FileText,
  Target,
  Sparkles,
  CheckCircle2,
  X,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  Maximize2,
  Crosshair,
  Layers,
  Sun,
  Moon,
  UploadCloud
} from 'lucide-react';

const BASE_PAGE_WIDTH = 600;
const BASE_PAGE_HEIGHT = 820;

export default function PdfViewer({
  activeDocument = null,
  activeCitation = null,
  setActiveCitation,
  selectedPage = 1,
  setSelectedPage,
  onUploadClick
}) {
  const [zoom, setZoom] = useState(1.0);
  const [paperTheme, setPaperTheme] = useState('light'); // 'light' | 'dark'
  const [isPulsing, setIsPulsing] = useState(false);
  const [showOverlay, setShowOverlay] = useState(true);

  const canvasRef = useRef(null);
  const highlightRef = useRef(null);
  const containerRef = useRef(null);
  const pulseTimerRef = useRef(null);

  // Compute pages list from active document
  const rawPages = activeDocument?.pages || [];
  const totalPages = activeDocument
    ? (activeDocument.pages_count || (rawPages.length > 0 ? rawPages.length : 1))
    : 0;

  // Resolve current page data
  const currentPageObj = rawPages.find((p) => p.page === selectedPage) || (
    rawPages.length > 0 ? rawPages[0] : null
  );

  // Trigger pulse shockwave whenever citation changes or is re-clicked
  useEffect(() => {
    if (activeCitation && activeCitation.page_number === selectedPage) {
      setIsPulsing(true);
      if (pulseTimerRef.current) clearTimeout(pulseTimerRef.current);
      pulseTimerRef.current = setTimeout(() => {
        setIsPulsing(false);
      }, 1800);

      const scrollTimer = setTimeout(() => {
        if (highlightRef.current) {
          highlightRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 120);

      return () => {
        clearTimeout(scrollTimer);
        if (pulseTimerRef.current) clearTimeout(pulseTimerRef.current);
      };
    }
  }, [activeCitation, selectedPage, zoom]);

  // Scaled coordinate calculation: handles both unit-normalized [0..1] and base point coordinates
  const getScaledBbox = useCallback(
    (bbox) => {
      if (!bbox || !Array.isArray(bbox) || bbox.length < 4) return null;
      const [rawX0, rawY0, rawX1, rawY1] = bbox;

      const isUnit =
        rawX0 >= 0 &&
        rawX0 <= 1.01 &&
        rawY0 >= 0 &&
        rawY0 <= 1.01 &&
        rawX1 >= 0 &&
        rawX1 <= 1.01 &&
        rawY1 >= 0 &&
        rawY1 <= 1.01 &&
        (rawX1 > 0.05 || rawY1 > 0.05);

      let normX0, normY0, normX1, normY1;
      if (isUnit) {
        normX0 = rawX0;
        normY0 = rawY0;
        normX1 = rawX1;
        normY1 = rawY1;
      } else {
        normX0 = rawX0 / BASE_PAGE_WIDTH;
        normY0 = rawY0 / BASE_PAGE_HEIGHT;
        normX1 = rawX1 / BASE_PAGE_WIDTH;
        normY1 = rawY1 / BASE_PAGE_HEIGHT;
      }

      const renderedWidth = BASE_PAGE_WIDTH * zoom;
      const renderedHeight = BASE_PAGE_HEIGHT * zoom;

      const left = normX0 * renderedWidth;
      const top = normY0 * renderedHeight;
      const width = Math.max(28, (normX1 - normX0) * renderedWidth);
      const height = Math.max(22, (normY1 - normY0) * renderedHeight);

      return {
        left,
        top,
        width,
        height,
        normCoords: [normX0.toFixed(3), normY0.toFixed(3), normX1.toFixed(3), normY1.toFixed(3)],
        scaledPixelCoords: [
          Math.round(left),
          Math.round(top),
          Math.round(left + width),
          Math.round(top + height)
        ]
      };
    },
    [zoom]
  );

  // Clean HTML5 Canvas Page Rendering Engine with High-DPI / Crispness
  const renderCanvasPage = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !activeDocument) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const renderedWidth = Math.round(BASE_PAGE_WIDTH * zoom);
    const renderedHeight = Math.round(BASE_PAGE_HEIGHT * zoom);

    canvas.width = Math.round(renderedWidth * dpr);
    canvas.height = Math.round(renderedHeight * dpr);
    canvas.style.width = `${renderedWidth}px`;
    canvas.style.height = `${renderedHeight}px`;

    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr * zoom, dpr * zoom);

    const isDark = paperTheme === 'dark';
    const bgPaper = isDark ? '#0f172a' : '#ffffff';
    const textMain = isDark ? '#f1f5f9' : '#0f172a';
    const textMuted = isDark ? '#94a3b8' : '#475569';
    const textSub = isDark ? '#64748b' : '#64748b';
    const borderCol = isDark ? '#1e293b' : '#e2e8f0';
    const accentIndigo = isDark ? '#818cf8' : '#4f46e5';

    // 1. Paper Background & Margin Guidelines
    ctx.fillStyle = bgPaper;
    ctx.fillRect(0, 0, BASE_PAGE_WIDTH, BASE_PAGE_HEIGHT);

    ctx.strokeStyle = borderCol;
    ctx.lineWidth = 1;
    ctx.strokeRect(0, 0, BASE_PAGE_WIDTH, BASE_PAGE_HEIGHT);

    // 2. Running Header
    const docTitle = (activeDocument.title || activeDocument.filename || 'STUDY DOCUMENT').toUpperCase();
    ctx.fillStyle = textSub;
    ctx.font = '600 9px ui-monospace, SFMono-Regular, Menlo, Monaco, monospace';
    ctx.fillText(docTitle.slice(0, 48), 36, 32);

    ctx.textAlign = 'right';
    ctx.fillText(`PAGE ${selectedPage} OF ${totalPages}  |  OFFICIAL SYLLABUS`, BASE_PAGE_WIDTH - 36, 32);
    ctx.textAlign = 'left';

    ctx.strokeStyle = borderCol;
    ctx.beginPath();
    ctx.moveTo(36, 40);
    ctx.lineTo(BASE_PAGE_WIDTH - 36, 40);
    ctx.stroke();

    // 3. Section Title / Page Heading
    const pageTitle = currentPageObj?.title || `Page ${selectedPage} Content`;
    ctx.fillStyle = accentIndigo;
    ctx.font = '700 11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillText(`SECTION ${selectedPage}`, 36, 62);

    ctx.fillStyle = textMain;
    ctx.font = '700 16px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillText(pageTitle.slice(0, 60), 36, 84);

    // 4. Render paragraphs extracted from the document
    let cursorY = 114;
    ctx.font = '400 11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

    const paragraphs = currentPageObj?.paragraphs || [];
    if (paragraphs.length === 0) {
      ctx.fillStyle = textMuted;
      ctx.fillText('(No text paragraphs detected on this page)', 36, cursorY);
    } else {
      paragraphs.forEach((pText) => {
        if (cursorY > BASE_PAGE_HEIGHT - 60) return;
        ctx.fillStyle = textMain;
        const words = String(pText).split(' ');
        let line = '';
        const maxWidth = BASE_PAGE_WIDTH - 72;

        for (let n = 0; n < words.length; n++) {
          const testLine = line + words[n] + ' ';
          const metrics = ctx.measureText(testLine);
          if (metrics.width > maxWidth && n > 0) {
            ctx.fillText(line, 36, cursorY);
            line = words[n] + ' ';
            cursorY += 18;
            if (cursorY > BASE_PAGE_HEIGHT - 60) break;
          } else {
            line = testLine;
          }
        }
        if (cursorY <= BASE_PAGE_HEIGHT - 60) {
          ctx.fillText(line, 36, cursorY);
          cursorY += 22;
        }
      });
    }

    // 5. Academic Footer Rule & Grounded Evidence Stamp
    ctx.strokeStyle = borderCol;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(36, BASE_PAGE_HEIGHT - 38);
    ctx.lineTo(BASE_PAGE_WIDTH - 36, BASE_PAGE_HEIGHT - 38);
    ctx.stroke();

    ctx.fillStyle = textSub;
    ctx.font = '600 8.5px ui-monospace, monospace';
    ctx.fillText(`STUDYFORGE REPOSITORY • DOC ID: ${activeDocument.document_id || 'ACTIVE'}`, 36, BASE_PAGE_HEIGHT - 22);

    ctx.textAlign = 'right';
    ctx.fillStyle = isDark ? '#34d399' : '#059669';
    ctx.fillText('✓ TEXTBOOK EVIDENCE CERTIFIED', BASE_PAGE_WIDTH - 36, BASE_PAGE_HEIGHT - 22);
    ctx.textAlign = 'left';
  }, [selectedPage, zoom, paperTheme, activeDocument, totalPages, currentPageObj]);

  // Re-render canvas whenever page, zoom, theme, or activeDocument changes
  useEffect(() => {
    renderCanvasPage();
  }, [renderCanvasPage]);

  // Bounding box data resolution
  const bboxToRender =
    activeCitation && activeCitation.page_number === selectedPage
      ? activeCitation.bounding_box
      : null;

  const scaledBbox = bboxToRender ? getScaledBbox(bboxToRender) : null;

  // Zoom handlers
  const handleZoomIn = () => setZoom((prev) => Math.min(2.0, parseFloat((prev + 0.15).toFixed(2))));
  const handleZoomOut = () => setZoom((prev) => Math.max(0.5, parseFloat((prev - 0.15).toFixed(2))));
  const handleResetZoom = () => setZoom(1.0);
  const handleFitWidth = () => {
    if (containerRef.current) {
      const containerWidth = containerRef.current.clientWidth - 48;
      const fitZoom = Math.max(0.5, Math.min(1.75, containerWidth / BASE_PAGE_WIDTH));
      setZoom(parseFloat(fitZoom.toFixed(2)));
    } else {
      setZoom(1.0);
    }
  };

  // If no document is uploaded, render clear empty state
  if (!activeDocument) {
    return (
      <div className="glass-panel rounded-2xl flex flex-col h-[720px] items-center justify-center p-8 border border-slate-800 shadow-2xl bg-slate-950/80 backdrop-blur-xl text-center">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4 shadow-lg shadow-indigo-500/10">
          <FileText className="w-8 h-8" />
        </div>
        <h3 className="text-base font-bold text-slate-100 mb-2">No study material selected</h3>
        <p className="text-xs text-slate-400 max-w-sm leading-relaxed mb-6">
          Upload any course notes, syllabus, or textbook PDF to inspect pages, examine formulas, and verify coordinate-grounded source citations.
        </p>
        {onUploadClick && (
          <button
            onClick={onUploadClick}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold shadow-lg shadow-indigo-500/20 transition-all duration-150"
          >
            <UploadCloud className="w-4 h-4" />
            <span>Upload Course PDF</span>
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl flex flex-col h-[720px] overflow-hidden border border-slate-800 shadow-2xl bg-slate-950/80 backdrop-blur-xl">
      {/* Top Professional Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 bg-slate-900/95 border-b border-slate-800 text-xs">
        {/* Document Identifier */}
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-slate-200 tracking-tight truncate max-w-[200px]" title={activeDocument.filename}>
                {activeDocument.filename}
              </span>
              <span className="px-2 py-0.5 text-[10px] font-mono font-medium bg-slate-800 text-indigo-300 rounded-md border border-slate-700/80">
                Page {selectedPage} of {totalPages}
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono hidden sm:block">
              Canvas Render Engine: 600×820 @ {Math.round(zoom * 100)}% Zoom
            </p>
          </div>
        </div>

        {/* Zoom & View Controls */}
        <div className="flex items-center gap-1.5 bg-slate-950/60 p-1 rounded-xl border border-slate-800">
          <button
            onClick={handleZoomOut}
            disabled={zoom <= 0.5}
            className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/80 disabled:opacity-40 disabled:hover:bg-transparent transition-colors"
            title="Zoom Out (-15%)"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>

          <span
            onClick={handleResetZoom}
            className="px-2 py-0.5 text-[11px] font-mono font-semibold text-slate-300 hover:text-white cursor-pointer select-none rounded hover:bg-slate-800/60 transition-colors"
            title="Click to reset zoom to 100%"
          >
            {Math.round(zoom * 100)}%
          </span>

          <button
            onClick={handleZoomIn}
            disabled={zoom >= 2.0}
            className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/80 disabled:opacity-40 disabled:hover:bg-transparent transition-colors"
            title="Zoom In (+15%)"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>

          <div className="w-[1px] h-4 bg-slate-800 mx-0.5" />

          <button
            onClick={handleFitWidth}
            className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/80 transition-colors"
            title="Fit to Container Width"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={handleResetZoom}
            className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/80 transition-colors"
            title="Reset Zoom (100%)"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          <div className="w-[1px] h-4 bg-slate-800 mx-0.5" />

          {/* Paper Theme Toggle */}
          <button
            onClick={() => setPaperTheme((t) => (t === 'light' ? 'dark' : 'light'))}
            className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/80 transition-colors"
            title={`Switch to ${paperTheme === 'light' ? 'Dark' : 'Light'} Paper Mode`}
          >
            {paperTheme === 'light' ? <Moon className="w-3.5 h-3.5" /> : <Sun className="w-3.5 h-3.5 text-amber-400" />}
          </button>

          {/* Overlay Visibility Toggle */}
          <button
            onClick={() => setShowOverlay((v) => !v)}
            className={`p-1.5 rounded-lg transition-colors ${
              showOverlay ? 'text-amber-400 bg-amber-500/10' : 'text-slate-400 hover:bg-slate-800/80'
            }`}
            title={showOverlay ? 'Hide Highlight Overlay' : 'Show Highlight Overlay'}
          >
            <Layers className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Page Navigator */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => setSelectedPage && setSelectedPage((p) => Math.max(1, p - 1))}
            disabled={selectedPage <= 1}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 disabled:opacity-30 transition-colors"
            title="Previous Page"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          {totalPages <= 6 ? (
            Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
              <button
                key={p}
                onClick={() => setSelectedPage && setSelectedPage(p)}
                className={`w-7 h-7 rounded-lg text-xs font-semibold transition-all duration-150 ${
                  selectedPage === p
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/30'
                    : 'bg-slate-800/80 text-slate-400 hover:bg-slate-700 hover:text-slate-200'
                }`}
              >
                {p}
              </button>
            ))
          ) : (
            <span className="px-2 text-xs font-mono text-slate-300">
              {selectedPage} / {totalPages}
            </span>
          )}

          <button
            onClick={() => setSelectedPage && setSelectedPage((p) => Math.min(totalPages, p + 1))}
            disabled={selectedPage >= totalPages}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 disabled:opacity-30 transition-colors"
            title="Next Page"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Document Viewer Canvas & SVG Overlay Viewport */}
      <div
        ref={containerRef}
        className="relative flex-1 p-6 overflow-auto bg-slate-950/80 flex flex-col items-center justify-start select-none"
      >
        {/* Dynamic Zoom Container */}
        <div
          className="relative transition-transform duration-200 ease-out origin-top shadow-2xl rounded-xl"
          style={{
            width: `${Math.round(BASE_PAGE_WIDTH * zoom)}px`,
            minHeight: `${Math.round(BASE_PAGE_HEIGHT * zoom)}px`
          }}
        >
          {/* 1. High-DPI HTML5 Clean Canvas Renderer */}
          <canvas
            ref={canvasRef}
            className="rounded-xl shadow-2xl block"
            style={{
              width: `${Math.round(BASE_PAGE_WIDTH * zoom)}px`,
              height: `${Math.round(BASE_PAGE_HEIGHT * zoom)}px`
            }}
          />

          {/* 2. Scaled SVG / Canvas Bounding Box Highlight Overlay */}
          {showOverlay && scaledBbox && (
            <div
              ref={highlightRef}
              className={`bbox-highlight ${isPulsing ? 'is-bursting' : ''}`}
              style={{
                top: `${scaledBbox.top}px`,
                left: `${scaledBbox.left}px`,
                width: `${scaledBbox.width}px`,
                height: `${scaledBbox.height}px`
              }}
            >
              {/* Expanding Shockwave Radar Ring on Trigger */}
              {isPulsing && <div className="bbox-shockwave-ring" />}

              {/* Corner crosshairs for technical precision */}
              <div className="absolute -top-1.5 -left-1.5 w-3 h-3 border-t-2 border-orange-400 rounded-tl-sm pointer-events-none" />
              <div className="absolute -top-1.5 -right-1.5 w-3 h-3 border-t-2 border-r-2 border-orange-400 rounded-tr-sm pointer-events-none" />
              <div className="absolute -bottom-1.5 -left-1.5 w-3 h-3 border-b-2 border-l-2 border-orange-400 rounded-bl-sm pointer-events-none" />
              <div className="absolute -bottom-1.5 -right-1.5 w-3 h-3 border-b-2 border-r-2 border-orange-400 rounded-br-sm pointer-events-none" />

              {/* Floating Coordinate HUD Badge */}
              <div className="absolute -top-8 left-0 bg-gradient-to-r from-orange-600 to-amber-600 text-white text-[10px] font-bold px-2.5 py-1 rounded-lg shadow-xl flex items-center justify-between gap-2.5 whitespace-nowrap z-40 border border-orange-400/40">
                <div className="flex items-center gap-1.5">
                  <Crosshair className={`w-3.5 h-3.5 ${isPulsing ? 'animate-spin' : ''} text-white`} />
                  <span>
                    Citation Bbox [{scaledBbox.scaledPixelCoords.join(', ')}]
                  </span>
                  <span className="text-[9px] font-mono bg-orange-950/50 px-1.5 py-0.2 rounded border border-orange-400/30 text-orange-200">
                    {Math.round(zoom * 100)}%
                  </span>
                </div>

                {setActiveCitation && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setActiveCitation(null);
                    }}
                    className="hover:bg-orange-700/80 p-0.5 rounded text-white/90 hover:text-white transition-colors ml-1"
                    title="Dismiss highlight overlay"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </div>

              {/* Snippet Context Callout Tooltip */}
              {activeCitation && activeCitation.snippet && (
                <div className="absolute -bottom-8 left-0 max-w-[340px] truncate bg-slate-900/90 text-slate-300 text-[10px] px-2 py-0.5 rounded border border-slate-700 shadow-lg pointer-events-none hidden sm:block">
                  <span className="text-orange-400 font-semibold">Evidence: </span>
                  {activeCitation.snippet}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Footer Citation Status Bar */}
      <div className="px-4 py-2.5 bg-slate-900/95 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-slate-300 text-[11px]">
            {activeCitation && activeCitation.page_number === selectedPage
              ? `Real-Time Highlight Active: Page ${activeCitation.page_number} (${Math.round(zoom * 100)}% Zoom)`
              : 'Click any citation badge in the chat console to trigger real-time bounding box highlight'}
          </span>
        </div>

        <div className="flex items-center gap-3 text-[11px]">
          {scaledBbox && (
            <span className="font-mono text-slate-400 hidden md:inline">
              Normalized: [{scaledBbox.normCoords.join(', ')}]
            </span>
          )}
          <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Canvas Grounding Verified</span>
          </div>
        </div>
      </div>
    </div>
  );
}
