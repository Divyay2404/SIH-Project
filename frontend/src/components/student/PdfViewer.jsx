import React from 'react';
import { FileText, Target, Sparkles, CheckCircle2, Eye } from 'lucide-react';

export default function PdfViewer({ activeCitation, selectedPage, setSelectedPage }) {
  const pagesData = [
    {
      page: 1,
      title: "Page 1: BST Definitions & Core Properties",
      content: [
        "CHAPTER 4: BINARY SEARCH TREES (BST)",
        "A Binary Search Tree is a node-based binary tree data structure with the strict property:",
        "• The left subtree of a node contains only nodes with keys lesser than the node's key.",
        "• The right subtree of a node contains only nodes with keys greater than the node's key.",
        "• Both left and right subtrees must also be binary search trees."
      ]
    },
    {
      page: 2,
      title: "Page 2: BST Insertion Algorithm",
      content: [
        "SECTION 4.2: INSERTION ALGORITHM",
        "Inserting a key K into a BST recursively compares K against current node:",
        "1. If root is NULL, create a new node with key K.",
        "2. If K < root.key, recurse into left child branch: root.left = insert(root.left, K).",
        "3. If K > root.key, recurse into right child branch: root.right = insert(root.right, K).",
        "4. Return root pointer."
      ]
    },
    {
      page: 3,
      title: "Page 3: BST Deletion Algorithm (3 Cases)",
      content: [
        "SECTION 4.3: DELETION ALGORITHM & IN-ORDER SUCCESSOR",
        "Deleting a target node requires handling 3 distinct cases:",
        "• Case 1 (Leaf Node): Unlink and delete directly.",
        "• Case 2 (Single Child): Splice parent pointer directly to existing child.",
        "• Case 3 (Two Children): Find In-Order Successor (smallest node in right subtree). Copy successor key to target node, then recursively delete successor."
      ]
    },
    {
      page: 4,
      title: "Page 4: Time & Space Complexity Analysis",
      content: [
        "SECTION 4.4: COMPLEXITY & CORNER CASES",
        "Time Complexity Analysis:",
        "• Search, Insertion, Deletion: Average Case O(log N) for balanced trees.",
        "• Worst Case: O(N) when tree degenerates into a single skewed linear branch.",
        "• Space Complexity: O(h) auxiliary recursive call stack space."
      ]
    }
  ];

  const currentPageObj = pagesData.find(p => p.page === selectedPage) || pagesData[2];

  return (
    <div className="glass-panel rounded-2xl flex flex-col h-[720px] overflow-hidden border border-slate-800 shadow-xl">
      {/* Top Toolbar */}
      <div className="flex items-center justify-between px-4 py-3 bg-slate-900/90 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-indigo-400" />
          <span className="text-xs font-semibold text-slate-200">
            Binary_Search_Trees_Chapter.pdf
          </span>
          <span className="px-2 py-0.5 text-[10px] font-medium bg-slate-800 text-slate-400 rounded-md border border-slate-700">
            Page {selectedPage} of 4
          </span>
        </div>

        {/* Page selector */}
        <div className="flex items-center gap-1">
          {[1, 2, 3, 4].map((p) => (
            <button
              key={p}
              onClick={() => setSelectedPage(p)}
              className={`w-7 h-7 rounded-lg text-xs font-semibold transition-all duration-150 ${
                selectedPage === p
                  ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-500/30'
                  : 'bg-slate-800/80 text-slate-400 hover:bg-slate-700 hover:text-slate-200'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Main Document Viewer Canvas */}
      <div className="relative flex-1 p-6 overflow-y-auto bg-slate-950/70 flex flex-col items-center">
        {/* Synthetic Document Paper Page */}
        <div className="relative w-full max-w-xl bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-2xl min-h-[580px]">
          {/* Document Header */}
          <div className="border-b border-slate-800/80 pb-3 mb-4 flex justify-between items-center">
            <span className="text-xs font-mono font-medium text-slate-400">{currentPageObj.title}</span>
            <span className="text-[10px] text-indigo-400 font-mono bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded-full flex items-center gap-1">
              <Eye className="w-3 h-3 text-indigo-400" /> Grounded Source
            </span>
          </div>

          {/* Document Paragraphs */}
          <div className="space-y-4 text-xs leading-relaxed text-slate-300">
            {currentPageObj.content.map((paragraph, idx) => (
              <p key={idx} className={idx === 0 ? "font-bold text-slate-100 text-sm tracking-tight" : ""}>
                {paragraph}
              </p>
            ))}
          </div>

          {/* Coordinate Bounding Box Overlay Highlight */}
          {activeCitation && activeCitation.page_number === selectedPage && (
            <div
              className="bbox-highlight transition-all duration-500"
              style={{
                top: `${activeCitation.bounding_box[1]}px`,
                left: `${activeCitation.bounding_box[0]}px`,
                width: `${activeCitation.bounding_box[2] - activeCitation.bounding_box[0]}px`,
                height: `${activeCitation.bounding_box[3] - activeCitation.bounding_box[1]}px`,
              }}
            >
              <div className="absolute -top-7 left-0 bg-orange-600 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-lg flex items-center gap-1">
                <Target className="w-3 h-3 animate-spin" />
                <span>Verified Source Bbox [{activeCitation.bounding_box.join(', ')}]</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer Citation Banner */}
      <div className="px-4 py-3 bg-slate-900/90 border-t border-slate-800 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-slate-400 text-[11px]">
            {activeCitation ? "Active Citation: Page " + activeCitation.page_number : "Click citation link in answer to highlight exact PDF bounding box"}
          </span>
        </div>
        <div className="flex items-center gap-1 text-[11px] text-emerald-400 font-semibold">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Coordinate Vector Indexed</span>
        </div>
      </div>
    </div>
  );
}
