import React, { useState } from 'react';
import { Upload, Presentation, FileText, CheckCircle, Sparkles, FolderPlus } from 'lucide-react';
import WeaknessHeatmap from './WeaknessHeatmap';
import { apiUrl } from '../../config/api';

export default function EducatorConsole() {
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [downloadingPpt, setDownloadingPpt] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formattedSize = (file.size / 1024 / 1024).toFixed(2) + " MB";
    setUploading(true);
    setUploadStatus({
      name: file.name,
      size: formattedSize,
      status: "Extracting document content..."
    });

    try {
      const formData = new FormData();
      formData.append('file', file);

      let response;
      try {
        response = await fetch(apiUrl('/api/ingest'), { method: 'POST', body: formData });
      } catch (networkErr) {
        throw new Error('Server unreachable. Please verify that the backend service is running.');
      }

      const contentType = response.headers.get('content-type') || '';
      const isJson = contentType.includes('application/json');

      if (!response.ok) {
        if (isJson) {
          try {
            const errorPayload = await response.json();
            throw new Error(errorPayload.detail || `Ingestion error (HTTP ${response.status})`);
          } catch (jsonErr) {
            if (jsonErr.message && !jsonErr.message.includes('Unexpected token')) {
              throw jsonErr;
            }
          }
        }

        // Handle non-JSON responses (e.g. 404, 502, 504 plain text/HTML)
        if (response.status === 404) {
          throw new Error('Server unavailable (HTTP 404): Upload endpoint not found.');
        } else if (response.status === 502 || response.status === 503 || response.status === 504) {
          throw new Error(`Server gateway error (HTTP ${response.status}). Please check backend status.`);
        } else {
          throw new Error(`Server returned an unexpected response (HTTP ${response.status}).`);
        }
      }

      if (!isJson) {
        throw new Error('Server returned an unexpected response format.');
      }

      const payload = await response.json();
      setUploadStatus({
        name: file.name,
        size: formattedSize,
        documentId: payload.document_id,
        title: payload.title,
        status: `${payload.chunks_extracted} sections extracted and ready for export`
      });
    } catch (err) {
      setUploadStatus((prev) => ({
        name: file.name,
        size: formattedSize,
        error: err.message,
        status: 'Upload failed'
      }));
    } finally {
      setUploading(false);
      if (e.target) e.target.value = '';
    }
  };

  // Trigger actual file download without navigating browser to 404 page
  const handleExportPPT = async () => {
    if (!uploadStatus?.documentId) return;
    setDownloadingPpt(true);
    try {
      const res = await fetch(apiUrl(`/api/export/ppt?document_id=${encodeURIComponent(uploadStatus.documentId)}`));
      if (res.ok) {
        const blob = await res.blob();
        downloadBlob(blob, `Lecture_${safeFilename(uploadStatus.title)}.pptx`);
      } else {
        throw new Error('The lecture deck could not be generated.');
      }
    } catch (err) {
      setUploadStatus((current) => ({ ...current, error: err.message }));
    } finally {
      setTimeout(() => setDownloadingPpt(false), 1000);
    }
  };

  const handleExportPDF = async () => {
    if (!uploadStatus?.documentId) return;
    setDownloadingPdf(true);
    try {
      const res = await fetch(apiUrl(`/api/export/pdf?document_id=${encodeURIComponent(uploadStatus.documentId)}`));
      if (res.ok) {
        const blob = await res.blob();
        downloadBlob(blob, `Study_Guide_${safeFilename(uploadStatus.title)}.pdf`);
      } else {
        throw new Error('The study handout could not be generated.');
      }
    } catch (err) {
      setUploadStatus((current) => ({ ...current, error: err.message }));
    } finally {
      setTimeout(() => setDownloadingPdf(false), 1000);
    }
  };

  const downloadBlob = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const safeFilename = (title) => (title || 'Uploaded_Document').replace(/[^a-z0-9]+/gi, '_');

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
              disabled={downloadingPpt || !uploadStatus?.documentId}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white font-semibold text-xs shadow-lg shadow-orange-600/20 transition-all duration-150 cursor-pointer disabled:opacity-50"
            >
              <Presentation className="w-4 h-4" />
              <span>{downloadingPpt ? "Downloading PPT..." : "Generate Lecture Deck (.pptx)"}</span>
            </button>

            <button
              onClick={handleExportPDF}
              disabled={downloadingPdf || !uploadStatus?.documentId}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/20 transition-all duration-150 cursor-pointer disabled:opacity-50"
            >
              <FileText className="w-4 h-4" />
              <span>{downloadingPdf ? "Downloading PDF..." : "Export Study Handout (.pdf)"}</span>
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
            accept=".pdf"
            onChange={handleFileUpload}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto mb-3 border border-indigo-500/20">
            <FolderPlus className="w-6 h-6" />
          </div>
          <h4 className="text-xs font-semibold text-slate-200">Drop a textbook chapter or syllabus PDF here</h4>
          <p className="text-[11px] text-slate-400 mt-1">Exports use the text extracted from this PDF, including scanned notes with OCR where available</p>
        </div>

        {uploadStatus && (
          <div className={`mt-4 p-3.5 rounded-xl flex items-center justify-between text-xs ${uploadStatus.error ? 'bg-red-500/10 border border-red-500/30 text-red-300' : 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-300'}`}>
            <div className="flex items-center gap-2">
              <CheckCircle className={`w-4 h-4 ${uploadStatus.error ? 'text-red-400' : 'text-emerald-400'}`} />
              <span>{uploadStatus.name} ({uploadStatus.size})</span>
            </div>
            <span className="font-semibold">{uploading ? 'Uploading...' : uploadStatus.error || uploadStatus.status}</span>
          </div>
        )}
      </div>

      {/* Class Mastery & Error Heatmap */}
      <WeaknessHeatmap />
    </div>
  );
}
