import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  FileText,
  Target,
  Sparkles,
  CheckCircle2,
  Eye,
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
  Moon
} from 'lucide-react';

const BASE_PAGE_WIDTH = 600;
const BASE_PAGE_HEIGHT = 820;

// Academic syllabus pages data
const pagesData = [
  {
    page: 1,
    chapter: "Chapter 4: Binary Trees & BST",
    title: "4.1 Binary Search Trees: Definition & Core Invariants",
    subheading: "Formal Definition, Strict Ordering Property & Vector Representation",
    paragraphs: [
      "A Binary Search Tree (BST) is a hierarchical node-based binary tree data structure with the strict ordering invariant:",
      "• For any node X, every key stored in the left subtree of X is strictly less than key(X): ∀ y ∈ Left(X), Key(y) < Key(X).",
      "• Every key stored in the right subtree of X is strictly greater than key(X): ∀ z ∈ Right(X), Key(z) > Key(X).",
      "• Both the left and right subtrees must also recursively satisfy all Binary Search Tree properties."
    ],
    codeSnippet: `// BST Invariant Verification Function\nbool isBST(Node* root, int minVal, int maxVal) {\n    if (root == nullptr) return true;\n    if (root->data <= minVal || root->data >= maxVal) return false;\n    return isBST(root->left, minVal, root->data) &&\n           isBST(root->right, root->data, maxVal);\n}`,
    diagramType: 'bst-overview',
    bboxCitation: [50.0, 100.0, 500.0, 220.0]
  },
  {
    page: 2,
    chapter: "Chapter 4: Binary Trees & BST",
    title: "4.2 BST Insertion Algorithm & Recursive Mechanics",
    subheading: "Recursive Branch Traversal, Node Allocation & Base Conditions",
    paragraphs: [
      "Inserting a key K into a Binary Search Tree traverses downward until a leaf position is reached:",
      "1. Base Condition: If root is NULL, allocate a new node with key K and return pointer.",
      "2. Recurse Left: If K < root.key, recursively insert into left subtree: root.left = insert(root.left, K).",
      "3. Recurse Right: If K > root.key, recursively insert into right subtree: root.right = insert(root.right, K).",
      "4. Duplicate Guard: If K == root.key, ignore or update frequency counter depending on multiset policy."
    ],
    codeSnippet: `Node* insert(Node* node, int key) {\n    if (node == nullptr) return new Node(key);\n    if (key < node->key) node->left = insert(node->left, key);\n    else if (key > node->key) node->right = insert(node->right, key);\n    return node;\n}`,
    diagramType: 'bst-insert',
    bboxCitation: [60.0, 150.0, 520.0, 300.0]
  },
  {
    page: 3,
    chapter: "Chapter 4: Binary Trees & BST",
    title: "4.3 BST Deletion Algorithm & In-Order Successor",
    subheading: "Node Removal Mechanics Across Three Fundamental Topological Degrees",
    paragraphs: [
      "Deleting a target key K from a BST requires handling 3 distinct structural cases:",
      "• Case 1 (Degree 0 - Leaf Node): Directly unlink and free memory; set parent pointer to NULL.",
      "• Case 2 (Degree 1 - Single Child): Splice the parent pointer directly to the node's only child.",
      "• Case 3 (Degree 2 - Two Children): Find the In-Order Successor (the minimum key in the right subtree). Copy successor key to target node, then recursively delete successor."
    ],
    codeSnippet: `// Case 3: In-Order Successor Substitution\nNode* minValNode = findMin(root->right);\nroot->key = minValNode->key;\nroot->right = deleteNode(root->right, minValNode->key);`,
    diagramType: 'bst-delete',
    bboxCitation: [80.0, 200.0, 540.0, 380.0]
  },
  {
    page: 4,
    chapter: "Chapter 4: Binary Trees & BST",
    title: "4.4 Time & Space Complexity Analysis & Corner Cases",
    subheading: "Balanced vs. Degenerate Trees, Recurrence Relations & Call Stack Bounds",
    paragraphs: [
      "The operational efficiency of BST operations directly correlates with tree height h:",
      "• Balanced BST (Best/Average Case): Height h = ⌊log₂ N⌋. Search, Insert, and Delete operate in O(log N) time.",
      "• Degenerate / Skewed BST (Worst Case): Height h = N. Operations degrade to linear O(N) traversal.",
      "• Auxiliary Call Stack Space: Recursion consumes O(h) memory on the call stack."
    ],
    codeSnippet: `/* Complexity Table: BST vs AVL vs Red-Black */\nOperation     Average Case     Worst Case     Aux Space\nSearch        O(log N)         O(N)           O(h)\nInsertion     O(log N)         O(N)           O(h)\nDeletion      O(log N)         O(N)           O(h)`,
    diagramType: 'bst-table',
    bboxCitation: [70.0, 120.0, 510.0, 280.0]
  }
];

