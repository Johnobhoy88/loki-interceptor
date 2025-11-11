import React, { useMemo } from 'react';
import ReactDiffViewer, { DiffMethod } from 'react-diff-viewer-continued';
import { DiffChange } from '@/types/editor';
import { computeLineInformation } from '@/lib/diff/diffAlgorithm';

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

export const DiffViewer: React.FC<DiffViewerProps> = ({
  oldValue,
  newValue,
  oldTitle = 'Original',
  newTitle = 'Modified',
  splitView = true,
  showDiffOnly = false,
  highlightLines = [],
  onLineClick,
}) => {
  const diffChanges = useMemo(
    () => computeLineInformation(oldValue, newValue),
    [oldValue, newValue]
  );

  const customStyles = {
    variables: {
      light: {
        diffViewerBackground: '#ffffff',
        diffViewerColor: '#212529',
        addedBackground: '#e6ffed',
        addedColor: '#24292e',
        removedBackground: '#ffeef0',
        removedColor: '#24292e',
        wordAddedBackground: '#acf2bd',
        wordRemovedBackground: '#fdb8c0',
        addedGutterBackground: '#cdffd8',
        removedGutterBackground: '#ffdce0',
        gutterBackground: '#f7f7f7',
        gutterBackgroundDark: '#f3f3f3',
        highlightBackground: '#fffbdd',
        highlightGutterBackground: '#fff5b1',
      },
      dark: {
        diffViewerBackground: '#1e1e1e',
        diffViewerColor: '#d4d4d4',
        addedBackground: '#044B53',
        addedColor: '#d4d4d4',
        removedBackground: '#632F34',
        removedColor: '#d4d4d4',
        wordAddedBackground: '#055d67',
        wordRemovedBackground: '#7d383f',
        addedGutterBackground: '#034148',
        removedGutterBackground: '#632b30',
        gutterBackground: '#2b2b2b',
        gutterBackgroundDark: '#262626',
        highlightBackground: '#4b4b19',
        highlightGutterBackground: '#5a5a1f',
      },
    },
  };

  return (
    <div className="diff-viewer-container">
      <div className="diff-header">
        <div className="diff-title">
          <span className="old-title">{oldTitle}</span>
          <span className="separator">↔</span>
          <span className="new-title">{newTitle}</span>
        </div>
        <div className="diff-stats">
          <span className="additions">
            +{diffChanges.filter((c) => c.type === 'insert').length}
          </span>
          <span className="deletions">
            -{diffChanges.filter((c) => c.type === 'delete').length}
          </span>
        </div>
      </div>
      <ReactDiffViewer
        oldValue={oldValue}
        newValue={newValue}
        splitView={splitView}
        showDiffOnly={showDiffOnly}
        compareMethod={DiffMethod.WORDS}
        styles={customStyles}
        useDarkTheme={false}
        leftTitle={oldTitle}
        rightTitle={newTitle}
        onLineNumberClick={onLineClick}
        highlightLines={highlightLines}
      />
    </div>
  );
};

export default DiffViewer;
