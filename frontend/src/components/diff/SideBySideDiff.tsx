import React, { useState } from 'react';
import { DiffChange, Correction } from '@/types/editor';
import { CorrectionAnnotation } from './CorrectionAnnotation';

interface SideBySideDiffProps {
  changes: DiffChange[];
  corrections?: Correction[];
  onAcceptChange?: (change: DiffChange) => void;
  onRejectChange?: (change: DiffChange) => void;
}

export const SideBySideDiff: React.FC<SideBySideDiffProps> = ({
  changes,
  corrections = [],
  onAcceptChange,
  onRejectChange,
}) => {
  const [selectedLine, setSelectedLine] = useState<number | null>(null);

  const getLineCorrections = (lineNumber: number): Correction[] => {
    return corrections.filter(
      (c) => c.range.startLine === lineNumber
    );
  };

  const renderLine = (change: DiffChange) => {
    const lineCorrections = getLineCorrections(change.lineNumber);
    const isSelected = selectedLine === change.lineNumber;

    return (
      <div
        key={change.lineNumber}
        className={`diff-line ${change.type} ${isSelected ? 'selected' : ''}`}
        onClick={() => setSelectedLine(change.lineNumber)}
      >
        <div className="line-number">{change.lineNumber}</div>
        <div className="line-content">
          <div className="old-content">
            {change.oldText && (
              <code className="line-text">{change.oldText}</code>
            )}
          </div>
          <div className="new-content">
            {change.newText && (
              <code className="line-text">{change.newText}</code>
            )}
          </div>
        </div>
        <div className="line-actions">
          {change.type !== 'modify' && onAcceptChange && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onAcceptChange(change);
              }}
              className="btn-accept-change"
              title="Accept change"
            >
              ✓
            </button>
          )}
          {change.type !== 'modify' && onRejectChange && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRejectChange(change);
              }}
              className="btn-reject-change"
              title="Reject change"
            >
              ✕
            </button>
          )}
        </div>
        {lineCorrections.length > 0 && (
          <CorrectionAnnotation corrections={lineCorrections} />
        )}
      </div>
    );
  };

  return (
    <div className="side-by-side-diff">
      <div className="diff-header">
        <div className="column-header old">Original</div>
        <div className="column-header new">Modified</div>
        <div className="column-header actions">Actions</div>
      </div>
      <div className="diff-body">
        {changes.map((change) => renderLine(change))}
      </div>
    </div>
  );
};

export default SideBySideDiff;
