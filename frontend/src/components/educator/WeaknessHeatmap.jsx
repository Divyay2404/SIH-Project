import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Layers,
  AlertCircle,
  BarChart3,
  TrendingDown,
  Filter,
  RefreshCw,
  CheckCircle2,
  HelpCircle,
  Search,
  ArrowUpDown,
  Flame,
  Lightbulb,
  X,
  Target,
  SlidersHorizontal,
  ChevronRight,
  UploadCloud,
  Sparkles
} from 'lucide-react';
import { apiUrl } from '../../config/api';

/**
 * Standard project error taxonomy categories and their pedagogical metadata.
 * Aligned with backend/app/diagnostics/learner_state.py
 */
const CANONICAL_TAXONOMY = [
  {
    key: 'Conceptual Gap',
    aliases: ['conceptual_gap', 'Conceptual Gap: In-Order Successor Substitution'],
    label: 'Conceptual Gap',
    shortDesc: 'Fundamental concept or invariant misunderstanding',
    color: 'border-rose-500/40 text-rose-300 bg-rose-500/10 hover:bg-rose-500/20',
    badgeColor: 'bg-rose-500/20 text-rose-300 border-rose-500/30'
  },
  {
    key: 'Process Mistake',
    aliases: ['process_mistake', 'Process / Calculation Mistake', 'Calculation Error', 'Procedural Error'],
    label: 'Process Mistake',
    shortDesc: 'Step sequence, pointer manipulation, or calculation slip',
    color: 'border-amber-500/40 text-amber-300 bg-amber-500/10 hover:bg-amber-500/20',
    badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/30'
  },
  {
    key: 'Terminology Confusion',
    aliases: ['terminology_confusion'],
    label: 'Terminology Confusion',
    shortDesc: 'Conflating traversal names, definitions, or notation',
    color: 'border-sky-500/40 text-sky-300 bg-sky-500/10 hover:bg-sky-500/20',
    badgeColor: 'bg-sky-500/20 text-sky-300 border-sky-500/30'
  },
  {
    key: 'Careless Error',
    aliases: ['careless_error'],
    label: 'Careless Error',
    shortDesc: 'Overlooked boundary condition or accidental option selection',
    color: 'border-violet-500/40 text-violet-300 bg-violet-500/10 hover:bg-violet-500/20',
    badgeColor: 'bg-violet-500/20 text-violet-300 border-violet-500/30'
  }
];

/**
 * Canonical baseline dataset used for fallback & initial rendering.
 * Ensures the widget is immediately functional even when offline or awaiting API response.
 */
const DEFAULT_FALLBACK_DATA = {
  overall_readiness: 72,
  topic_heatmap: [
    {
      topic: 'BST Concept & Properties',
      mastery: 88,
      error_type: 'None',
      status: 'Mastered',
      attempts: 54,
      error_rate: 12,
      recommendation: 'Foundational baseline mastered. Advance cohort to balanced tree structures.'
    },
    {
      topic: 'BST Insertion Algorithm',
      mastery: 78,
      error_type: 'Careless Error',
      status: 'Good Progress',
      attempts: 52,
      error_rate: 22,
      recommendation: 'Reinforce duplicate key insertion invariants and null pointer edge checks.'
    },
    {
      topic: 'BST Deletion (Two Children)',
      mastery: 42,
      error_type: 'Conceptual Gap',
      status: 'Critical Gap',
      attempts: 61,
      error_rate: 58,
      recommendation: 'Trigger 30-Minute Rescue Mission: School principal in-order successor analogy.'
    },
    {
      topic: 'BST In-Order Traversal Steps',
      mastery: 56,
      error_type: 'Process Mistake',
      status: 'Needs Review',
      attempts: 48,
      error_rate: 44,
      recommendation: 'Walk through 3-step pointer re-linking sequence on physical whiteboard.'
    },
    {
      topic: 'Time & Space Complexity Bounds',
      mastery: 68,
      error_type: 'Terminology Confusion',
      status: 'Needs Review',
      attempts: 50,
      error_rate: 32,
      recommendation: 'Clarify worst-case skewed tree O(N) vs average-case balanced tree O(log N).'
    },
    {
      topic: 'AVL Rotation & Height Balance',
      mastery: 38,
      error_type: 'Conceptual Gap',
      status: 'Critical Gap',
      attempts: 58,
      error_rate: 62,
      recommendation: 'Deploy visual pivot rotation animation before next assessment quiz.'
    }
  ],
  class_error_distribution: {
    'Conceptual Gap': 45,
    'Process Mistake': 25,
    'Terminology Confusion': 20,
    'Careless Error': 10
  }
};

