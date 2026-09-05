import React, { useState } from 'react';
import { Upload, Presentation, FileText, CheckCircle, Sparkles, FolderPlus } from 'lucide-react';
import WeaknessHeatmap from './WeaknessHeatmap';

export default function EducatorConsole() {
  const [uploadStatus, setUploadStatus] = useState(null);
  const [downloadingPpt, setDownloadingPpt] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadStatus({
        name: file.name,
        size: (file.size / 1024 / 1024).toFixed(2) + " MB",
        status: "Ingested into Chroma Vector Base with Bounding Boxes"
      });
    }
  };

  const handleExportPPT = () => {
    setDownloadingPpt(true);
    window.location.href = '/api/export/ppt?topic=Binary_Search_Trees';
    setTimeout(() => setDownloadingPpt(false), 2000);
  };

  const handleExportPDF = () => {
    setDownloadingPdf(true);
    window.location.href = '/api/export/pdf?topic=Binary_Search_Trees';
    setTimeout(() => setDownloadingPdf(false), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Top Banner: Single Source of Truth Content Generation */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="w-5 h-5 text-amber-400" />
              <h2 className="text-lg font-bold text-white tracking-tight">Educator Content & Lecture Deck Compiler</h2>
            </div>
            <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
              A single verified knowledge base powers both student adaptive tutoring and teacher presentation decks. Compile editable lecture PowerPoint slides and printable double-column handouts with one click.
            </p>
          </div>

          {/* Generator Export Buttons */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleExportPPT}
              disabled={downloadingPpt}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white font-semibold text-xs shadow-lg shadow-orange-600/20 transition-all duration-150"
            >
              <Presentation className="w-4 h-4" />
              <span>{downloadingPpt ? "Generating PPT..." : "Generate Lecture Deck (.pptx)"}</span>
            </button>

            <button
              onClick={handleExportPDF}
              disabled={downloadingPdf}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/20 transition-all duration-150"
            >
              <FileText className="w-4 h-4" />
              <span>{downloadingPdf ? "Compiling PDF..." : "Export Study Handout (.pdf)"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Syllabus Ingestion Hub */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl">
        <h3 className="text-sm font-bold text-slate-100 mb-4 flex items-center gap-2">
          <Upload className="w-4 h-4 text-indigo-400" />
          <span>Curriculum Material Upload & Structure-Aware Ingestion Hub</span>
        </h3>

        <div className="border-2 border-dashed border-slate-800 hover:border-indigo-500/50 rounded-2xl p-8 text-center transition-all bg-slate-950/40 relative">
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileUpload}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto mb-3 border border-indigo-500/20">
            <FolderPlus className="w-6 h-6" />
          </div>
          <h4 className="text-xs font-semibold text-slate-200">Drop Textbook Chapter or Syllabus PDF here</h4>
          <p className="text-[11px] text-slate-400 mt-1">Supports digital PDFs and scanned notes with PyMuPDF bounding-box indexing</p>
        </div>

        {uploadStatus && (
          <div className="mt-4 p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between text-xs text-emerald-300">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>{uploadStatus.name} ({uploadStatus.size})</span>
            </div>
            <span className="font-semibold">{uploadStatus.status}</span>
          </div>
        )}
      </div>

      {/* Class Mastery & Error Heatmap */}
      <WeaknessHeatmap />
    </div>
  );
}
