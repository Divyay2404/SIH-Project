import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Upload,
  Presentation,
  FileText,
  CheckCircle,
  CheckCircle2,
  Sparkles,
  FolderPlus,
  Plus,
  Trash2,
  ChevronUp,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Clock,
  BookOpen,
  Layers,
  Download,
  RotateCcw,
  Edit3,
  Eye,
  FileCode,
  Maximize2,
  Minimize2,
  AlertCircle,
  HelpCircle,
  MessageSquare,
  ArrowRight,
  Sparkle,
  Activity,
  Cpu,
  Bookmark,
  ListChecks,
  Hash,
  Compass,
  RefreshCw
} from 'lucide-react';
import WeaknessHeatmap from './WeaknessHeatmap';
import { apiUrl } from '../../config/api';

/**
 * Slide Category Definitions with theme styling
 */
const SLIDE_CATEGORIES = [
  { label: 'Title Slide', color: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30' },
  { label: 'Curriculum Overview', color: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
  { label: 'Theoretical Foundations', color: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30' },
  { label: 'Concept Breakdown', color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' },
  { label: 'Conceptual Diagram', color: 'bg-purple-500/20 text-purple-300 border-purple-500/30' },
  { label: 'Real-World Applications', color: 'bg-amber-500/20 text-amber-300 border-amber-500/30' },
  { label: 'Critical Analysis', color: 'bg-rose-500/20 text-rose-300 border-rose-500/30' },
  { label: 'Assessment Standards', color: 'bg-violet-500/20 text-violet-300 border-violet-500/30' },
  { label: 'Summary & Takeaways', color: 'bg-teal-500/20 text-teal-300 border-teal-500/30' },
];

/**
 * Generates an educational slide deck derived dynamically from document concepts and sections
 * when the backend analysis does not provide pre-formatted slides.
 */
function generateDocumentDerivedSlideDeck(title = 'Course Material', concepts = [], sections = [], summary = '') {
  const cList = Array.isArray(concepts) && concepts.length > 0 ? concepts : ['Core Concept', 'System Mechanics', 'Applications'];
  const sList = Array.isArray(sections) && sections.length > 0 ? sections : ['Overview', 'Theoretical Principles', 'Analysis'];

  return [
    {
      id: 'slide-1',
      category: 'Title Slide',
      title: title,
      subtitle: 'Document-Grounded Lecture Deck',
      bullets: [
        `Curriculum overview covering foundational principles of ${title}.`,
        summary ? (summary.slice(0, 140) + '...') : `Rigorous examination of topics in ${title}.`,
        'Extracted and indexed into StudyForge OS vector memory.',
        'Aligned with syllabus standards and assessment criteria.'
      ],
      notes: `TEACHER SPEAKER SCRIPT:\n\nWelcome students to today's lecture on '${title}'. Today we will walk through the core theoretical and applied topics extracted directly from the syllabus material.\n\nOutline the primary objectives and key focus areas for the session.`,
      diagram: false
    },
    {
      id: 'slide-2',
      category: 'Curriculum Overview',
      title: 'Curriculum Overview & Key Topics',
      subtitle: 'Structural boundaries and learning outcomes',
      bullets: [
        `Primary focus area: ${sList[0] || title}`,
        `Core principles: ${cList.slice(0, 3).join(', ') || 'Foundational principles'}`,
        'Methodological framework and execution constraints.',
        'Practical implications and domain boundary conditions.'
      ],
      notes: `TEACHER SPEAKER SCRIPT:\n\nReview the roadmap of topics for '${title}'. Walk students through each major section before diving into details.`,
      diagram: false
    },
    {
      id: 'slide-3',
      category: 'Theoretical Foundations',
      title: `Theoretical Foundations: ${cList[0] || 'Core Mechanics'}`,
      subtitle: 'Axiomatic principles and invariant guarantees',
      bullets: [
        `Definition and mathematical formalisms of ${cList[0] || title}.`,
        'Preserving structural and logical invariants across operational boundaries.',
        'Evaluating theoretical complexity bounds and constraints.',
        'Empirical verification and testing methodologies.'
      ],
      notes: `TEACHER SPEAKER SCRIPT:\n\nEmphasize the core foundational rules of ${cList[0] || title}. Ensure students understand why these rules must hold true.`,
      diagram: false
    },
    {
      id: 'slide-4',
      category: 'Concept Breakdown',
      title: `Detailed Mechanics: ${cList[1] || sList[1] || 'Operational Sequence'}`,
      subtitle: 'Step-by-step examination of system mechanics',
      bullets: [
        `Analysis of ${cList[1] || sList[1] || 'system mechanics'}.`,
        'Operational rules and state transitions.',
        'Key properties ensuring correctness and stability.',
        'Edge cases and boundary exception handling.'
      ],
      notes: `TEACHER SPEAKER SCRIPT:\n\nWalk students step-by-step through ${cList[1] || sList[1] || 'operational mechanics'}. Encourage questions regarding edge cases.`,
      diagram: false
    },
    {
      id: 'slide-5',
      category: 'Critical Analysis',
      title: 'Comparative Analysis & Evaluation',
      subtitle: 'Trade-offs, performance characteristics, and limitations',
      bullets: [
        'Strengths and efficiency under standard operational workloads.',
        'Resource trade-offs and runtime computational complexity.',
        'Common engineering pitfalls and failure modes.',
        'Recommended mitigation strategies in production environments.'
      ],
      notes: `TEACHER SPEAKER SCRIPT:\n\nDiscuss the advantages and limitations of the studied concepts. Challenge students to identify when alternate approaches are preferable.`,
      diagram: false
    },
    {
      id: 'slide-6',
      category: 'Summary & Takeaways',
      title: 'Lecture Summary & Key Takeaways',
      subtitle: 'Synthesis of concepts and preparation for evaluation',
      bullets: [
        `Consolidation of core principles covered in ${title}.`,
        'Checklist of foundational invariants and problem-solving steps.',
        'Preparation guidelines for diagnostic quizzes and assessments.',
        'Recommended follow-up readings and lab exercises.'
      ],
      notes: `TEACHER SPEAKER SCRIPT:\n\nSummarize the primary takeaways from today's session on '${title}'. Open the floor for final student questions.`,
      diagram: false
    }
  ];
}

/**
 * Generates an initial demo/sample 10-slide deck clearly labeled for demonstration.
 */
function generateSampleSlideDeck(topicTitle = 'Binary Search Trees & Structural Invariants') {
  return [
    {
      id: 'slide-1',
      category: 'Title Slide',
      title: topicTitle,
      subtitle: 'Curriculum Briefing & Educational Lecture Outline (Sample)',
      bullets: [
        `Core syllabus module covering foundational principles of ${topicTitle}.`,
        'Rigorous examination of theoretical models, computational complexity, and edge cases.',
        'Aligned with B.Tech computer science curriculum and formal university assessment standards.',
        'Interactive classroom presentation deck with embedded educator talking points.'
      ],
      notes: `TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\nWelcome everyone to today's comprehensive session on '${topicTitle}'. In this lecture, our primary objective is to establish a rigorous baseline understanding of the core modules. Emphasize to students that the concepts introduced today form the architectural bedrock for all subsequent analytical modules.\n\nTake 3 to 5 minutes to outline expectations, review the syllabus roadmap, and encourage active inquiry before diving into the core material.`,
      diagram: false
    },
    {
      id: 'slide-2',
      category: 'Curriculum Overview',
      title: 'Curriculum Overview & Scope',
      subtitle: 'Structural boundaries, learning goals, and prerequisites',
      bullets: [
        `Comprehensive examination of key modules in ${topicTitle}.`,
        'Core theoretical principles, state invariants, and empirical foundations.',
        'Algorithmic methodologies for systematic problem-solving.',
        'Real-world industry applications and boundary conditions.',
        'Evaluation criteria and preparation standards for upcoming assessments.'
      ],
      notes: `TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\nWhen presenting this curriculum overview, walk students methodically through each bullet point.\n\nPoint 1 establishes the broad structural scope, while Point 2 grounds the discussion in empirical theory. Instructors should spend extra time highlighting Point 4 (real-world applications), as students often struggle to connect abstract textbook theory with practical constraints.\n\nOpen the floor briefly to ensure the class understands the evaluation standards before moving forward.`,
      diagram: false
    },
    {
      id: 'slide-3',
      category: 'Theoretical Foundations',
      title: 'Theoretical Foundations & Invariants',
      subtitle: 'Axiomatic properties and mathematical guarantees',
      bullets: [
        `Defining axiomatic principles underlying ${topicTitle}.`,
        'Establishing rigorous logical frameworks and state invariant preservation.',
        'Analyzing fundamental hypotheses, space complexity, and logarithmic runtime bounds.',
        'Reviewing foundational literature and historical engineering context.',
        'Mapping conceptual relationships to predictable empirical outcomes.'
      ],
      notes: `TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\nExplore the theoretical foundations and axiomatic parameters.\n\nEmphasize how these principles serve as the prerequisite framework for understanding the rest of the material. Encourage students to relate these foundational rules back to real-world observations and previous coursework.`,
      diagram: false
    },
    {
      id: 'slide-4',
      category: 'Concept Breakdown',
      title: 'Core Mechanics: Traversal & Query Operations',
      subtitle: 'Step-by-step examination of algorithmic execution',
      bullets: [
        'Ordered tree traversal techniques: In-Order, Pre-Order, and Post-Order traversal patterns.',
        'Binary search property guarantee: Left Subtree Key < Root Key < Right Subtree Key.',
        'Logarithmic time complexity O(log N) for balanced trees vs worst-case linear O(N) degenerate trees.',
        'Recursive vs iterative implementations and call-stack overhead considerations.'
      ],
      notes: `TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\nDetailed Breakdown for Core Traversal Mechanics.\n\nInstructors should unpack these core bullet points line by line. Explain the underlying principles and empirical findings associated with each statement. Be sure to address common student misconceptions regarding boundaries and operational parameters.`,
      diagram: false
    },
    {
      id: 'slide-5',
      category: 'Concept Breakdown',
      title: 'Advanced Mutation: Node Deletion & Edge Cases',
      subtitle: 'Maintaining structural integrity across edge cases',
      bullets: [
        'Case 1: Deleting a leaf node with zero child pointers (immediate removal).',
        'Case 2: Deleting an internal node with a single child (direct parent pointer bypass).',
        'Case 3: Deleting a node with two children requiring In-Order Successor substitution.',
        'In-Order Successor determination: Smallest key in the right subtree.'
      ],
      notes: `TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\nCRITICAL DIAGNOSTIC FOCUS:\nOur class weakness analytics indicate students struggle with Case 3 deletion.\n\nDedicate at least 7 minutes to trace the in-order successor swap on the whiteboard. Demonstrate why swapping the smallest element in the right subtree guarantees the BST invariant is preserved without re-sorting the rest of the tree.`,
      diagram: false
    },
    {
      id: 'slide-6',
      category: 'Conceptual Diagram',
      title: 'Conceptual Progression & Architectural Workflow',
      subtitle: 'Three-stage progression from input ingestion to validated equilibrium',
      bullets: [
        'Stage 1 (Background): Ingestion of raw key sequence and baseline initialization.',
        'Stage 2 (Mechanism): Recursive invariant testing, comparator dispatch, and pointer rebinding.',
        'Stage 3 (Impact): Validated equilibrium state with guaranteed search bounds.'
      ],
      notes: `TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\nConceptual Progression & Workflow Walkthrough:\n\nThis workflow slide is critical for visualizing the document's conceptual progression. Walk students explicitly through the three universal stages displayed in the process cards: 1. Background, 2. Mechanism, and 3. Impact.\n\nEmphasize how the concepts build logically from initial definitions to final analytical takeaways.`,
      diagram: true,
      diagramStages: [
        {
          stage: '1. BACKGROUND',
          title: 'Initialization & Input',
          description: 'Establish core definitions, conceptual parameters, and raw data ingestion baseline.'
        },
        {
          stage: '2. MECHANISM',
          title: 'Algorithmic Processing',
          description: 'Examine structural breakdowns, recursive comparator checks, and state transitions.'
        },
        {
          stage: '3. IMPACT',
          title: 'Target Equilibrium',
          description: 'Synthesize verified outputs, invariant preservation, and asymptotic guarantees.'
        }
      ]
    },
    {
      id: 'slide-7',
      category: 'Real-World Applications',
      title: 'Real-World Applications & Systems Architecture',
      subtitle: 'Translating theory into enterprise database and compiler design',
      bullets: [
        'Relational database indexing engines (B-Tree and B+Tree evolution from BST principles).',
        'Memory management allocation tables and dynamic heap balancing mechanisms.',
        'Routing table optimization in high-throughput computer network switches.',
        'Symbol table lookup in compiler lexical analysis and intermediate code generation.'
      ],
      notes: `TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\nBridge theory and practice by discussing these real-world deployments. Ask students how the abstract principles covered earlier apply directly to database systems like PostgreSQL and MySQL.`,
      diagram: false
    },
    {
      id: 'slide-8',
      category: 'Critical Analysis',
      title: 'Critical Analysis & Trade-Off Matrix',
      subtitle: 'Evaluating performance boundaries, degenerate cases, and trade-offs',
      bullets: [
        'Skewed Tree Degradation: Sorted input vectors collapse tree height to O(N).',
        'Recursive Call Overhead: Auxiliary stack depth risks stack-overflow on deep structures.',
        'Concurrency Constraints: Locking individual nodes vs tree-wide mutual exclusion.',
        'Memory Footprint: Dual-pointer overhead (left/right pointers) vs contiguous flat arrays.'
      ],
      notes: `TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\nFacilitate an interactive discussion using these critical analysis questions. Encourage students to debate the trade-offs and consider potential failure modes.`,
      diagram: false
    },
    {
      id: 'slide-9',
      category: 'Assessment Standards',
      title: 'Assessment Standards & Rubric Guidelines',
      subtitle: 'Expected solution patterns, marks breakdown, and rubric thresholds',
      bullets: [
        '2-Mark Question: Define Binary Search Tree property with strict inequality bounds.',
        '5-Mark Question: Explain Case 3 node deletion algorithm with step-by-step pointer diagram.',
        '10-Mark Question: Provide full asymptotic analysis and prove O(log N) average search time.',
        'Rubric Alert: Deductions occur when duplicate key handling or null base cases are omitted.'
      ],
      notes: `TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\nReview evaluation criteria and assessment expectations with the class. Ensure students understand what is required to achieve mastery on upcoming exams. Point out that the 10-mark question requires both the theoretical proof and the exact pointer manipulation code snippet.`,
      diagram: false
    },
    {
      id: 'slide-10',
      category: 'Summary & Takeaways',
      title: 'Summary & Strategic Takeaways',
      subtitle: 'Synthesizing foundational concepts and next milestones',
      bullets: [
        `Reviewed foundational scope and educational roadmap for ${topicTitle}.`,
        'Analyzed core operational mechanics, traversal orders, and deletion invariant preservation.',
        'Examined conceptual progression and production deployment in database engines.',
        'Evaluated critical performance boundaries, degenerate cases, and asymptotic constraints.',
        'Confirmed foundational readiness for advanced balanced trees (AVL & Red-Black Trees).'
      ],
      notes: `TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\nConcluding Lecture Summary for '${topicTitle}':\n\nSynthesize the key takeaways listed on the slide. Remind students of the journey from our initial curriculum overview through the concept breakdowns and conceptual progression workflow.\n\nAssign recommended follow-up reading tasks, outline expectations for the upcoming homework assignment, and open the floor for final student queries.`,
      diagram: false
    }
  ];
}

export default function EducatorConsole({
  activeDocument: propActiveDoc,
  setActiveDocument: propSetActiveDoc,
  availableDocuments: propAvailDocs,
  setAvailableDocuments: propSetAvailDocs
}) {
  // Backend Connectivity State
  const [backendStatus, setBackendStatus] = useState('checking'); // 'connected' | 'unavailable' | 'checking'
  const [backendInfo, setBackendInfo] = useState(null);

  // Upload & Document State
  const [uploadStatus, setUploadStatus] = useState(() => {
    if (propActiveDoc) {
      return {
        name: propActiveDoc.filename,
        size: `${propActiveDoc.chunks_count || 0} chunks`,
        title: propActiveDoc.title,
        chunksExtracted: propActiveDoc.chunks_count || 0,
        pagesProcessed: propActiveDoc.pages_count || 1,
        documentId: propActiveDoc.document_id,
        summary: propActiveDoc.summary,
        importantConcepts: propActiveDoc.important_concepts,
        sections: propActiveDoc.sections,
        importantPortions: propActiveDoc.important_portions,
        indexingConfirmed: propActiveDoc.indexing_confirmed
      };
    }
    return null;
  });
  const [uploading, setUploading] = useState(false);
  const [uploadPhase, setUploadPhase] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [isUploadedDocument, setIsUploadedDocument] = useState(Boolean(propActiveDoc));

  // Slide Deck State
  const [slides, setSlides] = useState(() => {
    if (propActiveDoc?.slides && propActiveDoc.slides.length > 0) {
      return propActiveDoc.slides;
    }
    return [];
  });
  const [activeSlideIndex, setActiveSlideIndex] = useState(0);
  const [editorTab, setEditorTab] = useState('content'); // 'content' | 'notes'
  const [previewMode, setPreviewMode] = useState('split'); // 'split' | 'presentation'

  // Sync with propActiveDoc changes
  useEffect(() => {
    if (propActiveDoc) {
      setUploadStatus({
        name: propActiveDoc.filename,
        size: `${propActiveDoc.chunks_count || 0} chunks`,
        title: propActiveDoc.title,
        chunksExtracted: propActiveDoc.chunks_count || 0,
        pagesProcessed: propActiveDoc.pages_count || 1,
        documentId: propActiveDoc.document_id,
        summary: propActiveDoc.summary,
        importantConcepts: propActiveDoc.important_concepts,
        sections: propActiveDoc.sections,
        importantPortions: propActiveDoc.important_portions,
        indexingConfirmed: propActiveDoc.indexing_confirmed
      });
      setIsUploadedDocument(true);
      if (propActiveDoc.slides && propActiveDoc.slides.length > 0) {
        setSlides(propActiveDoc.slides);
      }
    }
  }, [propActiveDoc?.document_id]);

  // Load Isolated Sample BST Demo
  const handleLoadDemo = async () => {
    setUploading(true);
    setUploadPhase('Loading sample Binary Search Tree demo lecture...');
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
        important_portions: data.important_portions || [],
        slides: data.slides || generateSampleSlideDeck(),
        pages: data.pages || [],
        sourceUrl: apiUrl(`/api/document/${encodeURIComponent(data.document_id)}/pdf`)
      };
      setUploadStatus({
        name: demoDoc.filename,
        size: `${demoDoc.chunks_count} chunks`,
        title: demoDoc.title,
        chunksExtracted: demoDoc.chunks_count,
        pagesProcessed: demoDoc.pages_count,
        documentId: demoDoc.document_id,
        summary: demoDoc.summary,
        importantConcepts: demoDoc.important_concepts,
        sections: demoDoc.sections,
        importantPortions: demoDoc.important_portions,
        indexingConfirmed: true
      });
      setSlides(demoDoc.slides);
      setActiveSlideIndex(0);
      setIsUploadedDocument(false);
      propSetActiveDoc?.(demoDoc);
      setNotification({
        type: 'success',
        message: 'Sample BST demo lesson loaded with 10 structured lecture slides and speaker scripts.'
      });
    } catch (err) {
      setNotification({
        type: 'error',
        message: err.message || 'Failed to load demo data.'
      });
    } finally {
      setUploading(false);
      setUploadPhase('');
    }
  };

  // Bullet point input state
  const [newBulletText, setNewBulletText] = useState('');

  // Download states
  const [downloadingPpt, setDownloadingPpt] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [notification, setNotification] = useState(null);

  const fileInputRef = useRef(null);
  const activeSlide = slides[activeSlideIndex] || slides[0];

  // Auto-dismiss notification toast
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  // Check Backend Service Health
  const checkBackendHealth = useCallback(async () => {
    setBackendStatus('checking');
    try {
      const res = await fetch(apiUrl('/api/health'), {
        headers: { Accept: 'application/json' }
      });
      if (res.ok) {
        const data = await res.json();
        setBackendStatus('connected');
        setBackendInfo(data);
      } else {
        setBackendStatus('unavailable');
      }
    } catch (err) {
      setBackendStatus('unavailable');
    }
  }, []);

  useEffect(() => {
    checkBackendHealth();
  }, [checkBackendHealth]);

  // Handle Drag & Drop Events
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!dragActive) setDragActive(true);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  // Process Document File Ingestion
  const processFile = async (file) => {
    if (!file) return;

    const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    if (!isPdf) {
      setNotification({
        type: 'error',
        message: 'Invalid file format. Educator uploads support PDF course materials and lecture notes only.'
      });
      return;
    }

    if (file.size === 0) {
      setNotification({
        type: 'error',
        message: 'The uploaded PDF file is empty (0 bytes). Please upload a valid document.'
      });
      return;
    }

    const formattedSize = (file.size / 1024 / 1024).toFixed(2) + ' MB';
    setUploading(true);
    setUploadPhase('Uploading PDF to gateway...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      setUploadPhase('Processing PDF with PyMuPDF & OCR...');
      let response;
      try {
        response = await fetch(apiUrl('/api/ingest'), { method: 'POST', body: formData });
      } catch (networkErr) {
        setBackendStatus('unavailable');
        throw new Error('Backend service unreachable. Please ensure the FastAPI server is running.');
      }

      const contentType = response.headers.get('content-type') || '';
      const isJson = contentType.includes('application/json');

      if (!response.ok) {
        let errorMessage = `Server error HTTP ${response.status}`;
        if (isJson) {
          try {
            const errorPayload = await response.json();
            errorMessage = errorPayload.detail || errorPayload.message || errorMessage;
          } catch (jsonErr) {
            // Ignore JSON parse failure on non-JSON payload
          }
        }
        
        if (response.status === 404) {
          errorMessage = 'Server unavailable (HTTP 404): Ingestion endpoint not found. Please verify the FastAPI backend is deployed and VITE_API_BASE_URL is configured in your Vercel settings.';
        } else if ([502, 503, 504].includes(response.status)) {
          errorMessage = `Gateway error (HTTP ${response.status}). Ingestion service temporarily unavailable.`;
        }
        throw new Error(errorMessage);
      }

      if (!isJson) {
        throw new Error('Unexpected response format received from ingestion gateway.');
      }

      setUploadPhase('Analyzing Structure, Headings & Concepts...');
      const payload = await response.json();

      setUploadPhase('Indexing in Vector DB & Generating Learning Content...');
      setBackendStatus('connected');

      const documentTitle = payload.title || file.name.replace(/\.[^/.]+$/, '').replace(/_/g, ' ');
      const chunksExtracted = payload.chunks_extracted || 0;
      const pagesProcessed = payload.pages_processed || 1;
      const isIndexed = payload.indexing_confirmed === true;

      setUploadStatus({
        name: file.name,
        size: formattedSize,
        documentId: payload.document_id,
        title: documentTitle,
        chunksExtracted: chunksExtracted,
        pagesProcessed: pagesProcessed,
        indexingConfirmed: isIndexed,
        summary: payload.summary,
        importantConcepts: payload.important_concepts || [],
        sections: payload.sections || [],
        importantPortions: payload.important_portions || [],
        status: 'Ready'
      });

      // Populate document-specific slide deck from backend analysis
      if (Array.isArray(payload.slides) && payload.slides.length > 0) {
        setSlides(payload.slides);
      } else {
        // Derive dynamic slides from uploaded document concepts and sections
        setSlides(generateDocumentDerivedSlideDeck(
          documentTitle,
          payload.important_concepts,
          payload.sections,
          payload.summary
        ));
      }
      setIsUploadedDocument(true);
      setActiveSlideIndex(0);

      const newDoc = {
        document_id: payload.document_id,
        title: documentTitle,
        filename: file.name,
        pages_count: pagesProcessed,
        chunks_count: chunksExtracted,
        indexing_confirmed: isIndexed,
        summary: payload.summary,
        important_concepts: payload.important_concepts || [],
        sections: payload.sections || [],
        important_portions: payload.important_portions || [],
        slides: payload.slides || [],
        pages: payload.pages || [],
        sourceUrl: URL.createObjectURL(file)
      };
      propSetActiveDoc?.(newDoc);

      setNotification({
        type: 'success',
        message: `Successfully indexed "${documentTitle}"! ${chunksExtracted} sections extracted across ${pagesProcessed} page(s).`
      });
    } catch (err) {
      setUploadStatus({
        name: file.name,
        size: formattedSize,
        title: file.name.replace(/\.[^/.]+$/, '').replace(/_/g, ' '),
        error: err.message || 'Failed to process document'
      });
      setIsUploadedDocument(false);

      setNotification({
        type: 'error',
        message: `Ingestion failed: ${err.message}`
      });
    } finally {
      setUploading(false);
      setUploadPhase('');
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  // Helper for triggering browser blob downloads
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

  const safeFilename = (title) => (title || 'Lecture_Presentation').replace(/[^a-z0-9]+/gi, '_');

  // Trigger PPT Export
  const handleExportPPT = async () => {
    const docId = uploadStatus?.documentId;
    const presentationTitle = uploadStatus?.title || slides[0]?.title || 'Lecture_Presentation';

    if (!docId) {
      setNotification({
        type: 'error',
        message: 'No active document uploaded. Please upload a course PDF before exporting the presentation deck.'
      });
      return;
    }

    setDownloadingPpt(true);
    try {
      const res = await fetch(apiUrl(`/api/export/ppt?document_id=${encodeURIComponent(docId)}`));
      if (!res.ok) {
        let errText = `Export error HTTP ${res.status}`;
        const ct = res.headers.get('content-type') || '';
        if (ct.includes('application/json')) {
          try {
            const errJson = await res.json();
            errText = errJson.detail || errText;
          } catch (e) {}
        }
        throw new Error(errText);
      }

      const blob = await res.blob();
      downloadBlob(blob, `Lecture_${safeFilename(presentationTitle)}.pptx`);
      setNotification({
        type: 'success',
        message: `PowerPoint deck "Lecture_${safeFilename(presentationTitle)}.pptx" downloaded successfully!`
      });
    } catch (err) {
      setNotification({
        type: 'error',
        message: `PPT Export failed: ${err.message}`
      });
    } finally {
      setDownloadingPpt(false);
    }
  };

  // Trigger PDF Handout Export
  const handleExportPDF = async () => {
    const docId = uploadStatus?.documentId;
    const presentationTitle = uploadStatus?.title || slides[0]?.title || 'Study_Guide';

    if (!docId) {
      setNotification({
        type: 'error',
        message: 'No active document uploaded. Please upload a course PDF before exporting the study handout.'
      });
      return;
    }

    setDownloadingPdf(true);
    try {
      const res = await fetch(apiUrl(`/api/export/pdf?document_id=${encodeURIComponent(docId)}`));
      if (!res.ok) {
        let errText = `Export error HTTP ${res.status}`;
        const ct = res.headers.get('content-type') || '';
        if (ct.includes('application/json')) {
          try {
            const errJson = await res.json();
            errText = errJson.detail || errText;
          } catch (e) {}
        }
        throw new Error(errText);
      }

      const blob = await res.blob();
      downloadBlob(blob, `Study_Guide_${safeFilename(presentationTitle)}.pdf`);
      setNotification({
        type: 'success',
        message: `Study handout "Study_Guide_${safeFilename(presentationTitle)}.pdf" downloaded successfully!`
      });
    } catch (err) {
      setNotification({
        type: 'error',
        message: `Handout export failed: ${err.message}`
      });
    } finally {
      setDownloadingPdf(false);
    }
  };

  // Export Slide Outline JSON
  const handleExportJSON = () => {
    const dataStr = JSON.stringify({
      title: uploadStatus?.title || slides[0]?.title,
      exportedAt: new Date().toISOString(),
      slideCount: slides.length,
      isDocumentGrounded: isUploadedDocument,
      documentId: uploadStatus?.documentId || null,
      slides: slides
    }, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    downloadBlob(blob, `Slide_Outline_${safeFilename(uploadStatus?.title || 'Lecture')}.json`);
    setNotification({
      type: 'success',
      message: 'Slide outline exported as JSON.'
    });
  };

  // Slide Manipulation Handlers
  const handleTitleChange = (newTitle) => {
    setSlides(prev => prev.map((slide, idx) => (
      idx === activeSlideIndex ? { ...slide, title: newTitle } : slide
    )));
  };

  const handleSubtitleChange = (newSubtitle) => {
    setSlides(prev => prev.map((slide, idx) => (
      idx === activeSlideIndex ? { ...slide, subtitle: newSubtitle } : slide
    )));
  };

  const handleCategoryChange = (newCategory) => {
    setSlides(prev => prev.map((slide, idx) => (
      idx === activeSlideIndex ? { ...slide, category: newCategory } : slide
    )));
  };

  const handleBulletChange = (bulletIndex, text) => {
    setSlides(prev => prev.map((slide, idx) => {
      if (idx !== activeSlideIndex) return slide;
      const updatedBullets = [...slide.bullets];
      updatedBullets[bulletIndex] = text;
      return { ...slide, bullets: updatedBullets };
    }));
  };

  const handleDeleteBullet = (bulletIndex) => {
    setSlides(prev => prev.map((slide, idx) => {
      if (idx !== activeSlideIndex) return slide;
      const updatedBullets = slide.bullets.filter((_, bIdx) => bIdx !== bulletIndex);
      return { ...slide, bullets: updatedBullets };
    }));
  };

  const handleAddBullet = () => {
    if (!newBulletText.trim()) return;
    setSlides(prev => prev.map((slide, idx) => {
      if (idx !== activeSlideIndex) return slide;
      return { ...slide, bullets: [...slide.bullets, newBulletText.trim()] };
    }));
    setNewBulletText('');
  };

  const handleMoveBullet = (bulletIndex, direction) => {
    setSlides(prev => prev.map((slide, idx) => {
      if (idx !== activeSlideIndex) return slide;
      const targetIndex = bulletIndex + direction;
      if (targetIndex < 0 || targetIndex >= slide.bullets.length) return slide;
      const updatedBullets = [...slide.bullets];
      const temp = updatedBullets[bulletIndex];
      updatedBullets[bulletIndex] = updatedBullets[targetIndex];
      updatedBullets[targetIndex] = temp;
      return { ...slide, bullets: updatedBullets };
    }));
  };

  const handleNotesChange = (newNotes) => {
    setSlides(prev => prev.map((slide, idx) => (
      idx === activeSlideIndex ? { ...slide, notes: newNotes } : slide
    )));
  };

  const handleAddNewSlide = () => {
    const newSlideId = `slide-${Date.now()}`;
    const newSlide = {
      id: newSlideId,
      category: 'Concept Breakdown',
      title: 'New Analytical Topic & Conceptual Breakdown',
      subtitle: 'Key principles, operational parameters, and case study',
      bullets: [
        'Fundamental definition and core conceptual parameters.',
        'Algorithmic execution logic and operational guarantees.',
        'Primary edge-case constraints and performance benchmarks.'
      ],
      notes: `TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\nIntroduce this new topic to the class by establishing its relationship to preceding modules.\n\nHighlight key edge-case considerations and open the floor for student discussion.`,
      diagram: false
    };
    setSlides(prev => [...prev, newSlide]);
    setActiveSlideIndex(slides.length);
  };

  const handleDeleteSlide = (indexToDelete) => {
    if (slides.length <= 1) {
      setNotification({
        type: 'error',
        message: 'A presentation must contain at least one slide.'
      });
      return;
    }
    setSlides(prev => prev.filter((_, idx) => idx !== indexToDelete));
    if (activeSlideIndex >= indexToDelete && activeSlideIndex > 0) {
      setActiveSlideIndex(activeSlideIndex - 1);
    }
  };

  const handleMoveSlide = (index, direction) => {
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= slides.length) return;
    setSlides(prev => {
      const updated = [...prev];
      const temp = updated[index];
      updated[index] = updated[targetIndex];
      updated[targetIndex] = temp;
      return updated;
    });
    setActiveSlideIndex(targetIndex);
  };

  const handleResetOutline = () => {
    if (uploadStatus && !uploadStatus.error && Array.isArray(uploadStatus.slides)) {
      setSlides(uploadStatus.slides);
      setNotification({
        type: 'info',
        message: `Slide outline reset to document analysis for "${uploadStatus.title}".`
      });
    } else {
      setSlides(generateSampleSlideDeck());
      setIsUploadedDocument(false);
      setNotification({
        type: 'info',
        message: 'Slide outline reset to default sample curriculum template.'
      });
    }
    setActiveSlideIndex(0);
  };

  // Calculate estimated speaking duration (approx 130 words per min)
  const calculateSpeakingTime = (text) => {
    if (!text) return '< 1 min';
    const words = text.trim().split(/\s+/).length;
    const minutes = Math.max(1, Math.round(words / 130));
    return `~${minutes} min${minutes > 1 ? 's' : ''}`;
  };

  const totalSpeakingDuration = () => {
    const totalWords = slides.reduce((acc, s) => acc + (s.notes ? s.notes.split(/\s+/).length : 0), 0);
    const minutes = Math.max(5, Math.round(totalWords / 130));
    return `~${minutes} mins`;
  };

  return (
    <div className="space-y-8">
      {/* Toast Notification Alert */}
      {notification && (
        <div
          className={`fixed top-5 right-5 z-50 p-4 rounded-xl shadow-2xl border flex items-center gap-3 transition-all transform animate-in slide-in-from-top-4 duration-200 max-w-md ${
            notification.type === 'error'
              ? 'bg-red-950/90 border-red-500/50 text-red-200'
              : notification.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-200'
              : 'bg-indigo-950/90 border-indigo-500/50 text-indigo-200'
          }`}
        >
          {notification.type === 'error' ? (
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          ) : (
            <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />
          )}
          <span className="text-xs font-medium leading-relaxed">{notification.message}</span>
        </div>
      )}

      {/* Top Banner & Control Hub Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 shadow-xl">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-1.5">
              <Sparkles className="w-5 h-5 text-amber-400" />
              <h2 className="text-lg font-bold text-white tracking-tight">
                Educator Slide Generator & Presentation Control Hub
              </h2>

              {/* Backend Connectivity Status Pill */}
              {backendStatus === 'connected' ? (
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  Backend Connected
                </span>
              ) : backendStatus === 'checking' ? (
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700 flex items-center gap-1">
                  <RefreshCw className="w-2.5 h-2.5 animate-spin" />
                  Checking Backend...
                </span>
              ) : (
                <button
                  onClick={checkBackendHealth}
                  title="Click to retry backend connection"
                  className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 flex items-center gap-1 hover:bg-rose-500/30 transition-colors cursor-pointer"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                  Backend Unavailable (Retry)
                </button>
              )}

              {/* Document Status Tag */}
              {isUploadedDocument ? (
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  Document Grounded
                </span>
              ) : (
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  Demo / Sample Content
                </span>
              )}
            </div>
            <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
              Upload textbook chapters or syllabus documents to automatically compile synchronized PowerPoint presentation decks and printable ReportLab revision handouts with embedded pedagogical speaker scripts.
            </p>
          </div>

          {/* Generator Export Buttons */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleExportPPT}
              disabled={downloadingPpt || !uploadStatus?.documentId}
              id="export-ppt-btn"
              title={uploadStatus?.documentId ? "Download editable .pptx presentation deck" : "Upload a document to enable PowerPoint export"}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white font-semibold text-xs shadow-lg shadow-orange-600/20 transition-all duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Presentation className="w-4 h-4" />
              <span>{downloadingPpt ? 'Generating Deck...' : 'Generate Lecture Deck (.pptx)'}</span>
            </button>

            <button
              onClick={handleExportPDF}
              disabled={downloadingPdf || !uploadStatus?.documentId}
              id="export-pdf-btn"
              title={uploadStatus?.documentId ? "Download printable .pdf study handout" : "Upload a document to enable Study Handout export"}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/20 transition-all duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FileText className="w-4 h-4" />
              <span>{downloadingPdf ? 'Exporting Handout...' : 'Export Study Handout (.pdf)'}</span>
            </button>

            <button
              onClick={handleExportJSON}
              title="Download slide outline as JSON"
              className="flex items-center gap-1.5 px-3 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs border border-slate-700 transition-colors cursor-pointer"
            >
              <FileCode className="w-4 h-4 text-slate-400" />
              <span>JSON</span>
            </button>
          </div>
        </div>
      </div>

      {/* Syllabus & Textbook Document Ingestion Hub */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Upload className="w-4 h-4 text-indigo-400" />
            <span>Curriculum Material Upload & Structure-Aware Ingestion Hub</span>
          </h3>
          <span className="text-[11px] text-slate-400">Accepted formats: PDF Textbook Chapters, Course Materials</span>
        </div>

        {/* Drag & Drop Zone */}
        <div
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer relative overflow-hidden ${
            dragActive
              ? 'border-indigo-400 bg-indigo-500/10 shadow-lg shadow-indigo-500/20 scale-[1.01]'
              : 'border-slate-800 hover:border-indigo-500/50 bg-slate-950/40 hover:bg-slate-900/30'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileInputChange}
            className="hidden"
          />

          <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto mb-3.5 border border-indigo-500/20 shadow-inner">
            <FolderPlus className="w-7 h-7" />
          </div>

          <h4 className="text-sm font-semibold text-slate-200">
            {dragActive ? 'Drop your course or textbook PDF right here' : 'Drag & drop your textbook chapter or syllabus PDF here'}
          </h4>
          <p className="text-xs text-slate-400 mt-1 max-w-lg mx-auto leading-relaxed">
            PyMuPDF extracts section headings, theoretical axioms, and bounding boxes. Scanned notes are processed via OCR fallback.
          </p>

          <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:text-white hover:border-indigo-500/40 transition-colors">
              <Upload className="w-3.5 h-3.5 text-indigo-400" />
              <span>Browse Device Files</span>
            </div>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                handleLoadDemo();
              }}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-semibold transition-all cursor-pointer shadow-sm"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Load Sample BST Lesson</span>
            </button>
          </div>

          {/* Ingestion Progress Overlay */}
          {uploading && (
            <div className="absolute inset-0 bg-slate-950/85 backdrop-blur-sm flex flex-col items-center justify-center p-6 z-20">
              <div className="w-10 h-10 border-3 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mb-3"></div>
              <p className="text-xs font-semibold text-white">{uploadPhase || 'Processing document...'}</p>
              <p className="text-[11px] text-slate-400 mt-1">Indexing vectors and synthesizing lecture slides</p>
            </div>
          )}
        </div>

        {/* Upload Status Card */}
        {uploadStatus && (
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 space-y-3">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${uploadStatus.error ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                  {uploadStatus.error ? <AlertCircle className="w-5 h-5" /> : <CheckCircle2 className="w-5 h-5" />}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h5 className="text-xs font-bold text-white">{uploadStatus.title || uploadStatus.name}</h5>
                    <span className="text-[10px] px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300 font-mono">
                      {uploadStatus.size}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    {uploadStatus.error ? (
                      <span className="text-red-400">{uploadStatus.error}</span>
                    ) : (
                      <span>{uploadStatus.chunksExtracted} sections extracted across {uploadStatus.pagesProcessed} page(s)</span>
                    )}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {uploadStatus.indexingConfirmed ? (
                  <span className="text-[10px] px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium flex items-center gap-1">
                    <CheckCircle className="w-3 h-3 text-emerald-400" />
                    Indexed in Vector DB
                  </span>
                ) : uploadStatus.error ? (
                  <span className="text-[10px] px-2.5 py-1 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20 font-medium">
                    Ingestion Failed
                  </span>
                ) : (
                  <span className="text-[10px] px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20 font-medium">
                    Processing Index
                  </span>
                )}
                <button
                  onClick={() => {
                    setUploadStatus(null);
                    setIsUploadedDocument(false);
                    handleResetOutline();
                  }}
                  className="text-[11px] text-slate-400 hover:text-slate-200 px-2.5 py-1 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
                >
                  Clear / Upload Another
                </button>
              </div>
            </div>

            {/* Document Intelligence & Analysis Dashboard */}
            {!uploadStatus.error && uploadStatus.summary && (
              <div className="pt-3 border-t border-slate-800/80 space-y-3">
                {/* Executive Summary Card */}
                <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
                  <div className="flex items-center gap-1.5 mb-1.5 text-indigo-300 text-xs font-semibold">
                    <Bookmark className="w-3.5 h-3.5" />
                    <span>Curriculum Executive Summary</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed font-normal">
                    {uploadStatus.summary}
                  </p>
                </div>

                {/* Important Concepts & Headings Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {/* Concepts */}
                  {uploadStatus.importantConcepts && uploadStatus.importantConcepts.length > 0 && (
                    <div className="p-3 rounded-xl bg-slate-950/40 border border-slate-800/80">
                      <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2 flex items-center gap-1.5">
                        <Sparkle className="w-3 h-3 text-amber-400" />
                        Important Concepts & Topics ({uploadStatus.importantConcepts.length})
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {uploadStatus.importantConcepts.map((concept, cIdx) => (
                          <span
                            key={cIdx}
                            className="text-[10px] px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-300 border border-indigo-500/20"
                          >
                            {concept}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Section Headings */}
                  {uploadStatus.sections && uploadStatus.sections.length > 0 && (
                    <div className="p-3 rounded-xl bg-slate-950/40 border border-slate-800/80">
                      <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2 flex items-center gap-1.5">
                        <ListChecks className="w-3 h-3 text-emerald-400" />
                        Sections & Headings ({uploadStatus.sections.length})
                      </span>
                      <div className="space-y-1 max-h-24 overflow-y-auto pr-1">
                        {uploadStatus.sections.map((sec, sIdx) => (
                          <div key={sIdx} className="text-[11px] text-slate-300 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0"></span>
                            <span className="line-clamp-1">{sec}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Important Portions Excerpts */}
                {uploadStatus.importantPortions && uploadStatus.importantPortions.length > 0 && (
                  <div className="p-3 rounded-xl bg-slate-950/40 border border-slate-800/80">
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2 flex items-center gap-1.5">
                      <Compass className="w-3 h-3 text-purple-400" />
                      Important Portions & Verified Citations ({uploadStatus.importantPortions.length})
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-32 overflow-y-auto pr-1">
                      {uploadStatus.importantPortions.map((port, pIdx) => (
                        <div key={pIdx} className="p-2 rounded-lg bg-slate-900/60 border border-slate-800/60 text-[11px]">
                          <div className="flex items-center justify-between text-[10px] text-slate-400 mb-1">
                            <span className="font-mono text-indigo-300">Page {port.page}</span>
                            {port.is_critical && (
                              <span className="px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 text-[9px] font-bold">CRITICAL</span>
                            )}
                          </div>
                          <p className="text-slate-300 line-clamp-2 leading-relaxed">{port.snippet}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Slide Outline Editor & Live 16:9 Presentation Studio */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl space-y-6">
        {/* Studio Action Bar */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <div className="flex flex-wrap items-center gap-2.5">
              <Presentation className="w-5 h-5 text-indigo-400" />
              <h3 className="text-base font-bold text-white tracking-tight">
                Slide Outline Editor & Live Presentation Studio
              </h3>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                {slides.length} Slides
              </span>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1">
                <Clock className="w-3 h-3 text-amber-400" />
                {totalSpeakingDuration()} lecture
              </span>

              {/* Document Grounding Tag */}
              {isUploadedDocument ? (
                <span className="text-[10px] font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                  <CheckCircle className="w-3 h-3 text-emerald-400" />
                  Grounded in: {uploadStatus?.title}
                </span>
              ) : (
                <span className="text-[10px] font-semibold px-2.5 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
                  Demo Template (Upload PDF to replace)
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Select any slide from the outline to edit bullet points, customize teacher speaker scripts, and preview the live presentation canvas.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleAddNewSlide}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md transition-colors cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Slide</span>
            </button>

            <button
              onClick={handleResetOutline}
              title="Reset slide deck to document template"
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700 transition-colors cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>

            <button
              onClick={() => setPreviewMode(previewMode === 'split' ? 'presentation' : 'split')}
              title={previewMode === 'split' ? 'Expand Presentation Canvas' : 'Show Split Editor'}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700 transition-colors cursor-pointer"
            >
              {previewMode === 'split' ? <Maximize2 className="w-3.5 h-3.5" /> : <Minimize2 className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>

        {/* Studio Workspace */}
        {slides.length === 0 ? (
          <div className="p-12 text-center rounded-2xl bg-slate-950/60 border border-slate-800 space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mx-auto">
              <Presentation className="w-7 h-7" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">No Lecture Presentation Deck Loaded</h4>
              <p className="text-xs text-slate-400 max-w-md mx-auto mt-1 leading-relaxed">
                Upload a curriculum textbook chapter or course PDF to synthesize an editable 10-slide presentation with embedded teacher talking points, or load the sample BST lesson.
              </p>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md transition-colors cursor-pointer"
              >
                <Upload className="w-4 h-4" />
                <span>Upload Course PDF</span>
              </button>
              <button
                type="button"
                onClick={handleLoadDemo}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-semibold transition-colors cursor-pointer"
              >
                <Sparkles className="w-4 h-4 text-amber-400" />
                <span>Load Sample BST Lesson</span>
              </button>
            </div>
          </div>
        ) : (
          <div className={`grid gap-6 ${previewMode === 'split' ? 'grid-cols-1 lg:grid-cols-12' : 'grid-cols-1'}`}>
            {/* Left Panel: Slide Outline Navigator */}
            {previewMode === 'split' && (
              <div className="lg:col-span-4 space-y-3">
              <div className="flex items-center justify-between px-1">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-indigo-400" />
                  Slide Deck Outline
                </span>
                <span className="text-[11px] text-slate-500">
                  {activeSlideIndex + 1} of {slides.length} selected
                </span>
              </div>

              {/* Scrollable Slide List */}
              <div className="space-y-2 max-h-[720px] overflow-y-auto pr-1">
                {slides.map((slide, index) => {
                  const isActive = index === activeSlideIndex;
                  return (
                    <div
                      key={slide.id || index}
                      onClick={() => setActiveSlideIndex(index)}
                      className={`group p-3 rounded-xl border transition-all cursor-pointer relative ${
                        isActive
                          ? 'bg-indigo-950/40 border-indigo-500 shadow-md shadow-indigo-500/10'
                          : 'bg-slate-900/40 border-slate-800/80 hover:bg-slate-900 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-start gap-2.5">
                          <span className={`text-[11px] font-mono font-bold px-1.5 py-0.5 rounded-md ${
                            isActive ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-400'
                          }`}>
                            {String(index + 1).padStart(2, '0')}
                          </span>

                          <div>
                            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-800/80 text-slate-300 border border-slate-700/60 inline-block mb-1">
                              {slide.category}
                            </span>
                            <h4 className={`text-xs font-semibold line-clamp-1 leading-snug ${
                              isActive ? 'text-white' : 'text-slate-300'
                            }`}>
                              {slide.title}
                            </h4>
                            <p className="text-[10px] text-slate-500 mt-0.5">
                              {slide.bullets?.length || 0} points · {calculateSpeakingTime(slide.notes)}
                            </p>
                          </div>
                        </div>

                        {/* Reorder & Delete Controls */}
                        <div className="flex flex-col items-center gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
                          <div className="flex items-center gap-0.5">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleMoveSlide(index, -1);
                              }}
                              disabled={index === 0}
                              title="Move Up"
                              className="p-1 text-slate-400 hover:text-white disabled:opacity-20 transition-colors"
                            >
                              <ChevronUp className="w-3 h-3" />
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleMoveSlide(index, 1);
                              }}
                              disabled={index === slides.length - 1}
                              title="Move Down"
                              className="p-1 text-slate-400 hover:text-white disabled:opacity-20 transition-colors"
                            >
                              <ChevronDown className="w-3 h-3" />
                            </button>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteSlide(index);
                            }}
                            title="Delete Slide"
                            className="p-1 text-slate-500 hover:text-rose-400 transition-colors"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}

                {/* Add Slide Bottom Button */}
                <button
                  onClick={handleAddNewSlide}
                  className="w-full py-2.5 rounded-xl border border-dashed border-slate-800 hover:border-indigo-500/60 text-slate-400 hover:text-indigo-300 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors bg-slate-950/30 cursor-pointer"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Slide {slides.length + 1}</span>
                </button>
              </div>
            </div>
          )}

          {/* Right Panel: Live 16:9 Presentation Canvas & Content Editor */}
          <div className={`${previewMode === 'split' ? 'lg:col-span-8' : 'w-full'} space-y-6`}>
            {/* Live 16:9 Presentation Canvas */}
            <div className="relative rounded-2xl overflow-hidden border border-slate-800 bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950/30 shadow-2xl p-6 sm:p-8 aspect-[16/9] flex flex-col justify-between">
              {/* Slide Presentation Header */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    {activeSlide?.category}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-slate-400 bg-slate-900/80 px-2 py-0.5 rounded-md border border-slate-800">
                      SLIDE {String(activeSlideIndex + 1).padStart(2, '0')} / {String(slides.length).padStart(2, '0')}
                    </span>
                    <span className="text-[10px] font-medium text-emerald-400 flex items-center gap-1">
                      <Sparkle className="w-3 h-3" />
                      Live Preview
                    </span>
                  </div>
                </div>

                <h3 className="text-xl sm:text-2xl font-black text-white tracking-tight leading-tight mt-2">
                  {activeSlide?.title}
                </h3>
                {activeSlide?.subtitle && (
                  <p className="text-xs text-indigo-300/80 font-medium mt-1">
                    {activeSlide?.subtitle}
                  </p>
                )}
              </div>

              {/* Slide Body: Bullets or Conceptual Diagram Cards */}
              <div className="my-auto py-4 overflow-y-auto max-h-[58%] pr-2">
                {activeSlide?.diagram && activeSlide?.diagramStages ? (
                  /* 3-Stage Process Diagram Cards */
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    {activeSlide.diagramStages.map((stage, sIdx) => (
                      <div
                        key={sIdx}
                        className="p-3.5 rounded-xl bg-slate-900/80 border border-indigo-500/30 shadow-md flex flex-col justify-between"
                      >
                        <div>
                          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider block mb-1">
                            {stage.stage}
                          </span>
                          <h5 className="text-xs font-bold text-white mb-1.5">{stage.title}</h5>
                          <p className="text-[11px] text-slate-300 leading-relaxed">{stage.description}</p>
                        </div>
                        <div className="mt-3 flex items-center justify-end text-indigo-400">
                          <ArrowRight className="w-3.5 h-3.5" />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  /* Formatted Presentation Bullet Points */
                  <ul className="space-y-2.5">
                    {activeSlide?.bullets?.map((bullet, bIdx) => (
                      <li key={bIdx} className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-200">
                        <span className="w-2 h-2 rounded-full bg-indigo-400 shrink-0 mt-1.5 shadow-sm shadow-indigo-400/50"></span>
                        <span className="leading-relaxed font-normal">{bullet}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* Slide Presentation Footer */}
              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
                <div className="flex items-center gap-2">
                  <BookOpen className="w-3.5 h-3.5 text-slate-400" />
                  <span>StudyForge OS Academic Lecture Deck</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-slate-400">{calculateSpeakingTime(activeSlide?.notes)}</span>
                  <span>Confidential — Educator Use</span>
                </div>
              </div>
            </div>

            {/* Slide Navigation Controls */}
            <div className="flex items-center justify-between px-2">
              <button
                onClick={() => setActiveSlideIndex(Math.max(0, activeSlideIndex - 1))}
                disabled={activeSlideIndex === 0}
                className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs font-semibold text-slate-300 hover:text-white border border-slate-800 disabled:opacity-30 transition-colors cursor-pointer"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Previous Slide</span>
              </button>

              <div className="flex items-center gap-1.5">
                {slides.map((_, dotIdx) => (
                  <button
                    key={dotIdx}
                    onClick={() => setActiveSlideIndex(dotIdx)}
                    className={`h-2 rounded-full transition-all cursor-pointer ${
                      dotIdx === activeSlideIndex ? 'w-6 bg-indigo-500' : 'w-2 bg-slate-800 hover:bg-slate-700'
                    }`}
                    title={`Go to Slide ${dotIdx + 1}`}
                  />
                ))}
              </div>

              <button
                onClick={() => setActiveSlideIndex(Math.min(slides.length - 1, activeSlideIndex + 1))}
                disabled={activeSlideIndex === slides.length - 1}
                className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs font-semibold text-slate-300 hover:text-white border border-slate-800 disabled:opacity-30 transition-colors cursor-pointer"
              >
                <span>Next Slide</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            {/* Slide Content & Speaker Notes Editor Tabs */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setEditorTab('content')}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-colors cursor-pointer ${
                      editorTab === 'content'
                        ? 'bg-indigo-600 text-white shadow-md'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                    }`}
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    <span>Slide Content & Bullets ({activeSlide?.bullets?.length || 0})</span>
                  </button>

                  <button
                    onClick={() => setEditorTab('notes')}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-colors cursor-pointer ${
                      editorTab === 'notes'
                        ? 'bg-indigo-600 text-white shadow-md'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                    }`}
                  >
                    <MessageSquare className="w-3.5 h-3.5" />
                    <span>Teacher Speaker Notes & Script</span>
                  </button>
                </div>

                <span className="text-[11px] text-slate-400 font-mono">
                  Slide ID: {activeSlide?.id || `slide-${activeSlideIndex + 1}`}
                </span>
              </div>

              {/* Tab 1: Slide Content & Bullets Editor */}
              {editorTab === 'content' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div className="sm:col-span-2 space-y-1">
                      <label className="text-[11px] font-semibold text-slate-400">Slide Title</label>
                      <input
                        type="text"
                        value={activeSlide?.title || ''}
                        onChange={(e) => handleTitleChange(e.target.value)}
                        placeholder="Enter slide title..."
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
                      />
                    </div>

                    <div className="space-y-1">
                      <label className="text-[11px] font-semibold text-slate-400">Category Tag</label>
                      <select
                        value={activeSlide?.category}
                        onChange={(e) => handleCategoryChange(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors cursor-pointer"
                      >
                        {SLIDE_CATEGORIES.map(cat => (
                          <option key={cat.label} value={cat.label}>{cat.label}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="text-[11px] font-semibold text-slate-400">Subtitle / Context</label>
                    <input
                      type="text"
                      value={activeSlide?.subtitle || ''}
                      onChange={(e) => handleSubtitleChange(e.target.value)}
                      placeholder="Enter slide subtitle..."
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-300 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
                    />
                  </div>

                  {/* Bullets List Management */}
                  <div className="space-y-2 pt-2">
                    <div className="flex items-center justify-between">
                      <label className="text-[11px] font-semibold text-slate-400">
                        Slide Bullet Points ({activeSlide?.bullets?.length || 0})
                      </label>
                      <span className="text-[10px] text-slate-500">Reorder with arrows or delete</span>
                    </div>

                    <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                      {activeSlide?.bullets?.map((bullet, bIdx) => (
                        <div key={bIdx} className="flex items-center gap-2 bg-slate-950/60 p-2 rounded-xl border border-slate-800/80">
                          <span className="text-[10px] font-mono text-slate-500 w-4 text-center">{bIdx + 1}</span>
                          <input
                            type="text"
                            value={bullet}
                            onChange={(e) => handleBulletChange(bIdx, e.target.value)}
                            className="flex-1 bg-transparent text-xs text-slate-200 focus:outline-none focus:text-white"
                          />
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => handleMoveBullet(bIdx, -1)}
                              disabled={bIdx === 0}
                              title="Move Up"
                              className="p-1 text-slate-500 hover:text-slate-300 disabled:opacity-20"
                            >
                              <ChevronUp className="w-3 h-3" />
                            </button>
                            <button
                              onClick={() => handleMoveBullet(bIdx, 1)}
                              disabled={bIdx === activeSlide.bullets.length - 1}
                              title="Move Down"
                              className="p-1 text-slate-500 hover:text-slate-300 disabled:opacity-20"
                            >
                              <ChevronDown className="w-3 h-3" />
                            </button>
                            <button
                              onClick={() => handleDeleteBullet(bIdx)}
                              title="Delete Bullet Point"
                              className="p-1 text-slate-500 hover:text-rose-400 transition-colors"
                            >
                              <Trash2 className="w-3 h-3" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Add Bullet Input */}
                    <div className="flex items-center gap-2 pt-1">
                      <input
                        type="text"
                        value={newBulletText}
                        onChange={(e) => setNewBulletText(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            handleAddBullet();
                          }
                        }}
                        placeholder="Type new bullet point and press Enter or Add..."
                        className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
                      />
                      <button
                        onClick={handleAddBullet}
                        disabled={!newBulletText.trim()}
                        className="px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-xs font-semibold transition-colors cursor-pointer"
                      >
                        Add Point
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Teacher Speaker Script & Notes Editor */}
              {editorTab === 'notes' && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-[11px] font-semibold text-slate-400 flex items-center gap-1.5">
                      <MessageSquare className="w-3.5 h-3.5 text-indigo-400" />
                      Educator Lecture Guide & Talking Script
                    </label>
                    <div className="flex items-center gap-3 text-[11px] text-slate-400">
                      <span>{activeSlide?.notes ? activeSlide.notes.split(/\s+/).length : 0} words</span>
                      <span className="text-amber-400 font-medium">
                        Estimated speech: {calculateSpeakingTime(activeSlide?.notes)}
                      </span>
                    </div>
                  </div>

                  <textarea
                    value={activeSlide?.notes || ''}
                    onChange={(e) => handleNotesChange(e.target.value)}
                    rows={8}
                    placeholder="Enter teacher speaker notes, instructional prompts, and classroom guidance..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors leading-relaxed font-sans"
                  />

                  <div className="p-3 rounded-xl bg-indigo-950/30 border border-indigo-500/20 text-[11px] text-indigo-300 flex items-start gap-2.5">
                    <HelpCircle className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-semibold text-white">Pedagogical Delivery Tip:</span>
                      <p className="mt-0.5 text-slate-300">
                        Speaker notes will be embedded into the native metadata of exported PowerPoint slides (`.pptx`) and displayed under teacher guidance in ReportLab revision handouts (`.pdf`).
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      </div>

      {/* Cohort Class Mastery & Error Breakdown Heatmap */}
      <WeaknessHeatmap
        initialData={uploadStatus?.documentId === 'doc_bst_demo_01' ? undefined : { overall_readiness: 0, topic_heatmap: [], class_error_distribution: {}, is_empty: true }}
        onLoadDemo={handleLoadDemo}
        onUploadClick={() => fileInputRef.current?.click()}
      />
    </div>
  );
}