/**
 * Maps mastery percentage to visual tiers, colors, and accessibility labels.
 */
export function getReadinessTier(mastery = 0) {
  const safeMastery = typeof mastery === 'number' && !isNaN(mastery) ? mastery : 0;
  if (safeMastery >= 85) {
    return {
      tier: 'mastered',
      label: 'Mastered',
      colorClass: 'bg-emerald-500/15 border-emerald-500/40 text-emerald-200 hover:border-emerald-400 hover:bg-emerald-500/25',
      badgeClass: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
      barClass: 'bg-emerald-400',
      dotClass: 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]',
      severity: 'success'
    };
  }
  if (safeMastery >= 70) {
    return {
      tier: 'good',
      label: 'Good Progress',
      colorClass: 'bg-indigo-500/15 border-indigo-500/40 text-indigo-200 hover:border-indigo-400 hover:bg-indigo-500/25',
      badgeClass: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40',
      barClass: 'bg-indigo-400',
      dotClass: 'bg-indigo-400 shadow-[0_0_8px_rgba(129,140,248,0.6)]',
      severity: 'info'
    };
  }
  if (safeMastery >= 50) {
    return {
      tier: 'warning',
      label: 'Needs Review',
      colorClass: 'bg-amber-500/15 border-amber-500/40 text-amber-200 hover:border-amber-400 hover:bg-amber-500/25',
      badgeClass: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
      barClass: 'bg-amber-400',
      dotClass: 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)]',
      severity: 'warning'
    };
  }
  return {
    tier: 'critical',
    label: 'Critical Gap',
    colorClass: 'bg-rose-500/15 border-rose-500/40 text-rose-200 hover:border-rose-400 hover:bg-rose-500/25',
    badgeClass: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
    barClass: 'bg-rose-500',
    dotClass: 'bg-rose-400 animate-pulse shadow-[0_0_8px_rgba(244,63,94,0.7)]',
    severity: 'critical'
  };
}

/**
 * Normalizes error type names for comparison across backend variations.
 */
export function normalizeErrorType(errorType = '') {
  if (!errorType || errorType === 'None' || errorType === 'none') return 'None';
  const lower = String(errorType).toLowerCase();
  if (lower.includes('concept')) return 'Conceptual Gap';
  if (lower.includes('process') || lower.includes('procedur') || lower.includes('calculation')) return 'Process Mistake';
  if (lower.includes('terminol')) return 'Terminology Confusion';
  if (lower.includes('careless')) return 'Careless Error';
  return errorType;
}

/**
 * Main WeaknessHeatmap & Concept Mastery Component
 */