export default function PdfViewer({
  activeCitation,
  setActiveCitation,
  selectedPage = 3,
  setSelectedPage
}) {
  const [zoom, setZoom] = useState(1.0);
  const [paperTheme, setPaperTheme] = useState('light'); // 'light' | 'dark'
  const [isPulsing, setIsPulsing] = useState(false);
  const [showOverlay, setShowOverlay] = useState(true);

  const canvasRef = useRef(null);
  const highlightRef = useRef(null);
  const containerRef = useRef(null);
  const pulseTimerRef = useRef(null);

  const currentPageObj = pagesData.find((p) => p.page === selectedPage) || pagesData[2];

  // Trigger intense animated pulse shockwave whenever citation reference changes or is re-clicked
  useEffect(() => {
    if (activeCitation && activeCitation.page_number === selectedPage) {
      setIsPulsing(true);
      if (pulseTimerRef.current) clearTimeout(pulseTimerRef.current);
      pulseTimerRef.current = setTimeout(() => {
        setIsPulsing(false);
      }, 1800);

      // Smooth scroll container to center the bounding box
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

      // Detect if unit-normalized [0..1]
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
      const width = Math.max(24, (normX1 - normX0) * renderedWidth);
      const height = Math.max(20, (normY1 - normY0) * renderedHeight);

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

  // Clean HTML5 Canvas Page Rendering Engine with High-DPI / Retina Crispness
  const renderCanvasPage = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const renderedWidth = Math.round(BASE_PAGE_WIDTH * zoom);
    const renderedHeight = Math.round(BASE_PAGE_HEIGHT * zoom);

    // Set backing store dimensions for sharp rendering
    canvas.width = Math.round(renderedWidth * dpr);
    canvas.height = Math.round(renderedHeight * dpr);
    canvas.style.width = `${renderedWidth}px`;
    canvas.style.height = `${renderedHeight}px`;

    // Scale context by DPR and Zoom so drawing logic stays in BASE_PAGE coordinates (600 x 820)
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr * zoom, dpr * zoom);

    // Color tokens based on paperTheme
    const isDark = paperTheme === 'dark';
    const bgPaper = isDark ? '#0f172a' : '#ffffff';
    const textMain = isDark ? '#f1f5f9' : '#0f172a';
    const textMuted = isDark ? '#94a3b8' : '#475569';
    const textSub = isDark ? '#64748b' : '#64748b';
    const borderCol = isDark ? '#1e293b' : '#e2e8f0';
    const codeBg = isDark ? '#1e293b' : '#f8fafc';
    const codeText = isDark ? '#38bdf8' : '#0369a1';
    const accentIndigo = isDark ? '#818cf8' : '#4f46e5';

    // 1. Paper Background & Subtle Margin Guidelines
    ctx.fillStyle = bgPaper;
    ctx.fillRect(0, 0, BASE_PAGE_WIDTH, BASE_PAGE_HEIGHT);

    // Page Border
    ctx.strokeStyle = borderCol;
    ctx.lineWidth = 1;
    ctx.strokeRect(0, 0, BASE_PAGE_WIDTH, BASE_PAGE_HEIGHT);

    // 2. Academic Running Header
    ctx.fillStyle = textSub;
    ctx.font = '600 9px ui-monospace, SFMono-Regular, Menlo, Monaco, monospace';
    ctx.fillText('DATA STRUCTURES & ALGORITHMS • CS-302', 36, 32);

    ctx.textAlign = 'right';
    ctx.fillText(`PAGE 4-0${currentPageObj.page}  |  OFFICIAL SYLLABUS`, BASE_PAGE_WIDTH - 36, 32);
    ctx.textAlign = 'left';

    // Header divider rule
    ctx.strokeStyle = borderCol;
    ctx.beginPath();
    ctx.moveTo(36, 40);
    ctx.lineTo(BASE_PAGE_WIDTH - 36, 40);
    ctx.stroke();

    // 3. Chapter & Section Title
    ctx.fillStyle = accentIndigo;
    ctx.font = '700 10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillText(currentPageObj.chapter.toUpperCase(), 36, 62);

    ctx.fillStyle = textMain;
    ctx.font = '700 17px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillText(currentPageObj.title, 36, 84);

    ctx.fillStyle = textMuted;
    ctx.font = '500 11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillText(currentPageObj.subheading, 36, 102);

    // 4. Document Paragraphs (Wrapped Cleanly)
    let cursorY = 126;
    ctx.font = '400 11.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

    currentPageObj.paragraphs.forEach((pText) => {
      ctx.fillStyle = textMain;
      const words = pText.split(' ');
      let line = '';
      const maxWidth = BASE_PAGE_WIDTH - 72;

      for (let n = 0; n < words.length; n++) {
        const testLine = line + words[n] + ' ';
        const metrics = ctx.measureText(testLine);
        if (metrics.width > maxWidth && n > 0) {
          ctx.fillText(line, 36, cursorY);
          line = words[n] + ' ';
          cursorY += 18;
        } else {
          line = testLine;
        }
      }
      ctx.fillText(line, 36, cursorY);
      cursorY += 22;
    });

    // 5. Code & Algorithm Execution Box
    cursorY += 4;
    const codeBoxHeight = 88;
    ctx.fillStyle = codeBg;
    ctx.beginPath();
    ctx.roundRect(36, cursorY, BASE_PAGE_WIDTH - 72, codeBoxHeight, 6);
    ctx.fill();
    ctx.strokeStyle = borderCol;
    ctx.stroke();

    // Code header label
    ctx.fillStyle = accentIndigo;
    ctx.font = '700 9px ui-monospace, monospace';
    ctx.fillText('ALGORITHM LISTING 4.' + currentPageObj.page, 48, cursorY + 16);

    // Code lines
    ctx.fillStyle = codeText;
    ctx.font = '400 10px ui-monospace, monospace';
    const codeLines = currentPageObj.codeSnippet.split('\n');
    let codeY = cursorY + 32;
    codeLines.slice(0, 4).forEach((cLine) => {
      ctx.fillText(cLine, 48, codeY);
      codeY += 14;
    });

    cursorY += codeBoxHeight + 20;

    // 6. Vector Diagrams Rendered Directly onto Canvas
    if (currentPageObj.diagramType === 'bst-overview' || currentPageObj.diagramType === 'bst-delete') {
      // Draw Binary Search Tree Diagram
      ctx.fillStyle = isDark ? '#1e293b' : '#f8fafc';
      ctx.beginPath();
      ctx.roundRect(36, cursorY, BASE_PAGE_WIDTH - 72, 190, 8);
      ctx.fill();
      ctx.strokeStyle = borderCol;
      ctx.stroke();

      // Title of figure
      ctx.fillStyle = textMuted;
      ctx.font = '600 10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      const figureTitle =
        currentPageObj.page === 3
          ? 'FIGURE 4.3: In-Order Successor Substitution (Key 50 Replaced with 60)'
          : 'FIGURE 4.1: BST Structural Invariant Demonstration (Left < Root < Right)';
      ctx.fillText(figureTitle, 48, cursorY + 22);

      // Node coordinates for 3-level binary tree
      const centerX = BASE_PAGE_WIDTH / 2;
      const rootY = cursorY + 55;
      const level2Y = cursorY + 110;
      const level3Y = cursorY + 160;

      const nodes = [
        {
          key: currentPageObj.page === 3 ? '60' : '50',
          x: centerX,
          y: rootY,
          color: currentPageObj.page === 3 ? '#f97316' : accentIndigo,
          label: currentPageObj.page === 3 ? 'Substituted Successor' : 'Root Node'
        },
        { key: '30', x: centerX - 120, y: level2Y, color: accentIndigo },
        {
          key: '70',
          x: centerX + 120,
          y: level2Y,
          color: accentIndigo,
          label: 'Right Subtree'
        },
        { key: '20', x: centerX - 160, y: level3Y, color: textMuted },
        { key: '40', x: centerX - 80, y: level3Y, color: textMuted },
        {
          key: currentPageObj.page === 3 ? 'Pruned' : '60',
          x: centerX + 80,
          y: level3Y,
          color: currentPageObj.page === 3 ? '#ef4444' : '#10b981',
          label: currentPageObj.page === 3 ? 'Deleted Leaf' : 'In-Order Min'
        },
        { key: '80', x: centerX + 160, y: level3Y, color: textMuted }
      ];

      // Draw Edges
      ctx.strokeStyle = isDark ? '#475569' : '#cbd5e1';
      ctx.lineWidth = 1.5;

      const drawEdge = (n1, n2) => {
        ctx.beginPath();
        ctx.moveTo(n1.x, n1.y);
        ctx.lineTo(n2.x, n2.y);
        ctx.stroke();
      };

      drawEdge(nodes[0], nodes[1]);
      drawEdge(nodes[0], nodes[2]);
      drawEdge(nodes[1], nodes[3]);
      drawEdge(nodes[1], nodes[4]);
      drawEdge(nodes[2], nodes[5]);
      drawEdge(nodes[2], nodes[6]);

      // Draw Nodes
      nodes.forEach((node) => {
        ctx.beginPath();
        ctx.arc(node.x, node.y, 16, 0, Math.PI * 2);
        ctx.fillStyle = isDark ? '#0f172a' : '#ffffff';
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = node.color;
        ctx.stroke();

        ctx.fillStyle = node.color;
        ctx.font = '700 11px ui-monospace, monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(node.key, node.x, node.y);

        if (node.label) {
          ctx.font = '600 8.5px -apple-system, sans-serif';
          ctx.fillStyle = textSub;
          ctx.fillText(node.label, node.x, node.y - 22);
        }
      });
      ctx.textAlign = 'left';
      ctx.textBaseline = 'alphabetic';

      cursorY += 210;
    } else if (currentPageObj.diagramType === 'bst-table') {
      // Draw Complexity Comparison Table
      ctx.fillStyle = isDark ? '#1e293b' : '#f8fafc';
      ctx.beginPath();
      ctx.roundRect(36, cursorY, BASE_PAGE_WIDTH - 72, 160, 8);
      ctx.fill();
      ctx.strokeStyle = borderCol;
      ctx.stroke();

      ctx.fillStyle = textMuted;
      ctx.font = '600 10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      ctx.fillText('TABLE 4.4: Operations Complexity Matrix (Height h = log₂ N vs N)', 48, cursorY + 22);

      const tableRows = [
        ['Operation', 'Best Case', 'Average Case', 'Worst Case', 'Auxiliary Space'],
        ['Search(K)', 'Ω(1)', 'Θ(log N)', 'O(N)', 'O(h)'],
        ['Insert(K)', 'Ω(1)', 'Θ(log N)', 'O(N)', 'O(h)'],
        ['Delete(K)', 'Ω(1)', 'Θ(log N)', 'O(N)', 'O(h)'],
        ['Traversal', 'Θ(N)', 'Θ(N)', 'Θ(N)', 'O(h)']
      ];

      let rowY = cursorY + 44;
      const colWidths = [100, 95, 105, 95, 95];

      tableRows.forEach((row, rIdx) => {
        let colX = 48;
        if (rIdx === 0) {
          ctx.font = '700 9.5px -apple-system, sans-serif';
          ctx.fillStyle = accentIndigo;
        } else {
          ctx.font = '500 9.5px ui-monospace, monospace';
          ctx.fillStyle = textMain;
        }

        row.forEach((cell, cIdx) => {
          ctx.fillText(cell, colX, rowY);
          colX += colWidths[cIdx];
        });

        // Row border
        ctx.strokeStyle = borderCol;
        ctx.lineWidth = 0.8;
        ctx.beginPath();
        ctx.moveTo(44, rowY + 6);
        ctx.lineTo(BASE_PAGE_WIDTH - 44, rowY + 6);
        ctx.stroke();

        rowY += 22;
      });

      cursorY += 180;
    } else {
      // Flow diagram for insertion
      ctx.fillStyle = isDark ? '#1e293b' : '#f8fafc';
      ctx.beginPath();
      ctx.roundRect(36, cursorY, BASE_PAGE_WIDTH - 72, 160, 8);
      ctx.fill();
      ctx.strokeStyle = borderCol;
      ctx.stroke();

      ctx.fillStyle = textMuted;
      ctx.font = '600 10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      ctx.fillText('FIGURE 4.2: Recursive Insertion Decision Tree', 48, cursorY + 22);

      const steps = [
        '1. Compare Key K against Node->key',
        '2. Branch: If K < Node->key, recurse into Left Child branch',
        '3. Branch: If K > Node->key, recurse into Right Child branch',
        '4. Terminal: On encountering NULL pointer, allocate new Leaf Node(K)'
      ];

      let stepY = cursorY + 48;
      steps.forEach((st) => {
        ctx.fillStyle = accentIndigo;
        ctx.fillRect(48, stepY - 8, 4, 14);

        ctx.fillStyle = textMain;
        ctx.font = '500 10.5px -apple-system, BlinkMacSystemFont, sans-serif';
        ctx.fillText(st, 60, stepY + 3);
        stepY += 26;
      });

      cursorY += 180;
    }

    // 7. Academic Footer Rule & Grounded Evidence Stamp
    ctx.strokeStyle = borderCol;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(36, BASE_PAGE_HEIGHT - 38);
    ctx.lineTo(BASE_PAGE_WIDTH - 36, BASE_PAGE_HEIGHT - 38);
    ctx.stroke();

    ctx.fillStyle = textSub;
    ctx.font = '600 8.5px ui-monospace, monospace';
    ctx.fillText('STUDYCOPILOT GROUNDED SYLLABUS ARCHIVE • VERIFIED REPOSITORY ID: #BST-CS302', 36, BASE_PAGE_HEIGHT - 22);

    ctx.textAlign = 'right';
    ctx.fillStyle = isDark ? '#34d399' : '#059669';
    ctx.fillText('✓ TEXTBOOK EVIDENCE CERTIFIED', BASE_PAGE_WIDTH - 36, BASE_PAGE_HEIGHT - 22);
    ctx.textAlign = 'left';
  }, [selectedPage, zoom, paperTheme, currentPageObj]);

  // Re-render canvas whenever page, zoom, or theme changes
  useEffect(() => {
    renderCanvasPage();
  }, [renderCanvasPage]);

  // Bounding box data resolution
  const bboxToRender =
    activeCitation && activeCitation.page_number === selectedPage
      ? activeCitation.bounding_box || currentPageObj.bboxCitation
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
              <span className="font-semibold text-slate-200 tracking-tight">
                Binary_Search_Trees_Chapter.pdf
              </span>
              <span className="px-2 py-0.5 text-[10px] font-mono font-medium bg-slate-800 text-indigo-300 rounded-md border border-slate-700/80">
                Page {selectedPage} of 4
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

          {[1, 2, 3, 4].map((p) => (
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
          ))}

          <button
            onClick={() => setSelectedPage && setSelectedPage((p) => Math.min(4, p + 1))}
            disabled={selectedPage >= 4}
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
              <div className="absolute -top-1.5 -left-1.5 w-3 h-3 border-t-2 border-l-2 border-orange-400 rounded-tl-sm pointer-events-none" />
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
