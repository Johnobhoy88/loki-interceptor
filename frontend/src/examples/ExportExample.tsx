import React, { useState } from 'react';
import { EditorDocument, ExportOptions } from '@/types/editor';
import {
  exportToDocx,
  exportToPdf,
  exportToHtml,
  exportToTxt,
  exportToMarkdown,
} from '@/lib/export/exportUtils';

export const ExportExample: React.FC = () => {
  const [document] = useState<EditorDocument>({
    id: '1',
    title: 'Sample Export Document',
    content: `# Sample Document

This is a sample document that will be exported to various formats.

## Features
- Export to DOCX
- Export to PDF
- Export to HTML
- Export to TXT
- Export to Markdown`,
    language: 'markdown',
    version: 1,
    createdAt: new Date(),
    updatedAt: new Date(),
    metadata: {
      author: 'John Doe',
      tags: ['sample', 'export'],
      description: 'A sample document for export testing',
    },
  });

  const exportOptions: ExportOptions = {
    format: 'pdf',
    includeMetadata: true,
    includeCorrections: false,
    highlightCorrections: false,
  };

  const handleExport = async (format: string) => {
    try {
      switch (format) {
        case 'docx':
          await exportToDocx(document, { ...exportOptions, format: 'docx' });
          break;
        case 'pdf':
          await exportToPdf(document, { ...exportOptions, format: 'pdf' });
          break;
        case 'html':
          await exportToHtml(document, { ...exportOptions, format: 'html' });
          break;
        case 'txt':
          await exportToTxt(document, { ...exportOptions, format: 'txt' });
          break;
        case 'markdown':
          await exportToMarkdown(document, { ...exportOptions, format: 'markdown' });
          break;
      }
      alert(`Exported to ${format.toUpperCase()} successfully!`);
    } catch (error) {
      alert(`Export failed: ${error}`);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Export Document Example</h2>
      <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
        <button onClick={() => handleExport('docx')}>Export to DOCX</button>
        <button onClick={() => handleExport('pdf')}>Export to PDF</button>
        <button onClick={() => handleExport('html')}>Export to HTML</button>
        <button onClick={() => handleExport('txt')}>Export to TXT</button>
        <button onClick={() => handleExport('markdown')}>Export to Markdown</button>
      </div>
    </div>
  );
};