export default function WeaknessHeatmap({
  initialData = DEFAULT_FALLBACK_DATA,
  onLoadDemo = null,
  onUploadClick = null
}) {
  const [heatmapData, setHeatmapData] = useState(() => {
    if (initialData !== undefined && initialData !== null) {
      return initialData;
    }
    return DEFAULT_FALLBACK_DATA;
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTaxonomy, setSelectedTaxonomy] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('weakest'); // 'weakest' | 'strongest' | 'alphabetical'
  const [activeTooltipItem, setActiveTooltipItem] = useState(null);
  const [pinnedItem, setPinnedItem] = useState(null);

  // Fetch real-time class readiness analytics from backend
  const fetchReadiness = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(apiUrl('/api/readiness'), {
        headers: { Accept: 'application/json' }
      });
      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}: ${res.statusText}`);
      }
      const data = await res.json();
      if (data && typeof data === 'object') {
        if (data.is_empty || !Array.isArray(data.topic_heatmap) || data.topic_heatmap.length === 0) {
          setHeatmapData({
            overall_readiness: 0,
            topic_heatmap: [],
            class_error_distribution: {},
            is_empty: true
          });
        } else {
          setHeatmapData({
            overall_readiness: typeof data.overall_readiness === 'number' ? data.overall_readiness : 0,
            topic_heatmap: data.topic_heatmap,
            class_error_distribution: data.class_error_distribution && typeof data.class_error_distribution === 'object'
              ? data.class_error_distribution
              : {},
            is_empty: false
          });
        }
      }
    } catch (err) {
      console.warn('WeaknessHeatmap: Error fetching diagnostic analytics:', err.message);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReadiness();
  }, [fetchReadiness]);

  // Safe accessor for topics array
  const rawTopics = useMemo(() => {
    return Array.isArray(heatmapData?.topic_heatmap) ? heatmapData.topic_heatmap : [];
  }, [heatmapData]);

  // Dynamic calculations for Overview Metrics
  const metrics = useMemo(() => {
    const totalTopics = rawTopics.length;
    if (totalTopics === 0) {
      return {
        overallReadiness: heatmapData?.overall_readiness ?? 0,
        bottleneckTopic: null,
        criticalCount: 0,
        masteredCount: 0,
        dominantError: 'None'
      };
    }

    const calculatedAvg = Math.round(
      rawTopics.reduce((sum, t) => sum + (typeof t.mastery === 'number' ? t.mastery : 0), 0) / totalTopics
    );
    const overallReadiness = typeof heatmapData?.overall_readiness === 'number'
      ? heatmapData.overall_readiness
      : calculatedAvg;

    // Find the topic with the lowest mastery / highest error rate
    const sortedByWeakness = [...rawTopics].sort((a, b) => (a.mastery ?? 0) - (b.mastery ?? 0));
    const bottleneckTopic = sortedByWeakness[0] || null;

    // Count topics by severity
    const criticalCount = rawTopics.filter(t => (t.mastery ?? 0) < 50 || t.status === 'Critical Gap').length;
    const masteredCount = rawTopics.filter(t => (t.mastery ?? 0) >= 85).length;

    // Determine dominant mistake category from distribution
    const dist = heatmapData?.class_error_distribution || {};
    let dominantError = 'None';
    let maxDistVal = -1;
    for (const [cat, val] of Object.entries(dist)) {
      if (typeof val === 'number' && val > maxDistVal) {
        maxDistVal = val;
        dominantError = cat;
      }
    }

    return {
      overallReadiness,
      bottleneckTopic,
      criticalCount,
      masteredCount,
      dominantError
    };
  }, [rawTopics, heatmapData]);

  // Filter and sort topics
  const filteredTopics = useMemo(() => {
    let list = rawTopics.map(item => {
      const mastery = typeof item.mastery === 'number' ? item.mastery : 0;
      const errorRate = typeof item.error_rate === 'number' ? item.error_rate : Math.max(0, 100 - mastery);
      const normalizedError = normalizeErrorType(item.error_type);
      return {
        ...item,
        mastery,
        error_rate: errorRate,
        normalized_error: normalizedError,
        tierInfo: getReadinessTier(mastery)
      };
    });

    // Taxonomy filtering
    if (selectedTaxonomy !== 'ALL') {
      list = list.filter(item => {
        return item.normalized_error === selectedTaxonomy;
      });
    }

    // Search query filtering
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      list = list.filter(item => {
        const title = (item.topic || '').toLowerCase();
        const err = (item.error_type || '').toLowerCase();
        const status = (item.status || '').toLowerCase();
        return title.includes(q) || err.includes(q) || status.includes(q);
      });
    }

    // Sorting
    list.sort((a, b) => {
      if (sortBy === 'weakest') {
        return a.mastery - b.mastery; // lowest mastery (highest error) first
      }
      if (sortBy === 'strongest') {
        return b.mastery - a.mastery; // highest mastery first
      }
      if (sortBy === 'alphabetical') {
        return (a.topic || '').localeCompare(b.topic || '');
      }
      return 0;
    });

    return list;
  }, [rawTopics, selectedTaxonomy, searchQuery, sortBy]);

  return (
    <section
      aria-label="Class Weakness Heatmap and Concept Mastery"
      className="space-y-6 pt-4"
    >
      {/* Overview Analytics Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Cohort Readiness */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 relative overflow-hidden transition-all duration-200 hover:border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              Cohort Readiness Score
            </span>
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <BarChart3 className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2.5">
            <span className="text-3xl font-bold text-white tracking-tight font-mono">
              {metrics.overallReadiness}%
            </span>
            <span className="text-xs text-emerald-400 font-semibold flex items-center gap-0.5">
              +4.2% trend
            </span>
          </div>
          <div className="w-full h-2 bg-slate-800 rounded-full mt-3 overflow-hidden p-0.5 border border-slate-700/50">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(0, metrics.overallReadiness))}%` }}
              role="progressbar"
              aria-valuenow={metrics.overallReadiness}
              aria-valuemin="0"
              aria-valuemax="100"
              aria-label="Overall readiness percentage"
            />
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            {metrics.masteredCount} of {rawTopics.length} topics currently mastered
          </p>
        </div>

        {/* Metric 2: Top Bottleneck */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 relative overflow-hidden transition-all duration-200 hover:border-rose-900/40">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              Top Diagnostic Bottleneck
            </span>
            <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <AlertCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-bold text-rose-300 truncate" title={metrics.bottleneckTopic?.topic || 'None'}>
              {metrics.bottleneckTopic?.topic || 'No Bottlenecks'}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/30">
              {metrics.bottleneckTopic ? `${100 - metrics.bottleneckTopic.mastery}% Error Rate` : '0%'}
            </span>
            <span className="text-xs text-slate-400 truncate">
              {metrics.bottleneckTopic?.error_type || 'Healthy'}
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-2 line-clamp-1">
            Lowest readiness across cohort submissions
          </p>
        </div>

        {/* Metric 3: Active Rescue Missions */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 relative overflow-hidden transition-all duration-200 hover:border-amber-900/40">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              Rescue Interventions
            </span>
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <TrendingDown className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-amber-300 font-mono">
              {metrics.criticalCount}
            </span>
            <span className="text-xs text-slate-400">critical concepts</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            {metrics.criticalCount > 0
              ? 'Targeted real-world analogies recommended for high error rates'
              : 'All topics are performing above critical thresholds'}
          </p>
        </div>

        {/* Metric 4: Dominant Mistake Pattern */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 relative overflow-hidden transition-all duration-200 hover:border-indigo-900/40">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              Dominant Error Pattern
            </span>
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Flame className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-bold text-purple-200 truncate">
              {metrics.dominantError}
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Primary category driving student misconceptions in quizzes
          </p>
        </div>
      </div>

      {/* Main Heatmap Container */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6 relative">
        {/* Header with Title & Refresh */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
                <Layers className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <span>Class Weakness Heatmap & Concept Mastery</span>
                  <span className={`text-xs font-normal px-2 py-0.5 rounded-full border ${
                    (heatmapData === DEFAULT_FALLBACK_DATA || error || (heatmapData?.topic_heatmap && heatmapData.topic_heatmap.some(t => t.topic && t.topic.includes('BST'))))
                      ? 'bg-amber-500/15 border-amber-500/30 text-amber-300'
                      : 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
                  }`}>
                    {(heatmapData === DEFAULT_FALLBACK_DATA || error || (heatmapData?.topic_heatmap && heatmapData.topic_heatmap.some(t => t.topic && t.topic.includes('BST'))))
                      ? 'Sample Analytics (Demo / Fallback)'
                      : 'Live Diagnostics'}
                  </span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Interactive curriculum readiness matrix mapping student cognitive bottlenecks to mistake taxonomy
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2.5 self-start md:self-auto">
            <button
              onClick={fetchReadiness}
              disabled={loading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-900 text-slate-300 border border-slate-800 hover:border-slate-700 hover:text-white transition-all disabled:opacity-50"
              title="Refresh diagnostic analytics"
              aria-label="Refresh diagnostic analytics"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-indigo-400' : ''}`} />
              <span>{loading ? 'Refreshing...' : 'Refresh Matrix'}</span>
            </button>
          </div>
        </div>

        {/* Filter Controls & Search Toolbar */}
        <div className="space-y-3">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            {/* Taxonomy Filter Pills */}
            <div className="flex items-center gap-1.5 flex-wrap" role="group" aria-label="Mistake Taxonomy Filter">
              <span className="text-xs text-slate-400 font-semibold mr-1 flex items-center gap-1">
                <Filter className="w-3.5 h-3.5 text-indigo-400" />
                <span>Taxonomy:</span>
              </span>

              {/* All Errors Button */}
              <button
                type="button"
                onClick={() => setSelectedTaxonomy('ALL')}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all flex items-center gap-1.5 border ${
                  selectedTaxonomy === 'ALL'
                    ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/20 font-semibold'
                    : 'bg-slate-900/90 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200'
                }`}
                aria-pressed={selectedTaxonomy === 'ALL'}
              >
                <span>All Errors</span>
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                    selectedTaxonomy === 'ALL' ? 'bg-indigo-700 text-white' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {rawTopics.length}
                </span>
              </button>

              {/* Taxonomy Categories */}
              {CANONICAL_TAXONOMY.map(tax => {
                const count = rawTopics.filter(t => normalizeErrorType(t.error_type) === tax.key).length;
                const isSelected = selectedTaxonomy === tax.key;

                return (
                  <button
                    key={tax.key}
                    type="button"
                    onClick={() => setSelectedTaxonomy(tax.key)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all flex items-center gap-1.5 border ${
                      isSelected
                        ? `${tax.color} font-semibold shadow-md border-opacity-100 ring-1 ring-current`
                        : 'bg-slate-900/90 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200'
                    }`}
                    aria-pressed={isSelected}
                    title={tax.shortDesc}
                  >
                    <span>{tax.label}</span>
                    <span
                      className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                        isSelected ? 'bg-slate-950/80 text-white' : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {count}
                    </span>
                  </button>
                );
              })}
            </div>

            {/* Search and Sort Toolbar */}
            <div className="flex items-center gap-2 self-stretch sm:self-auto">
              {/* Search input */}
              <div className="relative flex-1 sm:w-48">
                <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  placeholder="Filter topic..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
                  aria-label="Filter topic by name"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                    aria-label="Clear search query"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </div>

              {/* Sort Selector */}
              <div className="relative">
                <select
                  value={sortBy}
                  onChange={e => setSortBy(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-indigo-500 transition-colors cursor-pointer appearance-none pr-7"
                  aria-label="Sort topics"
                >
                  <option value="weakest">Highest Error Rate</option>
                  <option value="strongest">Highest Mastery</option>
                  <option value="alphabetical">A-Z Name</option>
                </select>
                <ArrowUpDown className="w-3 h-3 text-slate-500 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
            </div>
          </div>

          {/* Active Filter Status & Reset Banner */}
          {(selectedTaxonomy !== 'ALL' || searchQuery) && (
            <div className="flex items-center justify-between text-xs bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-slate-300">
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Filtering:</span>
                {selectedTaxonomy !== 'ALL' && (
                  <span className="px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-500/30 text-[11px] font-medium flex items-center gap-1">
                    Taxonomy: {selectedTaxonomy}
                    <button
                      onClick={() => setSelectedTaxonomy('ALL')}
                      className="hover:text-white"
                      aria-label="Remove taxonomy filter"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                )}
                {searchQuery && (
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[11px] font-medium flex items-center gap-1">
                    Query: "{searchQuery}"
                    <button
                      onClick={() => setSearchQuery('')}
                      className="hover:text-white"
                      aria-label="Remove search filter"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                )}
                <span className="text-slate-400">
                  Showing {filteredTopics.length} of {rawTopics.length} concepts
                </span>
              </div>

              <button
                onClick={() => {
                  setSelectedTaxonomy('ALL');
                  setSearchQuery('');
                }}
                className="text-indigo-400 hover:text-indigo-300 text-xs font-semibold underline underline-offset-2"
              >
                Reset All Filters
              </button>
            </div>
          )}
        </div>

        {/* Color Scale Legend */}
        <div className="flex flex-wrap items-center justify-between gap-3 text-xs p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <div className="flex items-center gap-1.5 text-slate-400 font-semibold">
            <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
            <span>Readiness Color Scale:</span>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-[11px]">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded bg-rose-500/80 border border-rose-400 inline-block shadow-sm" />
              <span className="text-rose-300 font-medium">Critical Gap (&lt; 50% Mastery / &gt; 50% Error)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded bg-amber-500/80 border border-amber-400 inline-block shadow-sm" />
              <span className="text-amber-300 font-medium">Needs Review (50% – 69%)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded bg-indigo-500/80 border border-indigo-400 inline-block shadow-sm" />
              <span className="text-indigo-300 font-medium">Good Progress (70% – 84%)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded bg-emerald-500/80 border border-emerald-400 inline-block shadow-sm" />
              <span className="text-emerald-300 font-medium">Mastered (≥ 85%)</span>
            </div>
          </div>
        </div>

        {/* API Error Banner if offline */}
        {error && (
          <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-300 flex items-start justify-between gap-2">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-amber-400" />
              <span>
                <strong>Live Sync Notice:</strong> Backend analytics server not reachable ({error}). Displaying local diagnostic twin cache.
              </span>
            </div>
            <button
              onClick={fetchReadiness}
              className="px-2 py-0.5 rounded bg-amber-500/20 hover:bg-amber-500/30 font-semibold text-[11px] shrink-0"
            >
              Retry Sync
            </button>
          </div>
        )}

        {/* Loading Skeleton */}
        {loading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 animate-pulse">
            {[1, 2, 3, 4].map(idx => (
              <div key={idx} className="h-36 rounded-xl bg-slate-900 border border-slate-800 p-4 space-y-3">
                <div className="h-4 bg-slate-800 rounded w-3/4" />
                <div className="h-3 bg-slate-800/60 rounded w-1/2" />
                <div className="h-2 bg-slate-800 rounded w-full mt-4" />
                <div className="h-4 bg-slate-800/40 rounded w-2/3" />
              </div>
            ))}
          </div>
        )}

        {/* Empty State: No topics yet */}
        {!loading && rawTopics.length === 0 && (
          <div className="p-8 text-center rounded-2xl bg-slate-950/60 border border-slate-800 space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mx-auto text-indigo-400">
              <Layers className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-200">No Concepts Matching Selected Filter</h4>
              <p className="text-xs text-slate-400 max-w-md mx-auto mt-1 leading-relaxed">
                No Diagnostic Cohort Data Available. Student assessment attempts and concept error distributions will automatically appear here once diagnostic quizzes are taken for the active curriculum.
              </p>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-3 pt-1">
              {onUploadClick && (
                <button
                  onClick={onUploadClick}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white transition-colors cursor-pointer"
                >
                  <UploadCloud className="w-3.5 h-3.5" />
                  <span>Upload Curriculum PDF</span>
                </button>
              )}
              {onLoadDemo && (
                <button
                  onClick={onLoadDemo}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-semibold transition-colors cursor-pointer"
                >
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                  <span>Load Sample BST Demo</span>
                </button>
              )}
            </div>
          </div>
        )}

        {/* Empty State: Filters match 0 */}
        {!loading && rawTopics.length > 0 && filteredTopics.length === 0 && (
          <div className="p-8 text-center rounded-2xl bg-slate-950/60 border border-slate-800 space-y-3">
            <div className="w-10 h-10 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto text-slate-400">
              <SlidersHorizontal className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-slate-200">No Concepts Matching Selected Filter</h4>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              No topics in this curriculum match the "{selectedTaxonomy}" taxonomy filter or search query.
            </p>
            <button
              onClick={() => {
                setSelectedTaxonomy('ALL');
                setSearchQuery('');
              }}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white transition-colors cursor-pointer"
            >
              <span>Reset Filters</span>
            </button>
          </div>
        )}

        {/* Heatmap Grid */}
        {!loading && filteredTopics.length > 0 && (
          <div
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
            role="grid"
            aria-label="Topics Readiness Heatmap"
          >
            {filteredTopics.map((item, idx) => {
              const isPinned = pinnedItem?.topic === item.topic;
              const isHovered = activeTooltipItem?.topic === item.topic;
              const isActive = isPinned || isHovered;

              return (
                <div
                  key={idx}
                  role="article"
                  tabIndex={0}
                  aria-label={`${item.topic}: ${item.mastery}% readiness, error rate ${item.error_rate}%, top error: ${item.error_type}`}
                  aria-expanded={isActive}
                  onMouseEnter={() => setActiveTooltipItem(item)}
                  onMouseLeave={() => setActiveTooltipItem(null)}
                  onFocus={() => setActiveTooltipItem(item)}
                  onBlur={() => setActiveTooltipItem(null)}
                  onClick={() => setPinnedItem(isPinned ? null : item)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      setPinnedItem(isPinned ? null : item);
                    } else if (e.key === 'Escape') {
                      setPinnedItem(null);
                      setActiveTooltipItem(null);
                    }
                  }}
                  className={`group relative p-4 rounded-xl border transition-all duration-200 cursor-pointer select-none flex flex-col justify-between ${item.tierInfo.colorClass} ${
                    isActive ? 'ring-2 ring-indigo-400 shadow-xl scale-[1.02] z-20' : 'hover:scale-[1.01]'
                  }`}
                >
                  <div>
                    {/* Top row: Status Indicator & Score */}
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${item.tierInfo.dotClass}`} />
                        <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${item.tierInfo.badgeClass}`}>
                          {item.tierInfo.label}
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="font-mono text-base font-bold tracking-tight">
                          {item.mastery}%
                        </span>
                        <div className="text-[10px] opacity-70">readiness</div>
                      </div>
                    </div>

                    {/* Topic Title */}
                    <h4 className="text-xs sm:text-sm font-semibold text-slate-100 group-hover:text-white transition-colors leading-snug line-clamp-2 mt-1">
                      {item.topic}
                    </h4>
                  </div>

                  {/* Bottom metrics & Error breakdown */}
                  <div className="mt-3 pt-3 border-t border-white/10 space-y-2">
                    {/* Progress visual bar */}
                    <div className="w-full h-1.5 bg-slate-900/80 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${item.tierInfo.barClass} rounded-full transition-all duration-300`}
                        style={{ width: `${Math.min(100, Math.max(0, item.mastery))}%` }}
                      />
                    </div>

                    <div className="flex items-center justify-between text-[11px] opacity-90">
                      <span className="flex items-center gap-1 font-medium truncate" title={item.error_type}>
                        <span className="text-slate-400">Error:</span>
                        <span className={item.error_type === 'None' ? 'text-emerald-300 font-semibold' : 'font-semibold'}>
                          {item.error_type}
                        </span>
                      </span>

                      <span className="font-mono text-[10px] text-slate-300 shrink-0 ml-1">
                        {item.error_rate}% error
                      </span>
                    </div>
                  </div>

                  {/* Hover / Focus Tooltip Overlay */}
                  {isHovered && !pinnedItem && (
                    <div
                      role="tooltip"
                      id={`tooltip-${idx}`}
                      className="absolute left-1/2 -bottom-2 translate-y-full -translate-x-1/2 w-72 p-3.5 rounded-xl bg-slate-950/95 backdrop-blur-md border border-slate-700 shadow-2xl z-30 pointer-events-none text-left animate-in fade-in zoom-in-95 duration-150"
                    >
                      <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-2">
                        <span className="text-[11px] font-bold text-white truncate max-w-[180px]">
                          {item.topic}
                        </span>
                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${item.tierInfo.badgeClass}`}>
                          {item.tierInfo.label}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-xs mb-2.5">
                        <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-400 block">Readiness</span>
                          <span className="font-bold text-white font-mono">{item.mastery}%</span>
                        </div>
                        <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-400 block">Error Rate</span>
                          <span className="font-bold text-rose-300 font-mono">{item.error_rate}%</span>
                        </div>
                      </div>

                      <div className="space-y-1 text-[11px] text-slate-300">
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400">Top Error:</span>
                          <span className="font-semibold text-amber-300">{item.error_type}</span>
                        </div>
                        {item.attempts && (
                          <div className="flex items-center justify-between">
                            <span className="text-slate-400">Quiz Attempts:</span>
                            <span className="font-mono text-slate-200">{item.attempts} submissions</span>
                          </div>
                        )}
                      </div>

                      {item.recommendation && (
                        <div className="mt-2.5 p-2 rounded-lg bg-indigo-950/40 border border-indigo-500/30 text-[10px] text-indigo-300 flex items-start gap-1.5">
                          <Lightbulb className="w-3.5 h-3.5 shrink-0 text-indigo-400 mt-0.5" />
                          <span>{item.recommendation}</span>
                        </div>
                      )}

                      <div className="mt-2 text-[9px] text-slate-500 text-center">
                        Click or press Enter to pin inspection details
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Pinned Topic Inspector Modal / Drawer */}
        {pinnedItem && (
          <div
            className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-150"
            role="dialog"
            aria-modal="true"
            aria-labelledby="pinned-topic-title"
          >
            <div className="glass-panel w-full max-w-lg rounded-2xl border border-slate-700 p-6 relative shadow-2xl space-y-4">
              <button
                onClick={() => setPinnedItem(null)}
                className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
                aria-label="Close details inspector"
              >
                <X className="w-5 h-5" />
              </button>

              <div className="flex items-start gap-3">
                <div className={`p-3 rounded-xl ${pinnedItem.tierInfo.badgeClass} shrink-0`}>
                  <Target className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${pinnedItem.tierInfo.badgeClass}`}>
                      {pinnedItem.tierInfo.label}
                    </span>
                    <span className="text-xs text-slate-400">Topic Diagnostic Card</span>
                  </div>
                  <h3 id="pinned-topic-title" className="text-lg font-bold text-white mt-1">
                    {pinnedItem.topic}
                  </h3>
                </div>
              </div>

              {/* Stats Matrix */}
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
                  <span className="text-[11px] text-slate-400 block">Class Readiness</span>
                  <span className="text-2xl font-bold text-white font-mono">{pinnedItem.mastery}%</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
                  <span className="text-[11px] text-slate-400 block">Error Rate</span>
                  <span className="text-2xl font-bold text-rose-300 font-mono">{pinnedItem.error_rate}%</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
                  <span className="text-[11px] text-slate-400 block">Total Attempts</span>
                  <span className="text-2xl font-bold text-indigo-300 font-mono">
                    {pinnedItem.attempts || '50+'}
                  </span>
                </div>
              </div>

              {/* Error Taxonomy Analysis */}
              <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400 font-medium">Class Error Taxonomy Pattern:</span>
                  <span className="px-2 py-0.5 rounded font-semibold text-amber-300 bg-amber-500/10 border border-amber-500/20">
                    {pinnedItem.error_type}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Students struggling with this concept predominantly fail quiz checks involving{' '}
                  <strong className="text-white">{pinnedItem.error_type}</strong>.
                </p>
              </div>

              {/* Actionable Pedagogical Intervention */}
              <div className="p-4 rounded-xl bg-indigo-950/40 border border-indigo-500/30 space-y-2">
                <div className="flex items-center gap-2 text-xs font-bold text-indigo-300">
                  <Lightbulb className="w-4 h-4 text-indigo-400 shrink-0" />
                  <span>Educator Action Recommendation</span>
                </div>
                <p className="text-xs text-indigo-200 leading-relaxed">
                  {pinnedItem.recommendation ||
                    'Review foundational invariants with interactive visual examples before scheduling the next adaptive quiz cycle.'}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  onClick={() => setPinnedItem(null)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-colors"
                >
                  Close Inspection
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
