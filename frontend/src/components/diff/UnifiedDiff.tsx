import React from 'react';
import { DiffChange } from '@/types/editor';
import Prism from 'prismjs';
import 'prismjs/themes/prism.css';

interface UnifiedDiffProps {
  changes: DiffChange[];
  language?: string;
  showLineNumbers?: boolean;
}

export const UnifiedDiff: React.FC<UnifiedDiffProps> = ({
  changes,
  language = 'text',
  showLineNumbers = true,
}) => {
  const highlightCode = (code: string, lang: string): string => {
    try {
      const grammar = Prism.languages[lang] || Prism.languages.text;
      return Prism.highlight(code, grammar, lang);
    } catch {
      return code;
    }
  };

  return (
    <div className="unified-diff">
      <div className="diff-content">
        {changes.map((change, index) => (
          <div key={index} className={`unified-line ${change.type}`}>
            {showLineNumbers && (
              <div className="line-numbers">
                <span className="old-line-number">
                  {change.oldText ? change.lineNumber : ''}
                </span>
                <span className="new-line-number">
                  {change.newText ? change.lineNumber : ''}
                </span>
              </div>
            )}
            <div className="line-marker">
              {change.type === 'insert' && '+'}
              {change.type === 'delete' && '-'}
              {change.type === 'modify' && '~'}
            </div>
            <div className="line-content">
              {change.type === 'delete' && change.oldText && (
                <pre
                  dangerouslySetInnerHTML={{
                    __html: highlightCode(change.oldText, language),
                  }}
                />
              )}
              {change.type === 'insert' && change.newText && (
                <pre
                  dangerouslySetInnerHTML={{
                    __html: highlightCode(change.newText, language),
                  }}
                />
              )}
              {change.type === 'modify' && (
                <>
                  {change.oldText && (
                    <pre
                      className="old-text"
                      dangerouslySetInnerHTML={{
                        __html: highlightCode(change.oldText, language),
                      }}
                    />
                  )}
                  {change.newText && (
                    <pre
                      className="new-text"
                      dangerouslySetInnerHTML={{
                        __html: highlightCode(change.newText, language),
                      }}
                    />
                  )}
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UnifiedDiff;
