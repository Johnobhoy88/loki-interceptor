import React, { useState, useCallback } from 'react';
import { editor } from 'monaco-editor';
import { SearchOptions } from '@/types/editor';

interface SearchReplaceProps {
  editor: editor.IStandaloneCodeEditor | null;
  onClose: () => void;
}

export const SearchReplace: React.FC<SearchReplaceProps> = ({
  editor,
  onClose,
}) => {
  const [searchText, setSearchText] = useState('');
  const [replaceText, setReplaceText] = useState('');
  const [options, setOptions] = useState<SearchOptions>({
    query: '',
    caseSensitive: false,
    wholeWord: false,
    regex: false,
  });
  const [matches, setMatches] = useState(0);
  const [currentMatch, setCurrentMatch] = useState(0);

  const handleSearch = useCallback(() => {
    if (!editor || !searchText) return;

    const model = editor.getModel();
    if (!model) return;

    const matches = model.findMatches(
      searchText,
      true,
      options.regex,
      options.caseSensitive,
      options.wholeWord ? '\b' : null,
      true
    );

    setMatches(matches.length);
    if (matches.length > 0) {
      editor.setSelection(matches[0].range);
      editor.revealRangeInCenter(matches[0].range);
      setCurrentMatch(1);
    }
  }, [editor, searchText, options]);

  const handleNext = useCallback(() => {
    if (!editor) return;
    editor.trigger('search', 'editor.action.nextMatchFindAction', null);
  }, [editor]);

  const handlePrevious = useCallback(() => {
    if (!editor) return;
    editor.trigger('search', 'editor.action.previousMatchFindAction', null);
  }, [editor]);

  const handleReplace = useCallback(() => {
    if (!editor || !searchText) return;

    const selection = editor.getSelection();
    if (selection) {
      editor.executeEdits('search-replace', [
        {
          range: selection,
          text: replaceText,
        },
      ]);
      handleNext();
    }
  }, [editor, searchText, replaceText, handleNext]);

  const handleReplaceAll = useCallback(() => {
    if (!editor || !searchText) return;

    const model = editor.getModel();
    if (!model) return;

    const matches = model.findMatches(
      searchText,
      true,
      options.regex,
      options.caseSensitive,
      options.wholeWord ? '\b' : null,
      true
    );

    editor.executeEdits(
      'search-replace-all',
      matches.map((match) => ({
        range: match.range,
        text: replaceText,
      }))
    );

    setMatches(0);
    setCurrentMatch(0);
  }, [editor, searchText, replaceText, options]);

  return (
    <div className="search-replace-panel">
      <div className="panel-header">
        <h3>Find and Replace</h3>
        <button onClick={onClose} aria-label="Close">
          ✕
        </button>
      </div>

      <div className="search-inputs">
        <div className="input-group">
          <input
            type="text"
            placeholder="Find"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            aria-label="Search text"
          />
          <div className="search-options">
            <button
              className={options.caseSensitive ? 'active' : ''}
              onClick={() =>
                setOptions({ ...options, caseSensitive: !options.caseSensitive })
              }
              title="Match Case"
              aria-label="Match case"
            >
              Aa
            </button>
            <button
              className={options.wholeWord ? 'active' : ''}
              onClick={() =>
                setOptions({ ...options, wholeWord: !options.wholeWord })
              }
              title="Match Whole Word"
              aria-label="Match whole word"
            >
              [W]
            </button>
            <button
              className={options.regex ? 'active' : ''}
              onClick={() => setOptions({ ...options, regex: !options.regex })}
              title="Use Regular Expression"
              aria-label="Use regular expression"
            >
              .*
            </button>
          </div>
        </div>

        <div className="input-group">
          <input
            type="text"
            placeholder="Replace"
            value={replaceText}
            onChange={(e) => setReplaceText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleReplace()}
            aria-label="Replace text"
          />
        </div>
      </div>

      <div className="search-actions">
        <div className="match-counter">
          {matches > 0 && (
            <span>
              {currentMatch} of {matches}
            </span>
          )}
        </div>
        <div className="action-buttons">
          <button onClick={handlePrevious} title="Previous Match">
            ↑
          </button>
          <button onClick={handleNext} title="Next Match">
            ↓
          </button>
          <button onClick={handleReplace}>Replace</button>
          <button onClick={handleReplaceAll}>Replace All</button>
        </div>
      </div>
    </div>
  );
};
