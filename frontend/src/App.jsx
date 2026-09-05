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
      <footer className="border-t border-slate-900 py-4 text-center text-xs text-slate-500">
        <p>Smart India Hackathon (SIH) 2026 Prototype Submission | Developed by Team <span className="text-indigo-400 font-semibold">Tech_Warriors</span></p>
      </footer>
    </div>
  );
}
