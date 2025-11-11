# LOKI Advanced Document Editor

A comprehensive, production-ready document editor system with real-time correction highlighting, diff viewing, and multi-format export capabilities.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm test
```

## 📚 Features

- **Rich Text Editing** with Monaco Editor
- **Real-time Corrections** with 8 correction types
- **Side-by-Side Diff Viewer** with annotations
- **Multi-Format Export** (DOCX, PDF, HTML, TXT, Markdown)
- **Advanced Search & Replace** with regex
- **Version Control** and history
- **Auto-Save** functionality
- **Keyboard Shortcuts** (12 shortcuts)
- **Full Accessibility** (WCAG 2.1 AA)

## 📖 Documentation

- [Complete Documentation](../EDITOR_DOCUMENTATION.md) - 600+ line comprehensive guide
- [Quick Start Guide](EDITOR_QUICKSTART.md) - Get started quickly
- [Delivery Report](../AGENT_18_DELIVERY_REPORT.md) - Project summary

## 💡 Usage

### Basic Editor
```tsx
import { DocumentEditor } from '@/components/editor';

<DocumentEditor
  document={document}
  corrections={corrections}
  onContentChange={handleChange}
/>
```

### Diff Viewer
```tsx
import { DiffViewer } from '@/components/diff';

<DiffViewer
  oldValue={original}
  newValue={modified}
  splitView={true}
/>
```

### Export
```typescript
import { exportToPdf } from '@/lib/export';

await exportToPdf(document, {
  format: 'pdf',
  includeMetadata: true,
});
```

## 🎨 Components

### Editor Components
- `DocumentEditor` - Main Monaco Editor integration
- `EditorToolbar` - Toolbar with actions
- `EditorStatusBar` - Status information
- `CorrectionMarker` - Correction indicators
- `CorrectionPanel` - Correction details
- `SearchReplace` - Search and replace UI

### Diff Components
- `DiffViewer` - Main diff viewer
- `SideBySideDiff` - Side-by-side comparison
- `UnifiedDiff` - Unified diff view
- `CorrectionAnnotation` - Correction annotations

## 🛠️ Technology Stack

- React 18.2+
- TypeScript 5.3+
- Monaco Editor 0.45+
- Zustand 4.4+
- Vite 5.0+

## 📂 Structure

```
src/
├── components/
│   ├── editor/     # Editor components
│   └── diff/       # Diff components
├── lib/
│   ├── editor/     # Editor utilities
│   ├── diff/       # Diff algorithms
│   └── export/     # Export utilities
├── hooks/          # State management
├── types/          # TypeScript definitions
└── examples/       # Usage examples
```

## ⌨️ Keyboard Shortcuts

- `Ctrl+S` - Save
- `Ctrl+F` - Find
- `Ctrl+H` - Replace
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Shift+Alt+F` - Format

## 🧪 Testing

```bash
npm test              # Run all tests
npm run test:watch    # Watch mode
npm run test:coverage # Coverage report
```

## 📦 Building

```bash
npm run build         # Production build
npm run preview       # Preview build
```

## 🎯 Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## 📄 License

MIT

## 🙏 Credits

Built with Monaco Editor, React, TypeScript, and many other open source libraries.
