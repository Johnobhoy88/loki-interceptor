# LOKI Advanced Document Editor - User Guide

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Getting Started](#getting-started)
4. [Components](#components)
5. [Features](#features)
6. [API Reference](#api-reference)
7. [Customization](#customization)
8. [Examples](#examples)
9. [Keyboard Shortcuts](#keyboard-shortcuts)
10. [Accessibility](#accessibility)
11. [Performance](#performance)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The LOKI Advanced Document Editor is a comprehensive, production-ready document editing system built with React, TypeScript, and Monaco Editor. It provides rich text editing capabilities, real-time correction highlighting, side-by-side diff viewing, and powerful export functionality.

### Key Features

- **Rich Text Editing**: Monaco Editor integration with syntax highlighting for multiple languages
- **Real-time Corrections**: Inline correction annotations with confidence indicators
- **Diff Viewer**: Side-by-side and unified diff views with correction annotations
- **Export Functionality**: Export to DOCX, PDF, HTML, TXT, and Markdown formats
- **Search & Replace**: Advanced search with regex support
- **Version Control**: Document version tracking and comparison
- **Auto-save**: Configurable auto-save functionality
- **Keyboard Shortcuts**: Comprehensive keyboard navigation
- **Accessibility**: WCAG 2.1 AA compliant with screen reader support

### Technology Stack

- **React 18.2+**: Modern React with hooks
- **TypeScript 5.3+**: Full type safety
- **Monaco Editor 0.45+**: VS Code's editor component
- **Zustand 4.4+**: State management
- **React Diff Viewer**: Diff visualization
- **FileSaver.js**: File export capabilities
- **jsPDF**: PDF generation
- **Prism.js**: Syntax highlighting

---

## Architecture

### Component Structure

```
frontend/src/
├── components/
│   ├── editor/
│   │   ├── DocumentEditor.tsx       # Main editor component
│   │   ├── EditorToolbar.tsx        # Toolbar with actions
│   │   ├── EditorStatusBar.tsx      # Status information
│   │   ├── CorrectionMarker.tsx     # Correction indicators
│   │   ├── CorrectionPanel.tsx      # Correction details panel
│   │   ├── SearchReplace.tsx        # Search and replace UI
│   │   └── DocumentEditor.css       # Editor styles
│   ├── diff/
│   │   ├── DiffViewer.tsx           # Main diff viewer
│   │   ├── SideBySideDiff.tsx       # Side-by-side view
│   │   ├── UnifiedDiff.tsx          # Unified diff view
│   │   ├── CorrectionAnnotation.tsx # Correction annotations
│   │   └── DiffViewer.css           # Diff styles
│   └── corrections/
│       └── [Correction components]
├── lib/
│   ├── editor/
│   │   ├── editorUtils.ts           # Editor utilities
│   │   ├── autoSave.ts              # Auto-save manager
│   │   └── keyboardShortcuts.ts     # Keyboard handling
│   ├── diff/
│   │   └── diffAlgorithm.ts         # Diff computation
│   └── export/
│       └── exportUtils.ts           # Export functionality
├── hooks/
│   └── useEditor.ts                 # Editor state management
├── types/
│   └── editor.ts                    # TypeScript definitions
└── examples/
    └── [Example implementations]
```

### State Management

The editor uses Zustand for state management, providing:
- Document state
- Correction tracking
- Version history
- Search results
- Configuration settings

---

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

### Build

```bash
npm run build
```

### Running Tests

```bash
npm test
```

---

## Components

### DocumentEditor

The main editor component that integrates Monaco Editor with correction highlighting.

#### Props

```typescript
interface DocumentEditorProps {
  document: EditorDocument;
  corrections?: Correction[];
  config?: Partial<EditorConfig>;
  onContentChange?: (content: string) => void;
  onCorrectionClick?: (correction: Correction) => void;
  readOnly?: boolean;
}
```

#### Usage

```tsx
import { DocumentEditor } from '@/components/editor/DocumentEditor';

<DocumentEditor
  document={myDocument}
  corrections={corrections}
  onContentChange={handleChange}
  onCorrectionClick={handleCorrectionClick}
/>
```

### DiffViewer

Side-by-side diff comparison with correction annotations.

#### Props

```typescript
interface DiffViewerProps {
  oldValue: string;
  newValue: string;
  oldTitle?: string;
  newTitle?: string;
  splitView?: boolean;
  showDiffOnly?: boolean;
  highlightLines?: number[];
  onLineClick?: (lineNumber: number) => void;
}
```

#### Usage

```tsx
import { DiffViewer } from '@/components/diff/DiffViewer';

<DiffViewer
  oldValue={originalText}
  newValue={modifiedText}
  splitView={true}
  oldTitle="Original"
  newTitle="Modified"
/>
```

### CorrectionPanel

Displays detailed information about a correction with accept/reject actions.

#### Props

```typescript
interface CorrectionPanelProps {
  correction: Correction;
  onAccept: (correction: Correction) => void;
  onReject: (correction: Correction) => void;
  onClose: () => void;
}
```

### SearchReplace

Advanced search and replace functionality with regex support.

#### Props

```typescript
interface SearchReplaceProps {
  editor: editor.IStandaloneCodeEditor | null;
  onClose: () => void;
}
```

---

## Features

### 1. Rich Text Editing

Monaco Editor provides:
- Syntax highlighting for 100+ languages
- IntelliSense code completion
- Code folding
- Bracket matching
- Multi-cursor editing
- Virtual scrolling for large documents

### 2. Correction System

#### Correction Types

- **Grammar**: Grammatical errors
- **Spelling**: Spelling mistakes
- **Style**: Style improvements
- **Punctuation**: Punctuation errors
- **Clarity**: Clarity improvements
- **Consistency**: Consistency issues
- **Compliance**: Regulatory compliance
- **Accessibility**: Accessibility improvements

#### Confidence Levels

- **High (90-100%)**: Green indicator
- **Medium (70-89%)**: Yellow indicator
- **Low (0-69%)**: Red indicator

#### Correction Workflow

1. Corrections appear as inline decorations
2. Hover over correction to see details
3. Click to open correction panel
4. Accept or reject correction
5. Changes are applied immediately
6. Auto-save triggers (if enabled)

### 3. Diff Viewing

#### Split View

- Side-by-side comparison
- Line-by-line highlighting
- Addition, deletion, and modification indicators
- Click-to-navigate

#### Unified View

- Single-column view
- Inline change markers
- Syntax highlighting
- Compact representation

### 4. Export Functionality

#### Supported Formats

**DOCX (Microsoft Word)**
```typescript
await exportToDocx(document, {
  format: 'docx',
  includeMetadata: true,
  includeCorrections: false,
  highlightCorrections: false,
});
```

**PDF**
```typescript
await exportToPdf(document, {
  format: 'pdf',
  includeMetadata: true,
  includeCorrections: false,
  highlightCorrections: false,
});
```

**HTML**
```typescript
await exportToHtml(document, {
  format: 'html',
  includeMetadata: true,
  includeCorrections: true,
  highlightCorrections: true,
});
```

**TXT**
```typescript
await exportToTxt(document, {
  format: 'txt',
  includeMetadata: true,
  includeCorrections: false,
  highlightCorrections: false,
});
```

**Markdown**
```typescript
await exportToMarkdown(document, {
  format: 'markdown',
  includeMetadata: true,
  includeCorrections: false,
  highlightCorrections: false,
});
```

### 5. Auto-save

Configure auto-save behavior:

```typescript
const config: EditorConfig = {
  autoSave: true,
  autoSaveDelay: 3000, // 3 seconds
};
```

Auto-save triggers when:
- Content changes
- Delay period elapses
- Document is idle

### 6. Version Control

Track document versions:

```typescript
// Access version history
const versions = useEditorStore((state) => state.versions);

// Load a specific version
const loadVersion = useEditorStore((state) => state.loadVersion);
loadVersion(versions[0]);
```

### 7. Search & Replace

Advanced search features:
- Case-sensitive search
- Whole word matching
- Regular expression support
- Replace single or all occurrences
- Navigate through matches

---

## API Reference

### useEditorStore Hook

State management hook for the editor.

```typescript
const {
  document,
  corrections,
  selectedCorrection,
  updateContent,
  acceptCorrection,
  rejectCorrection,
  saveDocument,
  search,
  undo,
  redo,
} = useEditorStore();
```

#### Methods

**setDocument(document: EditorDocument)**
Set the current document.

**updateContent(content: string)**
Update document content and trigger auto-save.

**addCorrection(correction: Correction)**
Add a new correction to the document.

**acceptCorrection(correction: Correction)**
Accept and apply a correction.

**rejectCorrection(correction: Correction)**
Reject a correction.

**saveDocument(): Promise<void>**
Manually save the document.

**search(query: string, options: SearchOptions)**
Search the document with options.

**undo()**
Undo the last change.

**redo()**
Redo the last undone change.

### Editor Utilities

**applyCorrectionToDocument(document, correction): EditorDocument**
Apply a correction to a document.

**getTextAtRange(content, range): string**
Get text at a specific range.

**calculateDocumentStats(content): Stats**
Calculate document statistics (lines, words, characters).

**formatCorrectionSummary(corrections): string**
Format a summary of corrections.

**sortCorrectionsByPriority(corrections): Correction[]**
Sort corrections by priority and confidence.

### Diff Utilities

**computeLineInformation(oldText, newText): DiffChange[]**
Compute line-by-line differences.

**getDiffStats(oldText, newText): Stats**
Get diff statistics (additions, deletions).

**generateUnifiedDiff(oldText, newText): string**
Generate a unified diff patch.

---

## Customization

### Theme Customization

The editor supports light and dark themes:

```typescript
const config: EditorConfig = {
  theme: 'dark', // or 'light' or 'high-contrast'
};
```

### CSS Variables

Customize colors using CSS variables:

```css
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --border-color: #e0e0e0;
  --text-primary: #333333;
  --text-secondary: #666666;
  --primary-color: #2563eb;
}
```

### Editor Configuration

Full configuration options:

```typescript
const config: EditorConfig = {
  theme: 'light',
  fontSize: 14,
  fontFamily: 'Consolas, Monaco, monospace',
  lineHeight: 1.6,
  tabSize: 2,
  wordWrap: true,
  minimap: true,
  lineNumbers: true,
  autoSave: true,
  autoSaveDelay: 3000,
  suggestOnTriggerCharacters: true,
  quickSuggestions: true,
  accessibilitySupport: 'auto',
};
```

---

## Examples

### Basic Editor

```tsx
import React, { useState } from 'react';
import { DocumentEditor } from '@/components/editor/DocumentEditor';

export const MyEditor = () => {
  const [document] = useState({
    id: '1',
    title: 'My Document',
    content: 'Hello World!',
    language: 'markdown',
    version: 1,
    createdAt: new Date(),
    updatedAt: new Date(),
  });

  return <DocumentEditor document={document} />;
};
```

### With Corrections

```tsx
const corrections: Correction[] = [
  {
    id: 'c1',
    type: 'grammar',
    range: { startLine: 1, startColumn: 1, endLine: 1, endColumn: 6 },
    original: 'Hello',
    corrected: 'Hi',
    explanation: 'More casual greeting',
    confidence: 0.85,
    category: 'style',
    status: 'pending',
  },
];

<DocumentEditor
  document={document}
  corrections={corrections}
  onCorrectionClick={(c) => console.log(c)}
/>
```

### Custom Config

```tsx
const customConfig = {
  theme: 'dark',
  fontSize: 16,
  wordWrap: false,
  minimap: false,
  autoSave: true,
  autoSaveDelay: 5000,
};

<DocumentEditor
  document={document}
  config={customConfig}
/>
```

### Export Document

```tsx
import { exportToPdf } from '@/lib/export/exportUtils';

const handleExport = async () => {
  await exportToPdf(document, {
    format: 'pdf',
    includeMetadata: true,
    includeCorrections: false,
    highlightCorrections: false,
  });
};

<button onClick={handleExport}>Export to PDF</button>
```

---

## Keyboard Shortcuts

### General

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + S` | Save document |
| `Ctrl/Cmd + F` | Find |
| `Ctrl/Cmd + H` | Find and replace |
| `Ctrl/Cmd + Z` | Undo |
| `Ctrl/Cmd + Y` | Redo |
| `Ctrl/Cmd + Shift + Z` | Redo (alternative) |
| `Shift + Alt + F` | Format document |
| `Ctrl/Cmd + K` | Show keyboard shortcuts |
| `Escape` | Close active panel |

### Navigation

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + G` | Go to line |
| `Ctrl/Cmd + P` | Quick open |
| `Alt + ↑/↓` | Move line up/down |
| `Ctrl/Cmd + D` | Add selection to next match |
| `Ctrl/Cmd + Enter` | Accept correction |

### Editing

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + X` | Cut line |
| `Ctrl/Cmd + C` | Copy line |
| `Ctrl/Cmd + V` | Paste |
| `Ctrl/Cmd + /` | Toggle comment |
| `Tab` | Indent |
| `Shift + Tab` | Outdent |

---

## Accessibility

### Screen Reader Support

The editor is fully compatible with screen readers:
- NVDA (Windows)
- JAWS (Windows)
- VoiceOver (macOS/iOS)
- TalkBack (Android)

### ARIA Labels

All interactive elements have proper ARIA labels:
```tsx
<button aria-label="Accept correction">✓</button>
<button aria-label="Reject correction">✕</button>
```

### Keyboard Navigation

All features are accessible via keyboard:
- Tab navigation
- Arrow key navigation
- Keyboard shortcuts

### High Contrast Mode

Support for high contrast themes:
```typescript
const config = {
  theme: 'high-contrast',
  accessibilitySupport: 'on',
};
```

### Focus Indicators

Clear focus indicators for all interactive elements.

---

## Performance

### Optimization Techniques

**Virtual Scrolling**
- Renders only visible content
- Handles documents with 1M+ lines

**Code Splitting**
- Monaco Editor in separate chunk
- Lazy-loaded components
- Optimized bundle size

**Memoization**
- React.memo for components
- useMemo for expensive computations
- useCallback for event handlers

**Debouncing**
- Auto-save debouncing
- Search input debouncing
- Resize event handling

### Performance Metrics

- Time to Interactive: < 2s
- First Contentful Paint: < 1s
- Bundle Size: Monaco (~3MB), App (~200KB)
- Memory Usage: ~50MB for typical documents

### Best Practices

1. **Use virtual scrolling for large documents**
2. **Enable auto-save with appropriate delay**
3. **Lazy load corrections**
4. **Debounce search queries**
5. **Use code splitting**

---

## Troubleshooting

### Common Issues

**Editor doesn't load**
- Check Monaco Editor is properly installed
- Verify Vite configuration
- Check browser console for errors

**Auto-save not working**
- Verify `autoSave: true` in config
- Check `autoSaveDelay` setting
- Ensure save callback is provided

**Corrections not showing**
- Verify correction range is valid
- Check correction type is supported
- Ensure corrections array is passed

**Export fails**
- Check file permissions
- Verify export library is installed
- Check document content is valid

**Performance issues**
- Enable virtual scrolling
- Reduce minimap size
- Disable unused features
- Check for memory leaks

### Debug Mode

Enable debug logging:

```typescript
localStorage.setItem('editor:debug', 'true');
```

### Support

For issues and questions:
- GitHub Issues: [Repository URL]
- Documentation: [Docs URL]
- Email: support@loki.example.com

---

## License

MIT License - See LICENSE file for details.

---

## Credits

Built with:
- Monaco Editor by Microsoft
- React by Meta
- TypeScript by Microsoft
- Zustand by Poimandres
- And many other open source libraries

---

## Changelog

### v2.0.0 (2025-01-11)
- Initial release with full feature set
- Monaco Editor integration
- Diff viewer components
- Export functionality
- Comprehensive documentation

---

**End of Documentation**
