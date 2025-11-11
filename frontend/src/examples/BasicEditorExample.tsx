import React, { useState } from 'react';
import { DocumentEditor } from '@/components/editor/DocumentEditor';
import { EditorDocument, Correction } from '@/types/editor';

export const BasicEditorExample: React.FC = () => {
  const [document] = useState<EditorDocument>({
    id: '1',
    title: 'Sample Document',
    content: 'Hello World!\nThis is a sample document with some text.',
    language: 'markdown',
    version: 1,
    createdAt: new Date(),
    updatedAt: new Date(),
  });

  const [corrections] = useState<Correction[]>([
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
  ]);

  const handleContentChange = (content: string) => {
    console.log('Content changed:', content);
  };

  const handleCorrectionClick = (correction: Correction) => {
    console.log('Correction clicked:', correction);
  };

  return (
    <div style={{ height: '100vh' }}>
      <DocumentEditor
        document={document}
        corrections={corrections}
        onContentChange={handleContentChange}
        onCorrectionClick={handleCorrectionClick}
      />
    </div>
  );
};
