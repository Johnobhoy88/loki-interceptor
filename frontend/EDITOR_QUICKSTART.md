# LOKI Document Editor - Quick Start Guide

## Installation

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

Visit http://localhost:3000

## Basic Usage

### 1. Simple Editor

```tsx
import { DocumentEditor } from '@/components/editor';
import { EditorDocument } from '@/types/editor';

const document: EditorDocument = {
  id: '1',
  title: 'My Document',
  content: 'Start typing here...',
  language: 'markdown',
  version: 1,
  createdAt: new Date(),
  updatedAt: new Date(),
};

function MyEditor() {
  return <DocumentEditor document={document} />;
}
```

### 2. With Corrections

```tsx
const corrections = [
  {
    id: 'c1',
    type: 'grammar',
    range: { startLine: 1, startColumn: 1, endLine: 1, endColumn: 5 },
    original: 'teh',
    corrected: 'the',
    explanation: 'Spelling correction',
    confidence: 0.95,
    category: 'spelling',
    status: 'pending',
  },
];

<DocumentEditor
  document={document}
  corrections={corrections}
  onCorrectionClick={(c) => console.log(c)}
/>
```

### 3. Diff Viewer

```tsx
import { DiffViewer } from '@/components/diff';

<DiffViewer
  oldValue="Original text"
  newValue="Modified text"
  splitView={true}
/>
```

### 4. Export Document

```tsx
import { exportToPdf } from '@/lib/export';

const handleExport = async () => {
  await exportToPdf(document, {
    format: 'pdf',
    includeMetadata: true,
    includeCorrections: false,
    highlightCorrections: false,
  });
};
```

### 5. State Management

```tsx
import { useEditorStore } from '@/hooks/useEditor';

function MyComponent() {
  const { 
    document, 
    corrections, 
    acceptCorrection,
    updateContent 
  } = useEditorStore();

  return (
    <button onClick={() => acceptCorrection(corrections[0])}>
      Accept First Correction
    </button>
  );
}
```

## Keyboard Shortcuts

- `Ctrl+S` - Save
- `Ctrl+F` - Find
- `Ctrl+H` - Replace
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Shift+Alt+F` - Format

## Configuration

```tsx
const config = {
  theme: 'dark',
  fontSize: 16,
  wordWrap: true,
  minimap: false,
  autoSave: true,
  autoSaveDelay: 3000,
};

<DocumentEditor document={document} config={config} />
```

## Examples

See `frontend/src/examples/` for complete examples:
- BasicEditorExample.tsx
- DiffViewerExample.tsx
- ExportExample.tsx
- SearchReplaceExample.tsx

## Full Documentation

See [EDITOR_DOCUMENTATION.md](../../EDITOR_DOCUMENTATION.md) for complete documentation.

## Support

For issues, check the troubleshooting section in the main documentation.
