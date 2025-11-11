import React, { useState } from 'react';
import { DocumentEditor } from './components/editor';
import { DiffViewer } from './components/diff';
import { EditorDocument, Correction } from './types/editor';
import './App.css';

const sampleDocument: EditorDocument = {
  id: 'doc1',
  title: 'Welcome to LOKI Editor',
  content: `# Welcome to LOKI Advanced Document Editor

## Features

This editor provides:
- Real-time correction highlighting
- Side-by-side diff viewing
- Export to multiple formats (DOCX, PDF, HTML, TXT, Markdown)
- Advanced search and replace with regex support
- Keyboard shortcuts for productivity
- Auto-save functionality
- Version control and history

## Getting Started

Start typing to see the editor in action!

Try making some changes and watch the auto-save feature work.
Use Ctrl+F to search, Ctrl+H to find and replace.

## Corrections

The editor can highlight various types of corrections:
- Grammar errors
- Spelling mistakes
- Style improvements
- Punctuation issues
- Clarity enhancements
- Consistency problems
- Compliance requirements
- Accessibility improvements

Each correction shows a confidence level and explanation.
`,
  language: 'markdown',
  version: 1,
  createdAt: new Date(),
  updatedAt: new Date(),
  metadata: {
    author: 'LOKI System',
    tags: ['welcome', 'documentation'],
    description: 'Welcome document for LOKI Editor',
  },
};

const sampleCorrections: Correction[] = [
  {
    id: 'c1',
    type: 'grammar',
    range: { startLine: 3, startColumn: 1, endLine: 3, endColumn: 10 },
    original: 'provides:',
    corrected: 'provides the following:',
    explanation: 'More complete sentence structure',
    confidence: 0.85,
    category: 'style',
    status: 'pending',
    metadata: {
      rule: 'sentence-structure',
      severity: 'info',
      fixable: true,
    },
  },
];

function App() {
  const [document, setDocument] = useState(sampleDocument);
  const [corrections, setCorrections] = useState(sampleCorrections);
  const [view, setView] = useState<'editor' | 'diff'>('editor');

  const handleContentChange = (content: string) => {
    setDocument({ ...document, content, updatedAt: new Date() });
  };

  const handleCorrectionClick = (correction: Correction) => {
    console.log('Correction clicked:', correction);
  };

  const handleAcceptCorrection = (correction: Correction) => {
    setCorrections(corrections.filter(c => c.id !== correction.id));
  };

  const handleRejectCorrection = (correction: Correction) => {
    setCorrections(
      corrections.map(c =>
        c.id === correction.id ? { ...c, status: 'rejected' } : c
      )
    );
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>LOKI Advanced Document Editor</h1>
        <div className="view-switcher">
          <button
            className={view === 'editor' ? 'active' : ''}
            onClick={() => setView('editor')}
          >
            Editor
          </button>
          <button
            className={view === 'diff' ? 'active' : ''}
            onClick={() => setView('diff')}
          >
            Diff View
          </button>
        </div>
      </header>

      <main className="app-content">
        {view === 'editor' ? (
          <DocumentEditor
            document={document}
            corrections={corrections}
            onContentChange={handleContentChange}
            onCorrectionClick={handleCorrectionClick}
          />
        ) : (
          <DiffViewer
            oldValue={sampleDocument.content}
            newValue={document.content}
            oldTitle="Original"
            newTitle="Current"
            splitView={true}
          />
        )}
      </main>
    </div>
  );
}

export default App;
