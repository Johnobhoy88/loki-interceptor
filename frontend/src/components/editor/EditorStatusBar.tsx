import React, { useState, useEffect } from 'react';
import { editor } from 'monaco-editor';
import { EditorDocument, Correction } from '@/types/editor';

interface EditorStatusBarProps {
  document: EditorDocument;
  corrections: Correction[];
  editor: editor.IStandaloneCodeEditor | null;
}

export const EditorStatusBar: React.FC<EditorStatusBarProps> = ({
  document,
  corrections,
  editor,
}) => {
  const [position, setPosition] = useState({ line: 1, column: 1 });
  const [selection, setSelection] = useState({ chars: 0, lines: 0 });

  useEffect(() => {
    if (!editor) return;

    const updatePosition = () => {
      const pos = editor.getPosition();
      if (pos) {
        setPosition({ line: pos.lineNumber, column: pos.column });
      }
    };

    const updateSelection = () => {
      const selections = editor.getSelections();
      if (selections && selections.length > 0) {
        const model = editor.getModel();
        if (model) {
          const selection = selections[0];
          const text = model.getValueInRange(selection);
          const lines = text.split('\n').length;
          setSelection({ chars: text.length, lines });
        }
      } else {
        setSelection({ chars: 0, lines: 0 });
      }
    };

    const disposables = [
      editor.onDidChangeCursorPosition(updatePosition),
      editor.onDidChangeCursorSelection(updateSelection),
    ];

    updatePosition();

    return () => {
      disposables.forEach((d) => d.dispose());
    };
  }, [editor]);

  const pendingCorrections = corrections.filter((c) => c.status === 'pending');
  const acceptedCorrections = corrections.filter((c) => c.status === 'accepted');

  return (
    <div className="editor-status-bar">
      <div className="status-section">
        <span>Ln {position.line}, Col {position.column}</span>
        {selection.chars > 0 && (
          <span>({selection.chars} chars, {selection.lines} lines selected)</span>
        )}
      </div>
      <div className="status-section">
        <span>{document.language.toUpperCase()}</span>
      </div>
      <div className="status-section corrections-status">
        <span className="pending">{pendingCorrections.length} pending</span>
        <span className="accepted">{acceptedCorrections.length} accepted</span>
      </div>
      <div className="status-section">
        <span>Version {document.version}</span>
      </div>
    </div>
  );
};
