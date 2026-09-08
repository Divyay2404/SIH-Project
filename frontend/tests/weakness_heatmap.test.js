import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import React from 'react';
import { renderToString } from 'react-dom/server';
import WeaknessHeatmap, { getReadinessTier, normalizeErrorType } from '../src/components/educator/WeaknessHeatmap.jsx';

describe('WeaknessHeatmap & Concept Mastery Component', () => {
  const sampleData = {
    overall_readiness: 70,
    topic_heatmap: [
      {
        topic: 'BST Concept & Properties',
        mastery: 90,
        error_type: 'None',
        status: 'Mastered',
        attempts: 60,
        error_rate: 10
      },
      {
        topic: 'BST Insertion Algorithm',
        mastery: 75,
        error_type: 'Careless Error',
        status: 'Good Progress',
        attempts: 55,
        error_rate: 25
      },
      {
        topic: 'BST Deletion (Two Children)',
        mastery: 40,
        error_type: 'Conceptual Gap',
        status: 'Critical Gap',
        attempts: 65,
        error_rate: 60,
        recommendation: 'Trigger 30-Minute Rescue Mission: School principal analogy.'
      },
      {
        topic: 'BST In-Order Traversal Steps',
        mastery: 55,
        error_type: 'Process Mistake',
        status: 'Needs Review',
        attempts: 50,
        error_rate: 45
      }
    ],
    class_error_distribution: {
      'Conceptual Gap': 45,
      'Process Mistake': 25,
      'Terminology Confusion': 20,
      'Careless Error': 10
    }
  };

  test('getReadinessTier assigns correct color, tier, and severity classes', () => {
    // Critical Gap (< 50%) -> Red / Rose
    const crit = getReadinessTier(42);
    assert.equal(crit.tier, 'critical');
    assert.equal(crit.label, 'Critical Gap');
    assert.ok(crit.colorClass.includes('rose-500'));
    assert.ok(crit.barClass.includes('rose-500'));

    // Needs Review (50 - 69%) -> Yellow / Amber
    const rev = getReadinessTier(65);
    assert.equal(rev.tier, 'warning');
    assert.equal(rev.label, 'Needs Review');
    assert.ok(rev.colorClass.includes('amber-500'));

    // Good Progress (70 - 84%) -> Indigo / Blue
    const good = getReadinessTier(78);
    assert.equal(good.tier, 'good');
    assert.equal(good.label, 'Good Progress');
    assert.ok(good.colorClass.includes('indigo-500'));

    // Mastered (>= 85%) -> Green / Emerald
    const mast = getReadinessTier(92);
    assert.equal(mast.tier, 'mastered');
    assert.equal(mast.label, 'Mastered');
    assert.ok(mast.colorClass.includes('emerald-500'));
  });

  test('normalizeErrorType maps taxonomy variations accurately', () => {
    assert.equal(normalizeErrorType('conceptual_gap'), 'Conceptual Gap');
    assert.equal(normalizeErrorType('Conceptual Gap: In-Order Successor Substitution'), 'Conceptual Gap');
    assert.equal(normalizeErrorType('process_mistake'), 'Process Mistake');
    assert.equal(normalizeErrorType('Calculation Error'), 'Process Mistake');
    assert.equal(normalizeErrorType('procedural error'), 'Process Mistake');
    assert.equal(normalizeErrorType('terminology_confusion'), 'Terminology Confusion');
    assert.equal(normalizeErrorType('careless_error'), 'Careless Error');
    assert.equal(normalizeErrorType('None'), 'None');
    assert.equal(normalizeErrorType(''), 'None');
    assert.equal(normalizeErrorType(null), 'None');
  });

  test('renders topic cells and readiness scores in static HTML markup', () => {
    const html = renderToString(React.createElement(WeaknessHeatmap, { initialData: sampleData }));

    // Verify all topic titles are present
    assert.ok(html.includes('BST Concept &amp; Properties') || html.includes('BST Concept & Properties'));
    assert.ok(html.includes('BST Insertion Algorithm'));
    assert.ok(html.includes('BST Deletion (Two Children)'));
    assert.ok(html.includes('BST In-Order Traversal Steps'));

    // Verify readiness percentages
    assert.ok(html.includes('90%'));
    assert.ok(html.includes('40%'));

    // Verify status labels
    assert.ok(html.includes('Mastered'));
    assert.ok(html.includes('Critical Gap'));

    // Verify color scale presence
    assert.ok(html.includes('bg-rose-500'));
    assert.ok(html.includes('bg-emerald-500'));

    // Verify accessible role
    assert.ok(html.includes('role="grid"'));
    assert.ok(html.includes('role="article"'));
  });

  test('renders cohort metric overview cards dynamically', () => {
    const html = renderToString(React.createElement(WeaknessHeatmap, { initialData: sampleData }));

    assert.ok(html.includes('Cohort Readiness Score'));
    assert.ok(html.includes('Top Diagnostic Bottleneck'));
    assert.ok(html.includes('Rescue Interventions'));
    assert.ok(html.includes('Dominant Error Pattern'));

    // Top bottleneck topic should be BST Deletion (lowest mastery = 40%)
    assert.ok(html.includes('BST Deletion (Two Children)'));
    assert.ok(html.includes('60% Error Rate'));
  });

  test('renders taxonomy filter buttons with canonical categories', () => {
    const html = renderToString(React.createElement(WeaknessHeatmap, { initialData: sampleData }));

    assert.ok(html.includes('All Errors'));
    assert.ok(html.includes('Conceptual Gap'));
    assert.ok(html.includes('Process Mistake'));
    assert.ok(html.includes('Terminology Confusion'));
    assert.ok(html.includes('Careless Error'));
  });

  test('renders readiness color scale legend with labels and thresholds', () => {
    const html = renderToString(React.createElement(WeaknessHeatmap, { initialData: sampleData }));

    assert.ok(html.includes('Readiness Color Scale:'));
    assert.ok(html.includes('Critical Gap (&lt; 50% Mastery / &gt; 50% Error)'));
    assert.ok(html.includes('Needs Review (50% – 69%)'));
    assert.ok(html.includes('Good Progress (70% – 84%)'));
    assert.ok(html.includes('Mastered (≥ 85%)'));
  });

  test('handles empty dataset gracefully without crashing', () => {
    const emptyData = {
      overall_readiness: 0,
      topic_heatmap: [],
      class_error_distribution: {}
    };

    const html = renderToString(React.createElement(WeaknessHeatmap, { initialData: emptyData }));
    assert.ok(html.includes('No Concepts Matching Selected Filter'));
    assert.ok(html.includes('0%'));
  });

  test('handles malformed / nullish data resiliently without throwing', () => {
    const malformedData = {
      overall_readiness: null,
      topic_heatmap: [
        { topic: null, mastery: null, error_type: null, status: null }
      ],
      class_error_distribution: null
    };

    assert.doesNotThrow(() => {
      const html = renderToString(React.createElement(WeaknessHeatmap, { initialData: malformedData }));
      assert.ok(typeof html === 'string');
    });
  });

  test('handles undefined initialData by loading fallback default data', () => {
    assert.doesNotThrow(() => {
      const html = renderToString(React.createElement(WeaknessHeatmap));
      assert.ok(html.includes('Curriculum readiness matrix') || html.includes('Class Weakness Heatmap'));
      assert.ok(html.includes('BST Concept &amp; Properties') || html.includes('BST Concept & Properties'));
    });
  });
});
