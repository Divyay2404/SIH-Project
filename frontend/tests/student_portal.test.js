import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import React from 'react';
import { renderToString } from 'react-dom/server';
import StudentPortal from '../src/components/student/StudentPortal.jsx';
import PdfViewer from '../src/components/student/PdfViewer.jsx';

describe('StudentPortal Component & Any-PDF RAG Workflow', () => {
  test('renders StudentPortal with clear initial empty state without demo documents', () => {
    const html = renderToString(<StudentPortal />);
    assert.ok(html.includes('No study material selected'));
    assert.ok(html.includes('Upload a PDF to start studying'));
    assert.ok(html.includes('Upload PDF'));
    // Ensure hardcoded Binary_Search_Trees_Chapter.pdf is NOT in initial state
    assert.ok(!html.includes('Binary_Search_Trees_Chapter.pdf'));
  });

  test('renders MarksSelector within StudentPortal', () => {
    const html = renderToString(<StudentPortal />);
    assert.ok(html.includes('Answer Depth Scale:'));
    assert.ok(html.includes('2 Marks'));
    assert.ok(html.includes('5 Marks'));
    assert.ok(html.includes('10 Marks'));
  });

  test('PdfViewer renders empty state when no document is active', () => {
    const html = renderToString(
      <PdfViewer activeDocument={null} onUploadClick={() => {}} />
    );
    assert.ok(html.includes('No study material selected'));
    assert.ok(html.includes('Upload any course notes, syllabus, or textbook PDF'));
    assert.ok(html.includes('Upload Course PDF'));
    // Ensure no hardcoded BST chapter
    assert.ok(!html.includes('Binary_Search_Trees_Chapter.pdf'));
  });

  test('PdfViewer renders dynamic document information and total pages for arbitrary PDF', () => {
    const arbitraryDoc = {
      document_id: 'doc_chem_101',
      title: 'Chemical Thermodynamics',
      filename: 'Thermodynamics_Lecture_Notes.pdf',
      pages_count: 5,
      pages: [
        {
          page: 1,
          title: 'First Law of Thermodynamics',
          paragraphs: [
            'The first law of thermodynamics is an expression of the principle of conservation of energy.',
            'Energy can be transformed from one form to another, but cannot be created or destroyed.'
          ]
        },
        {
          page: 2,
          title: 'Enthalpy and Heat Capacities',
          paragraphs: ['Enthalpy is a property of a thermodynamic system defined as H = U + pV.']
        }
      ]
    };

    const html = renderToString(
      <PdfViewer
        activeDocument={arbitraryDoc}
        selectedPage={1}
      />
    );

    assert.ok(html.includes('Thermodynamics_Lecture_Notes.pdf'));
    assert.ok(/Page.*1.*of.*5/.test(html));
    assert.ok(html.includes('Canvas Render Engine'));
    assert.ok(!html.includes('Binary_Search_Trees_Chapter.pdf'));
  });

  test('PdfViewer scales citation bounding box coordinates for arbitrary documents', () => {
    const arbitraryDoc = {
      document_id: 'doc_os_01',
      title: 'Operating Systems Process Scheduling',
      filename: 'OS_Process_Scheduling.pdf',
      pages_count: 3,
      pages: [
        {
          page: 1,
          title: 'Process State Transitions',
          paragraphs: ['A process moves between New, Ready, Running, Waiting, and Terminated states.']
        }
      ]
    };

    const citation = {
      document_name: 'OS_Process_Scheduling.pdf',
      page_number: 1,
      snippet: 'A process moves between New, Ready, Running...',
      bounding_box: [40.0, 80.0, 480.0, 180.0]
    };

    const html = renderToString(
      <PdfViewer
        activeDocument={arbitraryDoc}
        activeCitation={citation}
        selectedPage={1}
      />
    );

    assert.ok(html.includes('Citation Bbox'));
    assert.ok(html.includes('Evidence:'));
    assert.ok(html.includes('A process moves between New, Ready, Running'));
  });
});
