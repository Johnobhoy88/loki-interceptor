import React, { useState } from 'react';
import { DiffViewer } from '@/components/diff/DiffViewer';
import { SideBySideDiff } from '@/components/diff/SideBySideDiff';
import { DiffChange } from '@/types/editor';

export const DiffViewerExample: React.FC = () => {
  const oldText = `Hello World!
This is the original text.
It has multiple lines.`;

  const newText = `Hi World!
This is the modified text.
It has multiple lines.
And a new line!`;

  const [viewMode, setViewMode] = useState<'unified' | 'split'>('split');

  const changes: DiffChange[] = [
    {
      type: 'modify',
      lineNumber: 1,
      oldText: 'Hello World!',
      newText: 'Hi World!',
    },
    {
      type: 'modify',
      lineNumber: 2,
      oldText: 'This is the original text.',
      newText: 'This is the modified text.',
    },
    {
      type: 'insert',
      lineNumber: 4,
      newText: 'And a new line!',
    },
  ];

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '20px' }}>
        <button onClick={() => setViewMode('split')}>Split View</button>
        <button onClick={() => setViewMode('unified')}>Unified View</button>
      </div>

      {viewMode === 'split' ? (
        <DiffViewer
          oldValue={oldText}
          newValue={newText}
          splitView={true}
          oldTitle="Original"
          newTitle="Modified"
        />
      ) : (
        <SideBySideDiff changes={changes} />
      )}
    </div>
  );
};
