import React, { useState } from 'react';
import Header from './components/common/Header';
import StudentPortal from './components/student/StudentPortal';
import EducatorConsole from './components/educator/EducatorConsole';

export default function App() {
  const [activeTab, setActiveTab] = useState('student');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      {/* Top Navigation */}
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-6 pb-12 flex-1 w-full">
        {activeTab === 'student' ? (
          <StudentPortal />
        ) : (
          <EducatorConsole />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500 bg-slate-950/80">
        <p>StudyForge OS — AI-Powered Adaptive Learning & Content Generation Platform</p>
      </footer>
    </div>
  );
}
